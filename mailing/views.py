from random import sample

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from blog.models import Blog
from mailing.forms import MailingForm, ClientForm, MessageForm
from mailing.models import Mailing, ClientMailing, Client, Message


@login_required
def index(request):
    blog = Blog.objects.all()
    mailing = Mailing.objects.all()
    mailing_is_active = Mailing.objects.filter(status='Started')
    client_mailing = ClientMailing.objects.all()
    unique_clients = set([cm.client for cm in client_mailing])

    sample_size = min(len(blog), 3)
    random_articles = sample(list(blog), k=sample_size)
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
        return Mailing.objects.filter(users=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing

    def get_queryset(self):
        return Mailing.objects.filter(users=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing:list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.users = self.request.user
        self.object.save()

        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mailing:list')

    def get_queryset(self):
        return Mailing.objects.filter(users=self.request.user)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
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


class MessageListView(ListView):
    model = Message
    extra_context = {
        'title': 'Список сообщений'
    }


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing:messages_list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('mailing:messages_list')


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('mailing:messages_list')


class ClientMailingListView(ListView):
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
