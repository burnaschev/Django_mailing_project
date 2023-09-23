from django.contrib import admin

from mailing.models import Client, Mailing, Message, ClientMailing, Log


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email',)
    search_fields = ('full_name',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('status', 'mailing_period',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_subject', 'message_body',)


@admin.register(ClientMailing)
class ClientMailingAdmin(admin.ModelAdmin):
    list_display = ('client', 'mailing',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('client', 'mailing',)
