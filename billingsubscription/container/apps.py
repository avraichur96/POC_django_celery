from django.apps import AppConfig


class ContainerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'container'

    def ready(self):
        from .models import Plan, PlanTypes
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        import json

        try:
            # create a fixed set of plans the first time this runs on any system DB.
            if not Plan.objects.exists():
                Plan.objects.bulk_create([
                    Plan(name="Basic starter plan",
                         description="Want to test out our features? a great starting point.",
                         plan_type=PlanTypes.BASIC, amount=100.00),
                    Plan(name="Pro plan", description="Already active user, take it to the next level!",
                         plan_type=PlanTypes.PRO, amount=200.00),
                    Plan(name="Enterprise plan",
                         description="Go enterprise with unlimited dedicated access to our services.",
                         plan_type=PlanTypes.ENTERPRISE, amount=300.00)
                ])

            # Schedule the CRON tasks via Django celery beat, only if they still don't exist on our system.
            if not PeriodicTask.objects.filter(name="Invoice Generation v1").exists():
                # Task runs every single day checking for subscriptions.
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute='0',
                    hour='0',
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )

                PeriodicTask.objects.create(
                    crontab=schedule,
                    name='Invoice Generation v1',
                    task='myapp.tasks.generate_invoices',
                    args=json.dumps([]),
                )
            if not PeriodicTask.objects.filter(name="Reminder v1").exists():
                # Task runs every single day checking for overdue invoices. Scheduled in Queue one minute after the task above.
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute='1',
                    hour='0',
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )

                PeriodicTask.objects.create(
                    crontab=schedule,
                    name='Reminder v1',
                    task='myapp.tasks.mark_invoices_remind_users',
                    args=json.dumps([]),
                )

        except Exception as e:
            # Can use logging instead to capture this.
            print(f"There was a problem when adding plans and Celery tasks during setup stage... {e}")
