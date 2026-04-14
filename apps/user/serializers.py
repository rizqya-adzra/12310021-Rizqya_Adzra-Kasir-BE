from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CoreUser

from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages={
            'required': 'Email wajib diisi.',
            'blank': 'Email wajib diisi.',
            'invalid': 'Format email tidak valid.'
        }
    )
    password = serializers.CharField(
        write_only=True, 
        error_messages={
            'required': 'Password wajib diisi.',
            'blank': 'Password wajib diisi.'
        }
    )

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password) 
            if not user:
                raise serializers.ValidationError({"detail": "Email atau password salah."})
            
            if not user.is_active:
                raise serializers.ValidationError({"detail": "Akun ini tidak aktif."})
        else:
            raise serializers.ValidationError({"detail": "Email dan password wajib diisi."})

        return user


class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreUser
        fields = ['username', 'email', 'image', 'is_staff', 'created_at', 'role']
        read_only_fields = ['email', 'is_staff', 'role', 'created_at']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)
        
        instance = super().update(instance, validated_data)
        
        if profile_data and hasattr(instance, 'profile'):
            profile_obj = instance.profile
            for attr, value in profile_data.items():
                setattr(profile_obj, attr, value)
            profile_obj.save()
            
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    class Meta:
        model = CoreUser
        fields = ['username', 'email', 'password', 'role', 'image']

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username') or email 

        user = CoreUser.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            role=validated_data.get('role', 'cashier'),
            image=validated_data.get('image')
        )
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=6)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Password lama salah.")
        return value