from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request,username=None, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            if email:
                user = UserModel.objects.get(email=email)
            if username:
                user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
