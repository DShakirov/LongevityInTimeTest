from celery import shared_task
from django.core.mail import send_mail



@shared_task
def send_otp(email, otp):
    subject = 'Your password for Longevity In Time Test'
    msg = f'Hello.\n Your one-time password for Longevity In Time Test is {otp}.\nBest regards.'
    send_mail(
            subject,
            msg,
            'shakirovdominatus@mail.ru',
            [email],
            fail_silently=False,
                )

