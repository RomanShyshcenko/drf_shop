from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response


def send_verification_email(user):
    confirmation_token = default_token_generator.make_token(user)
    user_id = user.id
    body = f"Here is your reset password url http://localhost:8000/{reverse('email_verification')}" \
           f"?user_id={user_id}&confirmation_token={confirmation_token}",

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="..."),
        # message:
        body,
        # from:
        "example@example.com",
        # to:
        [user.email]
    )
    print(body)
    try:
        if msg.send():
            return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

