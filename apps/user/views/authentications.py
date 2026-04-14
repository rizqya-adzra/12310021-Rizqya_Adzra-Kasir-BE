from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.exceptions import ObjectDoesNotExist
from utils.response import response_success, response_error 

from apps.user.serializers import LoginSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data 
            token, _ = Token.objects.get_or_create(user=user)
            return response_success(
                message="Login berhasil",
                data={
                    "id": user.id,
                    "email": user.email,
                    "token": token.key,
                    "is_staff": user.is_staff
                }
            )
        return response_error(
            message="Login gagal",
            errors=serializer.errors
        )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = None 

    def post(self, request):
        try:
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            
            return response_success(
                message="Logout berhasil"
            )

        except (AttributeError, ObjectDoesNotExist):
            return response_error(
                message="Gagal logout. Token tidak ditemukan atau sudah kadaluarsa.",
                errors={"token": "Token invalid"}
            )
        
        except Exception as e:
            return response_error(
                message="Terjadi kesalahan sistem.",
                errors=str(e), 
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )