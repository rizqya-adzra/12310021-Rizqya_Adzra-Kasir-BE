import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['is_member', 'user']