# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery.decorators import task

from django.core.mail import send_mail
from django.contrib.auth.models import User


#+from tracker import celery_app

@task(name="notify_user")
def notify(user_id, message):
        """Emails user of the message alert"""
        # TODO HANDLE rest security and annonymous user
        try:
            email = User.objects.get(pk=user_id).email
        except:
            email = "ronniebhase@gmail.com"

        send_mail(
            'Tracker alert!',
            message,
            'admin@localhost.com',
            [email,],
            fail_silently=False,
        )
