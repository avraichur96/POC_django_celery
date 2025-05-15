from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extending the default auth User of the DRF auth framework with custom fields as necessary for our scenario.
    """
    phone_number = models.CharField(max_length=10, blank=True, null=True,
                                    help_text="Optional Phone number info from the user.")

    def __str__(self):
        """
        :return: first name, appended to the phone number.
        """
        return self.first_name + "_" + self.last_name


class PlanTypes:
    BASIC = 0
    PRO = 1
    ENTERPRISE = 2

    DEFAULT = BASIC

    CHOICES = [(BASIC, "Basic"),
               (PRO, "Pro"),
               (ENTERPRISE, "Enterprise"), ]


class SubscriptionState:
    ACTIVE = 0
    EXPIRED = 1
    CANCELLED = 2

    DEFAULT = None

    CHOICES = [(ACTIVE, "Active"),
               (EXPIRED, "Expired"),
               (CANCELLED, "Cancelled")]


class InvoiceStatus:
    PENDING = 0
    PAID = 1
    OVERDUE = 2

    DEFAULT = PENDING

    CHOICES = [(PENDING, "Pending"), (PAID, "Paid"), (OVERDUE, "Overdue")]


class Plan(models.Model):
    """
    Holds the fixed set of plans available on the system.
    """
    plan_type = models.IntegerField(choices=PlanTypes.CHOICES, default=PlanTypes.DEFAULT)
    name = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=True, help_text="Long description of the plan.")
    amount = models.DecimalField(max_digits=9, decimal_places=4, null=False, default=0.00)


class Subscription(models.Model):
    """
    Holds the relation between the user and plan subscribed. Also holds info on the status of the subscription.
    """
    status = models.IntegerField(choices=SubscriptionState.CHOICES, default=SubscriptionState.CANCELLED)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # Highly unlikely plans will be deleted but still CASCADE for safety.
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField(null=False, help_text="Always populated when subscription starts.")
    end_date = models.DateField(null=False, help_text="Always populated when subscription starts.")


class Invoice(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=9, decimal_places=4, null=False)
    issue_date = models.DateField(null=False)
    due_date = models.DateField(null=True)
    status = models.IntegerField(choices=InvoiceStatus.CHOICES, default=InvoiceStatus.DEFAULT)
