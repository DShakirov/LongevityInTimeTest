import pyotp
from rest_framework import serializers
from .models import CustomUser
from .tasks import send_otp
from django.core.exceptions import ObjectDoesNotExist


class RegistrationSerializer(serializers.ModelSerializer):

    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'about_me',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
# generating OTP and saving User
        totp = pyotp.TOTP('base32secret3232', interval=300)
        otp = totp.now()
        user = CustomUser(
                email=self.validated_data['email'],
                otp=otp,
                first_name=self.validated_data['first_name'] if self.validated_data['first_name'] else '',
                last_name=self.validated_data['last_name'] if self.validated_data['last_name'] else '',
                about_me=self.validated_data['about_me'] if self.validated_data['about_me'] else ''
                          )
        email = self.validated_data['email']
        send_otp(email, otp) #send generated OTP to login
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"}, required=True)
    new_password = serializers.CharField(style={"input_type": "password"}, required=True)

    def validate_current_password(self, value):
        if NotImplementedError:
            raise serializers.ValidationError({'authorisation': 'User is not logged in'})
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError({'current_password': 'Does not match'})
        return value


class FetchSerializer(serializers.Serializer):
    email = serializers.CharField()
    def get_user_data(self):
        try:
            user = CustomUser.objects.get(email=self.validated_data['email'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'email':'No user with such email'})
        if user: 
            return{
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'about_me': user.about_me
            }
        
