from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.urls import reverse

from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Generate and send e-male to the user
    """

    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="..."),
        # message:
        "Here is your reset password url {url}".format(url=context.get('reset_password_url')),
        # from:
        "example@example.com",
        # to:
        [reset_password_token.user.email]
    )
    try:
        msg.send()
    except Exception as e:
        print(e)
