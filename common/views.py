from django.shortcuts import render
from rest_framework import exceptions, serializers
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import app

from core.models import User
from .authentication import JWTAuthentication
from .serializers import UserSerializer


# registers a new user
class RegisterAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match')

        data['is_ambassador'] = 'api/ambassador' in request.path

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# verifies user email and password and sets jwt
class LoginAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect password')

        scope = 'ambassador' if 'api/ambassador' in request.path else 'admin'

        if user.is_ambassador and scope == 'admin':
            raise exceptions.AuthenticationFailed('Unauthorized')

        token = JWTAuthentication.generate_jwt(user.id, scope)

        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'message': 'success'
        }

        return response


# gets authenticated user
class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = UserSerializer(user).data
        print('User: ', data)

        if 'api/ambassador' in request.path:
            data['revenue'] = user.revenue

        return Response(data)


# logout the current user
class LogoutAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, _):
        response = Response()
        response.delete_cookie(key='jwt')
        response.data = {
            'message': 'success'
        }

        return response


class ProfileInfoAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProfilePasswordAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, pk=None):
        data = request.data
        user = request.user

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords do not match')

        user.set_password(data['password'])
        user.save()
        return Response(UserSerializer(user).data)
