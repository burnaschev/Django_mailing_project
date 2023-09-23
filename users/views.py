import random

from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from users.forms import UserRegisterForm, UserForm
from users.models import User
from users.services import send_new_password, send_verify_email


class LoginView(BaseLoginView):
    template_name = 'users/login.html'


class LogoutView(BaseLogoutView):
    pass


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/register.html'

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.verification_token = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        new_user.save()
        send_verify_email(self.request, new_user.verification_token, new_user.email)
        return super().form_valid(form)


def verify_email(request, token):
    user = get_object_or_404(User, verification_token=token)
    if not user.email_verified:
        user.email_verified = True
        user.save()

    return render(request, 'users/verification_success.html')


class UserUpdateView(UpdateView):
    model = User
    success_url = reverse_lazy('users:profile')
    form_class = UserForm
    template_name = 'users/user_form.html'

    def get_object(self, queryset=None):
        return self.request.user


def generate_new_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    send_new_password(request.user.email, new_password)
    request.user.set_password(new_password)
    request.user.save()
    return redirect(reverse('catalog:home'))
