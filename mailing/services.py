import datetime

from django.conf import settings
from django.core.mail import send_mail

from mailing.models import Log, Mailing


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
        response = ''
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
    date_now = datetime.datetime.now(datetime.timezone.utc)
    for mailing_settings in Mailing.objects.filter(status=Mailing.STARTED):

        if (date_now.time() > mailing_settings.time_start) and (date_now.time() < mailing_settings.time_stop):

            client_mailing = mailing_settings.clientmailing_set.all()
            for client_m in client_mailing:
                logs = Log.objects.filter(
                    mailing=mailing_settings, client=client_m.client
                )

                if logs.exists():
                    last_try_date = logs.order_by('-date_time').first().date_time

                    if mailing_settings.mailing_period == Mailing.D:
                        if (date_now - last_try_date).days >= 1:
                            send_mailing(mailing_settings, client_m)

                    elif mailing_settings.mailing_period == Mailing.W:
                        if (date_now - last_try_date).days >= 7:
                            send_mailing(mailing_settings, client_m)

                    elif mailing_settings.mailing_period == Mailing.M:

                        if (date_now - last_try_date).days >= 30:
                            send_mailing(mailing_settings, client_m)

                else:
                    send_mailing(mailing_settings, client_m)
