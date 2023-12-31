# Generated by Django 4.2.5 on 2023-09-23 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mailing', '0002_mailing_users'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientmailing',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mailing.client', verbose_name='Клиент'),
        ),
        migrations.AlterField(
            model_name='clientmailing',
            name='mailing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mailing.mailing', verbose_name='Рассылка клиента'),
        ),
    ]
