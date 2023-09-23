from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_new_password(email, new_password):
    send_mail(
        subject='Вы сменили пароль',
        message=f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
    )

def send_verify_email(request, verification_token, email):
    send_mail(
        subject='Подтвердите вашу почту',
        message=f'Для подтверждения вашей почты, перейдите по ссылке: '
                f'{request.build_absolute_uri(reverse(viewname="users:verify_email", args=[verification_token]))}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )
