from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import smart_bytes
from django.conf import settings
import uuid
from datetime import datetime, timedelta
from django.core.mail import send_mail

from user_app.api.serializers import (
    CustomUserSerializer,
    password_validator_check,
)
from user_app.models import CustomUser, ResetToken


class RegisterView(APIView):
    def post(self, request):
        """
        Register a user in database.
        Args:
            request (Request): The request object containing the user's username,email and password.
        Returns:
            Response: A response object with a success message "User created" if the user was created,
            or an error message if the request is invalid.
        """
        try:
            CustomUser.objects.get(email=request.data["email"])

        except CustomUser.DoesNotExist:
            serializer = CustomUserSerializer(data=request.data)
            # White space validator
            if " " in request.data["username"]:
                raise ValidationError({"Error": "Username cannot have whitespaces"})

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"Success": "User created"}, status=status.HTTP_201_CREATED
                )

            else:
                return Response(
                    {"Error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )

        else:
            return Response(
                {"Error": "User already present Please Login"},
                status.HTTP_400_BAD_REQUEST,
            )

class ResetPasswordEmailView(APIView):
    @staticmethod
    def send_email(to, subject, message):
        try:
            email_address = settings.SEND_EMAIL_HOST
            email_password = settings.SEND_EMAIL_PASSWORD
            if email_address is None or email_password is None:
                return False
            send_mail(
                subject=subject,
                message=message,
                from_email=email_address,
                auth_user=email_address,
                auth_password=email_password,
                recipient_list=[to],
                fail_silently=False,
            )
            return True
        except Exception as e:
            return str(e)

    def post(self, request):
        """
        Sends a password reset email to user registered email.
        Args:
            request (Request): The request object containing the user's email.
        Returns:
            Response: A response object with a success message
            "Email send Please visit the url in your inbox to reset password" if the email was valid
             or an error message if the request is invalid.
        """
        if not CustomUser.objects.filter(email=request.data["email"]).exists():
            raise ValidationError({"Error": "You are not a registered user"})
        user = CustomUser.objects.get(email=request.data["email"])
        encoded_user_id = urlsafe_base64_encode(smart_bytes(user.pk))
        token = uuid.uuid4()
        # Checking if user token is already present or not if yes delete that record
        if ResetToken.objects.filter(user=user).exists():
            instance = ResetToken.objects.get(user=user)
            instance.delete()
        ResetToken.objects.create(
            user=user,
            reset_token=token,
            created_time=datetime.now(),
            encoded_user_id=encoded_user_id,
        )
        # Generating a link
        link = f"{settings.BASE_URL}reset-password/{encoded_user_id}/{token}/"
        # Mail configuration
        to = request.data["email"]
        subject = "Subject : Reset Your Password"
        message = (
            f"Dear {user.username},\n\n"
            f"We have received a request to reset your password for application : The waste that world needs!.\n"
            f"To reset your password, please click on the following link:\n{link}\n"
            f"If you did not request to reset your password, "
            f"Please ignore this email and your account will remain unchanged.\n"
            f"Please note that the link will expire in 30 Minutes. If the link expires, "
            f"you will need to request another password reset.\n\n"
            f"Thank you,\n\nOperations Team."
        )
        s = self.send_email(to, subject, message)
        if s is not True:
            return Response({"Error": s}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "Success": "Email send Please visit the url in your inbox to reset password"
            }
        )


class ResetPasswordView(APIView):
    def put(self, request, uid, token):
        """
        Resets the user password.
        Args:
            request (Request): The request object containing the user's password.
        Returns:
            Response: A response object with a success message "User password reset" if the encoded_user_id and token
            is valid or an error message if the request is invalid.
        """
        password = password_validator_check(request.data["password"])
        # Decoding the userid provided in url
        try:
            user_id = int(urlsafe_base64_decode(uid).decode("ascii"))
        except (UnicodeDecodeError, ValueError):
            raise ValidationError({"Error": "Oops! Someone corrupted the url"})
        if not CustomUser.objects.filter(id=user_id).exists():
            raise ValidationError({"Error": "Oops! Someone corrupted the url"})
        # Getting the token from db where it references to userid
        try:
            instance = ResetToken.objects.get(user=user_id)
        except ResetToken.DoesNotExist:
            return Response(
                {"Error": "Oops! Someone corrupted the url"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        if token != instance.reset_token or uid != instance.encoded_user_id:
            raise ValidationError({"Error": "Oops! Someone corrupted the url"})

        if instance.blacklisted_token == token:
            raise ValidationError(
                {"Error": "You have already changed your password! Request a new email"}
            )

        today = datetime.now().time()
        # Getting token generation time
        token_time = instance.created_time.time()
        difference = timedelta(
            hours=(today.hour - token_time.hour),
            minutes=(today.minute - token_time.minute),
            seconds=(today.second - token_time.second),
        )
        if difference.seconds > 1800:
            raise ValidationError({"Error": "Reset Link has expired Request again"})

        # Getting the user
        user = CustomUser.objects.get(id=user_id)
        user.set_password(password)
        user.save()
        # If the user password is updated also populate the blacklist token field in instance object
        instance.blacklisted_token = token
        instance.save()
        return Response({"Success": "User password reset"}, status=status.HTTP_200_OK)
