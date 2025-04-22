from datetime import datetime
from uuid import uuid4

import requests
from django.core.management.base import BaseCommand

from invoices.models import Invoice, Transaction

AUTH = ('dype-it-test', 'hodne_slozite_heslo_je_heslo1234')
SOURCE_URL = 'https://hook.eu1.make.com/hdva1jmjpej8arsq2ejek3k48qjk0ane'
TARGET_URL = 'https://hook.eu1.make.com/appfn3yat3otjpi55w3tlm4ycatobkt8'
MY_NOTE = "Zpracoval: Martin Bujňák"

class Command(BaseCommand):
    help = 'Fetch, transform, and send data to Abra Flexi'

    def parse_date(self, date_str):
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except (ValueError, TypeError):
            for fmt in ["%Y-%m-%d", "%d.%m.%Y"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except (ValueError, TypeError):
                    continue
            self.stdout.write(self.style.WARNING(f"Invalid date: {date_str}"))
            return None

    def get_vs_from_invoice(self, invoice):
        return invoice.get("vs") or invoice.get("invoice_id") or ""

    def get_vs_from_transaction(self, transaction):
        return transaction.get("vs") or transaction.get("invoice_id") or ""

    def handle(self, *args, **options):
        try:
            response = requests.get(SOURCE_URL, auth=AUTH)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to fetch data: {e}"))
            return

        invoices = data.get("invoices", [])
        transactions = data.get("transactions", [])

        invoice_count = 0
        for inv in invoices:
            vs = self.get_vs_from_invoice(inv)
            issue_date = self.parse_date(inv.get("date") or inv.get("issue_date"))
            due_date = self.parse_date(inv.get("due_date"))
            if not vs or not issue_date or not due_date:
                continue
            description = inv.get("description", "") or inv.get("note", "") or "Služby"
            Invoice.objects.update_or_create(
                vs=vs,
                defaults={
                    "issue_date": issue_date,
                    "due_date": due_date,
                    "amount": inv.get("amount", 0),
                    "note": f'{description}\n{MY_NOTE}'.strip(),
                    "description": description
                }
            )
            invoice_count += 1

        transaction_count = 0
        for tx in transactions:
            vs = self.get_vs_from_transaction(tx)
            tx_date = self.parse_date(tx.get("date"))
            if not vs or not tx_date:
                continue
            Transaction.objects.update_or_create(
                vs=vs,
                transaction_date=tx_date,
                amount=tx.get("amount", 0),
                defaults={"note": f'{tx.get("description", "") or tx.get("note", "")}\n{MY_NOTE}'.strip()}
            )
            transaction_count += 1

        matched_count = 0
        unmatched_count = 0
        for tx in Transaction.objects.filter(matched_invoice__isnull=True).exclude(vs=""):
            try:
                invoice = Invoice.objects.get(vs=tx.vs)
                tx.matched_invoice = invoice
                tx.save()
                matched_count += 1
            except Invoice.DoesNotExist:
                unmatched_count += 1

        faktury_json = []
        for inv in Invoice.objects.all():
            if not inv.issue_date or not inv.due_date:
                continue
            item_name = getattr(inv, 'description', None) or "Služby"
            kod = uuid4().hex[:20]  # zaručeně unikátní 20 znaků
            faktura_item = {
                "kod": kod,
                "typDokl": "code:FAKTURA",
                "varSym": inv.vs,
                "datVyst": inv.issue_date.strftime("%Y-%m-%d"),
                "datSplat": inv.due_date.strftime("%Y-%m-%d"),
                "sumCelkem": float(inv.amount),
                "poznam": inv.note or "",
                "polozkyFaktury": [
                    {
                        "nazev": item_name[:200],
                        "mnozMj": 1.0,
                        "cenaMj": float(inv.amount),
                        "sumCelkem": float(inv.amount),
                        "szbDph": 0.0
                    }
                ]
            }
            faktury_json.append(faktura_item)

        banka_json = []
        for tx in Transaction.objects.all():
            if not tx.transaction_date:
                continue
            banka_item = {
                "kod": f"TX-{uuid4().hex[:16]}",
                "banka": "code:BANKA-CZK",
                "typDokl": "code:STANDARD",
                "varSym": tx.vs,
                "datPohybu": tx.transaction_date.strftime("%Y-%m-%d"),
                "castka": float(tx.amount),
                "poznam": tx.note or "",
            }
            banka_json.append(banka_item)

        export_json = {
            "winstrom": {
                "@version": "1.0",
                "faktura-vydana": faktury_json,
                "banka": banka_json
            }
        }

        try:
            send_resp = requests.post(
                TARGET_URL,
                auth=AUTH,
                headers={"Content-Type": "application/json"},
                json=export_json
            )
            send_resp.raise_for_status()
            self.stdout.write(self.style.SUCCESS(f"✅ Data sent successfully. Status: {send_resp.status_code}"))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"❌ Sending failed: {e}"))
            if hasattr(e, 'response') and e.response is not None:
                self.stdout.write(f"  Status: {e.response.status_code}")
                self.stdout.write(f"  Response: {e.response.text[:1000]}")

        self.stdout.write("📊 Summary:")
        self.stdout.write(f"  Invoices processed: {invoice_count}")
        self.stdout.write(f"  Transactions processed: {transaction_count}")
        self.stdout.write(f"  Matched: {matched_count}, Unmatched: {unmatched_count}")
        self.stdout.write(f"  Exported invoices: {len(faktury_json)}")
        self.stdout.write(f"  Exported transactions: {len(banka_json)}")