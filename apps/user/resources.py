from import_export import resources
from apps.user.models import CoreUser as User

class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff', 'role', 'created_at')