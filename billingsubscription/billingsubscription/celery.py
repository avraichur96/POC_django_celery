import os
from celery import Celery

# set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'billingsubscription.settings')

app = Celery('billingsubscription')

# load config from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# auto-discover tasks in all registered apps
app.autodiscover_tasks()
