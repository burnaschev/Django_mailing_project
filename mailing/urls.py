from django.urls import path
from django.views.decorators.cache import cache_page

from mailing.apps import MailingConfig
from mailing.views import MailingListView, MailingDetailView, MailingDeleteView, MailingUpdateView, MailingCreateView, \
    index, contacts, ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, ClientDeleteView, \
    MessageUpdateView, MessageListView, MessageCreateView, MessageDeleteView, ClientMailingListView, toggle_client, \
    stop_mailing, verification_failed

app_name = MailingConfig.name

urlpatterns = [
    path('', cache_page(15)(index), name='home'),
    path('contacts/', cache_page(60)(contacts), name='contacts'),
    path('mailing/list/', MailingListView.as_view(), name='list'),
    path('mailing/view/<int:pk>/', MailingDetailView.as_view(), name='view'),
    path('mailing/create/', cache_page(60)(MailingCreateView.as_view()), name='create'),
    path('mailing/edit/<int:pk>/', cache_page(60)(MailingUpdateView.as_view()), name='edit'),
    path('mailing/delete/<int:pk>/', MailingDeleteView.as_view(), name='delete'),
    path('mailing/verification_failed/', cache_page(60)(verification_failed), name='verification_failed'),

    path('client/list/', ClientListView.as_view(), name='client_list'),
    path('client/view/<int:pk>/', cache_page(60)(ClientDetailView.as_view()), name='client_view'),
    path('client/create/', cache_page(60)(ClientCreateView.as_view()), name='client_create'),
    path('client/edit/<int:pk>/', ClientUpdateView.as_view(), name='client_edit'),
    path('client/delete/<int:pk>/', cache_page(60)(ClientDeleteView.as_view()), name='client_delete'),

    path('messages/', MessageListView.as_view(), name='messages_list'),
    path('messages/create/', cache_page(60)(MessageCreateView.as_view()), name='messages_create'),
    path('messages/update/<int:pk>/', cache_page(60)(MessageUpdateView.as_view()), name='messages_update'),
    path('messages/delete/<int:pk>/', cache_page(60)(MessageDeleteView.as_view()), name='messages_delete'),

    path('<int:pk>/clients/', ClientMailingListView.as_view(), name='mailing_clients'),
    path('<int:pk>/clients/add/<int:client_pk>/', toggle_client, name='mailing_clients_toggle'),
    path('mailing/list//status/<int:pk>/', stop_mailing, name='stop_mailing'),
]
