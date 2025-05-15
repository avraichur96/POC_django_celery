from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from .models import *
from .serializers import *
from .tasks import generate_invoices

from datetime import date, timedelta


class DummyTestListView(APIView):
    """
    Please ignore this view, it is created only for testing purposes.
    """

    permission_classes = []

    def get(self, request):
        # Uncomment to test out generate invoices task on demand without scheduling.
        # generate_invoices.delay()

        return Response(data={
            "details": "This is a dummy listing response to test IsAuthenticated permission class and task triggers."},
                        status=status.HTTP_200_OK)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'token': token.key})
            return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscribeActionView(APIView):
    """
    Single view class to subscribe and unsubscribe for the given plan and the user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        input_data = request.data
        ser = SubscribeRequestSerializer(data=input_data)
        ser.is_valid(raise_exception=True)
        cleaned_data = ser.validated_data

        is_subscribe = cleaned_data["is_subscribe"]  # False for unsubscribe and True for subscribe.
        plan_id = cleaned_data["plan_id"]
        username = cleaned_data["username"]

        try:
            plan = Plan.objects.get(pk=plan_id)
        except Plan.DoesNotExist:
            raise ValidationError(message={"Plan": "Invalid plan ID passed."})

        try:
            user = CustomUser.objects.filter(username=username).first()  # Always single user per username.
        except CustomUser.DoesNotExist:
            raise ValidationError(
                message={"User": "You do not have an account. Please register with us and try again."})

        # According to our design we only have one subscription per system.
        existing_subscription = Subscription.objects.filter(user=user.id, status=SubscriptionState.ACTIVE).first()

        if not is_subscribe:
            # Unsubscribe flow
            if not existing_subscription.exists():
                raise ValidationError(
                    message={"Subscription": "This user does not have an active subscription to be CANCELLED."})

            existing_subscription.update(status=SubscriptionState.CANCELLED)
        else:
            # Subscription flow. Can be reactivation or new creation.
            if existing_subscription.exists():
                existing_subscription.update(status=SubscriptionState.ACTIVE, start_date=date.today(),
                                             end_date=date.today() + timedelta(days=30))
                return Response(data={"Successfully updated your subscription."}, status=status.HTTP_200_OK)

            try:
                new_sub = Subscription(start_date=date.today(), end_date=+ timedelta(days=30), user=user.id,
                                       plan=plan.id,
                                       status=SubscriptionState.ACTIVE)
                new_sub.save()
            except Exception as e:
                # Print or log the error.
                print(f"There was a problem when adding Subscription... {e}")

        return Response(data={"Successfully added your subscription."}, status=status.HTTP_200_OK)


class ListInvoicesView(APIView):
    """
    List invoices with filters, user and status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        input_data = request.data
        ser = ListInvoicesRequestSerializer(data=input_data)
        ser.is_valid(raise_exception=True)
        cleaned_data = ser.validated_data

        # No need to validate filters as there won't be data for the wrong criteria.
        plan_id = cleaned_data["plan_id"]
        username = cleaned_data["username"]
        status_id = cleaned_data["status"]

        invoices = Invoice.objects.select_related("user", "plan").filter(user__username=username, plan=plan_id,
                                                                         status=status_id)

        ser = ListInvoicesOutputSerializer(instance=invoices, many=True)
        data = ser.data

        return Response(data=data, status=status.HTTP_200_OK)
