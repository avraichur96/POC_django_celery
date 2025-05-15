# POC_django_celery
 A POC billing subscription system that exposes REST API and Celery tasks.
It uses redis queue and celery beat to schedule some daily useful tasks. This can be seamlessly integrated as a django app as all the major functionality is encapsulated in a django app called 'container'.

 ## Dependencies

- django, djangorestframework, celery, django-celery-beat
- Installation of redis Queue with configuration as mentioned in settings.py
- python manage.py runserver; Run Python Django in-built server.
- redis-server; Spawns redis instance. (UNIX sys only)
- celery -A container worker --loglevel=debug; Spawn celery worker. 
- Dont forget to activate venv before anything. 

## Features

- Exposes api/container/register/  - For user Sign Up. Token based auth using DRF. 
- Exposes api/container/login/ - For User Login. Token based auth using DRF.
- Exposes api/container/subscribe/ - For activate/deactivate subscription.
- Exposes api/container/list_invoices/ - List invoices and filtering ability for admin view.
- Two scheduled tasks every day to generate invoices, and send reminder to users. 

## Notable and future extensions.  

- CustomUser that extends the auth user to suit our needs (existing)
- Add proxy service that handles email and stripe integration (future enhancement)
- Add a task audit system as a separate entity in our DB system for easier scheduled task debugging (future enhancement)
- Change connector to a more robust DB than sqlite (future enhancement)
