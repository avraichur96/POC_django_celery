from celery import shared_task
from .models import *
from datetime import date, timedelta


@shared_task
def dummy_task():
    return f"dummy print returned after task.delay() ."


@shared_task
def generate_invoices():
    # Assuming we generate the invoices 2 days prior to the end date of the subscription.
    filter_date = date.today() + timedelta(days=2)
    collect_subs = Subscription.objects.select_related("plan").filter(end_date__gte=filter_date,
                                                                      status=SubscriptionState.ACTIVE)
    invoices = []
    count = 0
    for sub in collect_subs:
        single_inv = Invoice(due_date=sub.end_date, issue_date=date.today(), amount=sub.plan.amount, user=sub.user,
                             plan=sub.plan.id,
                             status=InvoiceStatus.PENDING)
        invoices.append(single_inv)
        count += 1

    try:
        Invoice.objects.bulk_create(invoices)
    except Exception as e:
        # Print or log the error. We can also store to additional DB table called task_audit that can hold exception
        # information and timestamp for task debug purposes and respawn if necessary.
        print(f"There was a problem during Bulk creation of invoices. Force run the generate task again... {e}")

    return f"Task completed Successfully. Generated {count} Invoices."


@shared_task
def mark_invoices_remind_users():
    pending_invoices = Invoice.objects.select_related("user", "plan").filter(due_date__gte=date.today()).exclude(
        status=InvoiceStatus.PAID)

    for inv in pending_invoices:
        # generate Stripe link and send reminder emails. Currently, a dummy function.
        name = str(inv.user)  # CustomUser __str__ has been override to return first + last name.
        link = "dummy_link_without_stripe"
        plan_name = inv.plan.name
        to_email = inv.user.email  # Currently unused until email proxy integration.
        print(
            f"Dear {name}, your invoice for plan ' {plan_name} ' is due today. Please make the payment on the link "
            f"below. {link}")

    # mark the invoices as OVERDUE after sending in the reminders.
    Invoice.objects.filter(due_date__gte=date.today()).update(status=InvoiceStatus.OVERDUE)
    return "Task completed Successfully."
