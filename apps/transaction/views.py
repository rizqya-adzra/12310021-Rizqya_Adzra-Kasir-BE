from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .models import Member, Transaction
from .serializers import MemberSerializer, TransactionSerializer
from utils.response import response_success, response_error
from utils.pagination import CustomPagination
from utils.permissions import IsCashierRole, IsCashierOrReadOnly
from apps.transaction.filters import TransactionFilter

def format_rupiah(value):
    if value is None:
        return "Rp 0"
    return f"Rp {int(value):,}".replace(",", ".")

def generate_receipt_pdf_response(transaction, request, filename=None):
    if not filename:
        filename = f"Struk_{transaction.invoice}.pdf"
        
    template_path = 'receipt_detail.html'
    
    formatted_details = []
    for detail in transaction.details.all():
        formatted_details.append({
            'product_name': detail.product.name,
            'quantity': detail.quantity,
            'price': format_rupiah(detail.price),
            'subtotal': format_rupiah(detail.subtotal)
        })

    context = {
        'invoice': transaction.invoice,
        'created_at': transaction.created_at,
        'username': transaction.user.username if transaction.user else 'Sistem',
        'customer_name': transaction.customer_name or 'Umum',
        'is_member': transaction.is_member,
        'details': formatted_details,
        'total_quantity': transaction.total_quantity,
        'subtotal': format_rupiah(transaction.subtotal),
        'is_point': transaction.is_point,
        'point': format_rupiah(transaction.point),
        'total': format_rupiah(transaction.total),
        'payment_amount': format_rupiah(transaction.payment_amount),
        'change_amount': format_rupiah(transaction.change_amount),
    }
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Terjadi kesalahan saat generate PDF Struk', status=500)
        
    return response


class MemberListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCashierRole]
    queryset = Member.objects.all().order_by('-created_at')
    serializer_class = MemberSerializer
    pagination_class = CustomPagination
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'telephone']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return response_success(
                message="Berhasil mengambil data member",
                data=serializer.data,
                current_page=self.paginator.page.number,
                total_pages=self.paginator.page.paginator.num_pages
            )

        serializer = self.get_serializer(queryset, many=True)
        return response_success(message="Berhasil mengambil data member", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response_success(message="Member berhasil didaftarkan", data=serializer.data)
            
        return response_error(message="Gagal mendaftar member", errors=serializer.errors)


class TransactionListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsCashierOrReadOnly]
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['invoice', 'customer_name', 'telephone']
    ordering_fields = ['customer_name', 'payment_amount', 'total_quantity']


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return response_success(
                message="Berhasil mengambil data transaksi",
                data=serializer.data,
                current_page=self.paginator.page.number,
                total_pages=self.paginator.page.paginator.num_pages
            )

        serializer = self.get_serializer(queryset, many=True)
        return response_success(message="Berhasil mengambil data transaksi", data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Transaksi berhasil diproses", 
                data=serializer.data
            )
            
        return response_error(
            message="Gagal memproses transaksi, periksa keranjang belanja Anda.", 
            errors=serializer.errors
        )


class TransactionDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsCashierOrReadOnly]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        export = request.query_params.get('export')
        if export == 'pdf':
            return generate_receipt_pdf_response(instance, request)
        
        serializer = self.get_serializer(instance)
        return response_success(
            message="Berhasil mengambil detail transaksi",
            data=serializer.data
        )