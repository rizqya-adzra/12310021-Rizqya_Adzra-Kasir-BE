from django.urls import path
from apps.transaction.views import  MemberListCreateView, TransactionListCreateView, TransactionDetailView

urlpatterns = [
    path('transactions/members/', MemberListCreateView.as_view(), name='login'),
    path('transactions/', TransactionListCreateView.as_view(), name='category-detail'),
    path('transactions/<uuid:pk>/', TransactionDetailView.as_view(), name='product-list-create'),
]