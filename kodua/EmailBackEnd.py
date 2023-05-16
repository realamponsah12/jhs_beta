from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackEnd(ModelBackend):
    def authenticate(self,username=None, password=None, **kwargs):
        UserModel=get_user_model()
        print(username, password)
        try:
           
            user=UserModel.objects.get(username=username)
            print(user)
        except UserModel.DoesNotExist:
            print('error getting su')
            return None
        
        if user.check_password(password):
            print('pass checked')
            return user
        return None