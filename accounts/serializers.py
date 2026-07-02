"""
Serializers for registration and user profile responses.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Create a new user; password is write-only and validated by Django validators."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "email", "password", "password_confirm", "first_name", "last_name")
        read_only_fields = ("id",)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        email = validated_data["email"]
        # Username required by AbstractUser — derive from email
        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )
        return user


class EmailTokenObtainPairSerializer(serializers.Serializer):
    """
    Login with email + password instead of username.
    Used by SimpleJWT LoginView.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        email = attrs.get("email", "").lower()
        password = attrs.get("password")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials."}
            )
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"detail": "No active account found with the given credentials."}
            )
        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        attrs["user"] = user
        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Public user fields returned after login/register."""

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "date_joined")
        read_only_fields = fields
