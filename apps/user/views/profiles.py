from django.http import HttpResponse

from rest_framework import generics, filters
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.openapi import AutoSchema
from django_filters.rest_framework import DjangoFilterBackend
from utils.export import BaseExportExcelView

from apps.user.serializers import MeSerializer, ChangePasswordSerializer, UserCreateSerializer
from apps.user.models import CoreUser as User
from utils.response import response_success, response_error 
from utils.permissions import IsAdminRole
from utils.pagination import CustomPagination
from apps.user.resources import UserResource


class UserExportExcelView(BaseExportExcelView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all().order_by('-created_at')
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'created_at', 'email']
    search_fields = ['email', 'username']
    
    resource_class = UserResource
    filename = "Data_Pengguna.xlsx"
    

class MyProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = MeSerializer 
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response_success(
            message="Berhasil mengambil data profil",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True 
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Profil berhasil diperbarui",
                data=serializer.data
            )
        return response_error(
            message="Gagal memperbarui profil, mohon periksa input Anda.",
            errors=serializer.errors
        )
        
        
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = self.get_object()
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            try:
                request.user.auth_token.delete()
            except (AttributeError, Exception):
                pass

            return response_success(
                message="Password berhasil diperbarui. Silakan login kembali."
            )
        
        return response_error(message="Gagal ganti password", errors=serializer.errors)
    

class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole] 
    schema = AutoSchema()
    
    pagination_class = CustomPagination
    queryset = User.objects.all().order_by('-created_at')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'created_at', 'email']
    search_fields = ['email', 'username'] 

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return MeSerializer 
    

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        if request.query_params.get('export') == 'excel':
            resource = UserResource()
            dataset = resource.export(queryset)
            response = HttpResponse(
                dataset.xlsx, 
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="Data_Pengguna.xlsx"'
            return response
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            total_pages = self.paginator.page.paginator.num_pages
            current_page = self.paginator.page.number
            
            return response_success(
                message="Berhasil mengambil data semua pengguna",
                data=serializer.data,
                current_page=current_page,
                total_pages=total_pages
            )

        serializer = self.get_serializer(queryset, many=True)
        return response_success(
            message="Berhasil mengambil data semua pengguna",
            data=serializer.data
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Berhasil membuat pengguna baru",
                data=serializer.data
            )
            
        return response_error(
            message="Gagal membuat pengguna baru, periksa input Anda.", 
            errors=serializer.errors
        )
        
        
class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer 
    lookup_field = 'email'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserCreateSerializer
        return MeSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return response_success(
            message="Berhasil mengambil detail pengguna",
            data=serializer.data
        )

    def update(self, request, *args, **kwargs):
        partial = True 
        kwargs['partial'] = True 
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return response_success(
                message="Berhasil memperbarui data pengguna",
                data=serializer.data
            )
        
        return response_error(
            message="Gagal memperbarui pengguna, periksa input Anda.",
            errors=serializer.errors
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return response_success(
            message="Berhasil menghapus pengguna",
            data=None
        ) 