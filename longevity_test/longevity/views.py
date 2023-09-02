import pyotp
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import  Response
from rest_framework.views import APIView

from .tasks import send_otp
from .utils import get_tokens_for_user
from .serializers import RegistrationSerializer, PasswordChangeSerializer, FetchSerializer
from .models import CustomUser



class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.POST['email']
        password = request.POST['password']
        otp = request.POST['otp'] if 'otp' in request.data else ''
        totp = pyotp.TOTP('base32secret3232', interval=300)
        user = authenticate(request, email=email, password=password)
        if user is not None:
# verifying OTP
            if otp == user.otp and totp.verify(otp):
                login(request, user)
                auth_data = get_tokens_for_user(request.user)
                return Response({'msg': 'Login Success', **auth_data}, status=status.HTTP_200_OK)
            else:
# if OTP is not valid generate new OTP and send it to email
                new_otp = totp.now()
                CustomUser.objects.filter(email=email).update(otp=new_otp)
                send_otp(email, new_otp)
                return Response({'msg': 'OTP has been send to your email'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'msg': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'msg': 'Successfully Logged out'}, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = PasswordChangeSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateProfileView(APIView):
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.POST['email']
        password = request.POST['password']
        if 'about_me' not in request.data:
            return Response({'msg': 'No data to update'}, status=status.HTTP_400_BAD_REQUEST)
        about_me = request.POST['about_me']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            CustomUser.objects.filter(email=email).update(about_me=about_me)
            return Response({'msg': 'User profile successfully updated'}, status=status.HTTP_200_OK)
        return Response({'msg': "User with such email or login not found"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteUserView(APIView):
    def post(self, request):
        if 'email' not in request.data or 'password' not in request.data:
            return Response({'msg': 'Credentials missing'}, status=status.HTTP_400_BAD_REQUEST)
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            CustomUser.objects.filter(email=email).delete()
            return Response({'msg': 'User profile successfully deleted'}, status=status.HTTP_200_OK)
        return Response({'msg': "User with such email or login not found"}, status=status.HTTP_400_BAD_REQUEST)


class FetchProfileView(APIView):
    def post(self, request):
        serializer = FetchSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.get_user_data(), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)