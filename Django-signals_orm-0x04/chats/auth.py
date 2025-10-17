from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that can be used to customize JWT behavior
    """
    def authenticate(self, request):
        try:
            return super().authenticate(request)
        except Exception as e:
            return None

def get_user_from_token(token):
    """
    Helper function to get user from JWT token
    """
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        return user
    except Exception as e:
        return None