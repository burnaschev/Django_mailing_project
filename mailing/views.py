from random import sample

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.models import Blog
from mailing.forms import MailingForm, ClientForm, MessageForm
from mailing.models import Mailing, ClientMailing, Client, Message


class ManagerRequiredMixin:

    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name="manager").exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


def index(request):
    blog = Blog.objects.all()
    mailing = Mailing.objects.all()
    mailing_is_active = Mailing.objects.filter(status='Started')
    client_mailing = ClientMailing.objects.all()

    unique_clients = cache.get('unique_clients')
    if unique_clients is None:
        unique_clients = set([cm.client for cm in client_mailing])
        cache.set('unique_clients', unique_clients, 60)

    sample_size = min(len(blog), 3)
    random_articles = cache.get('random_articles')
    if random_articles is None:
        random_articles = sample(list(blog), k=sample_size)
        cache.set('random_articles', random_articles, 60)

    context = {
        'random_articles': random_articles,
        'total_mailings': len(mailing),
        'active_mailings': len(mailing_is_active),
        'unique_clients': len(unique_clients)
    }

    return render(request, 'mailing/home.html', context)


@login_required
def contacts(request):
    return render(request, 'mailing/contacts.html')


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing

    def get_queryset(self):
        if self.request.user.groups.filter(name="manager").exists() or self.request.user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(users=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing

    def get_queryset(self):
        if self.request.user.groups.filter(name="manager").exists() or self.request.user.is_superuser:
            return Mailing.objects.all()
        return Mailing.objects.filter(users=self.request.user)


class MailingCreateView(LoginRequiredMixin, ManagerRequiredMixin, UserPassesTestMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    permission_required = 'mailing.change_mailing'
    success_url = reverse_lazy('mailing:list')

    def test_func(self):
        return self.request.user.email_verified or self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect(reverse_lazy('mailing:verification_failed'))

    def form_valid(self, form):
        self.object = form.save()
        self.object.users = self.request.user
        self.object.save()

        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    permission_required = 'mailing.change_mailing'
    success_url = reverse_lazy('mailing:list')


class MailingDeleteView(LoginRequiredMixin, ManagerRequiredMixin, DeleteView):
    model = Mailing
    permission_required = 'mailing.delete_mailing'
    success_url = reverse_lazy('mailing:list')


class ClientListView(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        return Client.objects.filter(users=self.request.user)


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.users = self.request.user
        self.object.save()

        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:client_list')


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailing:client_list')


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    extra_context = {
        'title': 'Список сообщений'
    }


class MessageCreateView(LoginRequiredMixin, ManagerRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing:messages_list')

    def get_permission_object(self):
        return self.object


class MessageUpdateView(LoginRequiredMixin, ManagerRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    permission_required = 'mailing.change_message'
    success_url = reverse_lazy('mailing:messages_list')


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('mailing:messages_list')


class ClientMailingListView(LoginRequiredMixin, ListView):
    model = ClientMailing

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['clients'] = Client.objects.filter(users=self.request.user)
        context_data['mailing_pk'] = self.kwargs.get('pk')
        context_data['client_mailings'] = ClientMailing.objects.filter(mailing_id=self.kwargs.get('pk'))

        return context_data


def toggle_client(request, pk, client_pk):
    if ClientMailing.objects.filter(client_id=client_pk, mailing_id=pk).exists():
        ClientMailing.objects.filter(client_id=client_pk, mailing_id=pk).delete()
    else:
        ClientMailing.objects.create(client_id=client_pk, mailing_id=pk)
    return redirect(reverse('mailing:mailing_clients', args=[pk]))


def stop_mailing(request, pk):
    if not request.user.groups.filter(name="manager").exists() and not request.user.is_superuser:
        raise PermissionDenied
    mailing = Mailing.objects.get(pk=pk)
    if mailing.status == mailing.STARTED or mailing.status == mailing.CREATED:
        mailing.status = mailing.STOPPED
        mailing.save()
    else:
        mailing.status = mailing.STARTED
        mailing.save()
    return redirect(reverse('mailing:list'))


@login_required
def verification_failed(request):
    return render(request, 'mailing/verification_failed.html')
