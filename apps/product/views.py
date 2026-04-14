from django.http import HttpResponse

from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from utils.export import BaseExportExcelView

from apps.product.models import Category, Product
from apps.product.serializers import CategorySerializer, ProductSerializer, AddStockSerializer
from utils.response import response_success, response_error
from utils.permissions import IsAdminRole, IsAdminOrReadOnly
from apps.product.filters import ProductFilter
from utils.pagination import CustomPagination
from apps.product.resources import CategoryResource, ProductResource


class ProductExportExcelView(BaseExportExcelView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Product.objects.all().order_by('-created_at')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'price', 'category']
    search_fields = ['name']
    
    resource_class = ProductResource
    filename = "Data_Product.xlsx"

class CategoryExportExcelView(BaseExportExcelView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Category.objects.all().order_by('-created_at')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name', 'description']
    search_fields = ['name']
    
    resource_class = CategoryResource
    filename = "Data_Category.xlsx"
    

class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Category.objects.all().order_by('-created_at')
    serializer_class = CategorySerializer
    
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if request.query_params.get('export') == 'excel':
            resource = CategoryResource()
            dataset = resource.export(queryset)
            response = HttpResponse(
                dataset.xlsx, 
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="Data_Category.xlsx"'
            return response
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return response_success(
                message="Berhasil mengambil data semua kategori",
                data=serializer.data,
                current_page=self.paginator.page.number,
                total_pages=self.paginator.page.paginator.num_pages
            )

        serializer = self.get_serializer(queryset, many=True)
        return response_success(
            message="Berhasil mengambil data semua kategori",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Berhasil membuat kategori baru",
                data=serializer.data
            )
            
        return response_error(
            message="Gagal membuat kategori, periksa input Anda.",
            errors=serializer.errors
        )


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response_success(
            message="Berhasil mengambil detail kategori",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Berhasil memperbarui data kategori",
                data=serializer.data
            )
        
        return response_error(
            message="Gagal memperbarui kategori, periksa input Anda.",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return response_success(
            message="Berhasil menghapus kategori",
            data=None
        )


class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku']
    
    ordering_fields = '__all__'
    ordering = ['-created_at']


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.query_params.get('export') == 'excel':
            resource = ProductResource()
            dataset = resource.export(queryset)
            response = HttpResponse(
                dataset.xlsx, 
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="Data_Product.xlsx"'
            return response
        
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return response_success(
                message="Berhasil mengambil data semua produk",
                data=serializer.data,
                current_page=self.paginator.page.number,
                total_pages=self.paginator.page.paginator.num_pages
            )

        serializer = self.get_serializer(queryset, many=True)
        return response_success(
            message="Berhasil mengambil data semua produk",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return response_success(
                message="Berhasil membuat produk baru",
                data=serializer.data
            )
            
        return response_error(
            message="Gagal membuat produk, periksa input Anda.",
            errors=serializer.errors
        )
    
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.all()
        
        if not user.is_authenticated or user.role != 'admin':
            return queryset.filter(visibility='active')
            
        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response_success(
            message="Berhasil mengambil detail produk",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Berhasil memperbarui data produk",
                data=serializer.data
            )
        
        return response_error(
            message="Gagal memperbarui produk, periksa input Anda.",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return response_success(
            message="Berhasil menghapus produk",
            data=None
        )
        
class ProductAddStockView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = Product.objects.all() 
    serializer_class = AddStockSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            
            instance.stock += amount
            instance.save()
            
            return response_success(
                message=f"Berhasil menambah stok sebanyak {amount}.",
                data={
                    "id": instance.id,
                    "name": instance.name,
                    "current_stock": instance.stock
                }
            )
            
        return response_error(
            message="Gagal menambah stok, periksa input Anda.",
            errors=serializer.errors
        )