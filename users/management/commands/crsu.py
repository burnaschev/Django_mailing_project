from django.core.management import BaseCommand
import os
from users.models import User
from dotenv import load_dotenv

load_dotenv('.env')

class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            email='admin@mail.com',
            first_name='admin',
            last_name='group',
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

        user.set_password(os.getenv('ADMIN_PASSWORD'))
        user.save()
