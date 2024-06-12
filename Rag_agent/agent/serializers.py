from rest_framework import serializers
from .models import User, UploadedUrl
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

class UserRegisterSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only = True)
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only = True)
    password2 = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name","last_name","email","password1","password2"]
        extra_kwargs = {
            'password':{'write_only':True}
        }

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            detail = {
                'detail': "User Already exists!"
            }
            raise ValidationError(detail=detail)
        return username

    def validate(self, instance):
        if instance['password1'] != instance['password2']:
            raise ValidationError({"message":"Both password must match"})
        
        if User.objects.filter(email=instance['email']).exists():
            raise ValidationError({"message":"Email already taken"})
        
        return instance
    
    def create(self, validated_data):
        password1 = validated_data.pop('password')
        password2 = validated_data.pop('password2')

        user = User.objects.create(**validated_data)
        user.set_password(password1)
        user.save()
        Token.objects.create(user=user)
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id","username","password"]

 