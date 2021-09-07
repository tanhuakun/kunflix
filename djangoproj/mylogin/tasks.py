from djangoproj.celery import app as celery_app
import random
import string
from .models import ForgetPassword
from django.contrib.auth.models import User
from django.core.mail import send_mail

@celery_app.task(name="forget_password")
def forget_password_email(username):
    u = User.objects.get(username=username)
    letters = string.ascii_letters
    key1 = ''.join(random.choice(letters) for i in range(10))
    key2 = ''.join(random.choice(letters) for i in range(6))
    newforget = ForgetPassword(requser=u, key1=key1, key2=key2)
    newforget.save()
    send_mail(
        'Reset Password',
        f'Hello {u.username},\n' + \
        'You have requested to reset your password. Please inform me ASAP if you did not request to reset it\n' + \
        f'You can reset by going to the link below:\n\n' + \
        f'https://kunflix.ydns.eu/forgotmypass/{key1}/{key2}/{u.username}\n\n' + \
        'Thank you for using this site! Please do not reply to this email as I cannot receive emails.',
        'huakun@kunflix.ydns.eu',
        [f'{u.email}'],
        fail_silently=False,
    )


    