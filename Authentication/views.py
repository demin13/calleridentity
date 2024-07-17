from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .serializers import UserRegistrationSerializer, UserLoginSerializer
from Authentication.utility.handler import Validator, handle_exceptions

User = get_user_model()

class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    
    @staticmethod
    @handle_exceptions
    def post(request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={"message": "User registration success."}, status=status.HTTP_201_CREATED)
        return Response(data={"error": Validator.TrimSerializerError(serializer.errors)}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    @handle_exceptions
    def post(request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                phone=serializer.validated_data['phone'],
                password=serializer.validated_data['password']
            )
            if user is not None:
                refresh = RefreshToken.for_user(user)
                response = {
                    'name': user.name,
                    'phone': user.phone,
                    'email': user.email,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(data=response, status=status.HTTP_200_OK)
            return Response(data={'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(data={"error": Validator.TrimSerializerError(serializer.errors)}, 
                        status=status.HTTP_400_BAD_REQUEST)