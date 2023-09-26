from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from mailing.models import Log, Mailing
from users.models import User


def send_mailing(mailing_settings, client_m):
    try:
        send_mail(
            mailing_settings.message.message_subject,
            mailing_settings.message.message_body,
            settings.EMAIL_HOST_USER,
            [client_m.client.email],
            fail_silently=False,
        )
        status = Log.STATUS_OK
        response = '200'
    except Exception as e:
        status = Log.STATUS_FAILED
        response = str(e)

    Log.objects.create(
        status=status,
        mailing=mailing_settings,
        client_id=client_m.client_id,
        response=response
    )


def send_mails():
    current_time = datetime.utcnow()
    current_date = datetime.utcnow().date()
    for mailing_settings in Mailing.objects.filter(status=Mailing.STARTED):
        start_date = datetime.combine(current_date, mailing_settings.time_start)
        current_stop_date = datetime.combine(current_date, mailing_settings.time_stop)
        stop_date = current_stop_date if mailing_settings.time_stop > mailing_settings.time_start else current_stop_date + timedelta(
            hours=24)

        if start_date < current_time < stop_date:

            client_mailing = mailing_settings.clientmailing_set.all()
            for client_m in client_mailing:
                logs = Log.objects.filter(
                    mailing=mailing_settings, client=client_m.client
                )

                if logs.exists():
                    last_try_date = logs.order_by('-date_time').first().date_time.replace(tzinfo=None)

                    if mailing_settings.mailing_period == Mailing.D:
                        if (current_time - last_try_date).days >= 1:
                            send_mailing(mailing_settings, client_m)

                    elif mailing_settings.mailing_period == Mailing.W:
                        if (current_time - last_try_date).days >= 7:
                            send_mailing(mailing_settings, client_m)

                    elif mailing_settings.mailing_period == Mailing.M:

                        if (current_time - last_try_date).days >= 30:
                            send_mailing(mailing_settings, client_m)

                else:
                    send_mailing(mailing_settings, client_m)


