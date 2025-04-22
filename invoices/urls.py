from django.urls import path, include
from rest_framework.routers import DefaultRouter

from invoices.views import InvoiceViewSet, TransactionViewSet

# from .views import TodoViewSet, TodoListView, TodoCreateView

router = DefaultRouter()
router.register(r'todos', InvoiceViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
