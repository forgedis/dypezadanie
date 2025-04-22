from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from rest_framework.viewsets import ModelViewSet

from invoices.models import Invoice, Transaction
from invoices.serializer import InvoiceSerializer, TransactionSerializer


# from invoices.serializer import TodoSerializer


class InvoiceViewSet(ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

class TransactionViewSet(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


# class InvoiceListView(ListView):
#     model = Invoice
#     template_name = 'invoice/todo_list.html'
#     context_object_name = 'todos'
#     ordering = ['-created_at']
#
#
# class TodoCreateView(CreateView):
#     model = Todo
#     template_name = 'todo/todo_form.html'
#     fields = ['title', 'description', 'completed']
#     success_url = reverse_lazy('todo-list')  # 🔥 Ensure this name matches your URLs
