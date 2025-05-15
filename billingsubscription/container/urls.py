from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('dummy/', DummyTestListView.as_view(), name='dummy'),
    path('subscribe/', SubscribeActionView.as_view(), name='subscribe'),
    path('list_invoices/', ListInvoicesView.as_view(), name='list_invoices')
]
