import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView

from users.forms import UserRegisterForm, UserForm
from users.models import User
from users.services import send_new_password, send_verify_email


class ManagerRequiredMixin(PermissionRequiredMixin):
    permission_required = 'users.manager_access'

    def handle_no_permission(self):
        raise PermissionDenied


class LoginView(BaseLoginView):
    template_name = 'users/login.html'


class LogoutView(BaseLogoutView):

    def get_success_url(self):
        return reverse_lazy('mailing:list')


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

def verify_email_btn(request, pk):
    user = get_object_or_404(User, pk=pk)
    send_verify_email(request, user.verification_token, user.email)

    return render(request, 'mailing/verification_failed.html')

class UserUpdateView(UpdateView):
    model = User
    success_url = reverse_lazy('users:profile')
    form_class = UserForm
    template_name = 'users/user_form.html'

    def get_object(self, queryset=None):
        return self.request.user


class UserListView(ListView, ManagerRequiredMixin):
    model = User

    def get_queryset(self):
        if self.request.user.groups.filter(name="manager").exists() or self.request.user.is_superuser:
            return User.objects.filter(is_staff=False, is_superuser=False)
        else:
            raise PermissionDenied('Доступ запрещен')


def generate_new_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    send_new_password(request.user.email, new_password)
    request.user.set_password(new_password)
    request.user.save()
    return redirect(reverse('mailing:home'))


@login_required
def block_user(request, pk):
    if request.user.groups.filter(name="manager").exists() or request.user.is_superuser:
        user = User.objects.get(pk=pk)
        if not user.is_active:
            user.is_active = True
            user.save()
        else:
            user.is_active = False
            user.save()
        return redirect(reverse('users:user_list'))
    else:
        raise PermissionDenied('Доступ запрещен')
