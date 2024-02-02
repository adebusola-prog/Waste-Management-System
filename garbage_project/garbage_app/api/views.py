from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import GarbageCollector
from garbage_app.api.serializers import (
    CollectionPlanSerializer,
    CollectionRequestSerializer,
    GarbageCollectorSerializer,
    RequestRejectionSerializer,
    GarbageDetailCollectorSerializer,
    CollectionRequestSubscribeSerializer,
)
from garbage_app.models import CollectionPlan, CollectionRequest, CustomUser


class CustomerGarbageCollectorsView(APIView):
    def get(self, request):
        if request.user.customer_location and not request.user.is_superuser:
            garbage_collectors = GarbageCollector.accepted_collectors.\
                filter(user__garbage_collector_location__name=request.user.customer_location)
            serializer = GarbageCollectorSerializer(garbage_collectors, many=True)
            return Response(serializer.data)
        else:
            return Response({"message": "No Collector in your location"})
        
class CustomerGarbageCollectorDetailView(APIView):
    def get_object(self, pk):
        try:
            if self.request.user.customer_location and not self.request.user.is_superuser:
                return GarbageCollector.accepted_collectors.filter\
                    (user__garbage_collector_location__name=self.request.user.customer_location).filter(id=pk).first()
        except GarbageCollector.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk, format=None):
        garbage_collector = self.get_object(pk)
        serializer = GarbageDetailCollectorSerializer(garbage_collector)
        return Response(serializer.data)


@api_view(['POST'])
def create_collection_plan(request):
    if request.method == "POST":
        serializer = CollectionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(garbage_collector=request.user.garbagecollector)
            return Response({"message": "Collection plan created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CollectionPlanListView(APIView):
    def get(self, request):
        plans = CollectionPlan.active_objects.all()
        serializer = CollectionPlanSerializer(plans, many=True)
        return Response(serializer.data)

class CollectionPlanListView(APIView):
    def get(self, request):
        plans = CollectionPlan.active_objects.all()
        serializer = CollectionPlanSerializer(plans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollectionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.garbage_collector= request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CollectionPlanDetailView(APIView):
    def get(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        serializer = CollectionPlanSerializer(plan)
        return Response(serializer.data)

    def put(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        serializer = CollectionPlanSerializer(plan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        plan = CollectionPlan.active_objects.filter(id=pk).first()
        if plan:
            plan.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class AcceptRequestView(APIView):
    def post(self, request):
        if not request.user.garbage_collector_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)

        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)

        if not all_request:
            return Response("No request found", status=status.HTTP_404_NOT_FOUND)
        
        for request_obj in all_request:
            if request_obj.status in [CollectionRequest.Status.PENDING, CollectionRequest.Status.REJECTED]:
                request_obj.status = CollectionRequest.Status.ACCEPTED
                request_obj.save()
                send_accept_email(request_obj)
                break
        
        redirect_url = reverse('garbage:home_page')
        return Response({"redirect_url": redirect_url}, status=status.HTTP_200_OK)

class RejectRequestView(APIView):
    def post(self, request):
        if not request.user.garbage_collector_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        
        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)
        
        if not all_request:
            return Response("No request found", status=status.HTTP_404_NOT_FOUND)
        
        for request_obj in all_request:
            serializer = RequestRejectionSerializer(data=request.data, instance=request_obj)
            if serializer.is_valid():
                rejection_reason = serializer.validated_data.get('rejection_reason')
                if request_obj.status in [CollectionRequest.Status.PENDING, CollectionRequest.Status.ACCEPTED]:
                    request_obj.status = CollectionRequest.Status.REJECTED
                    request_obj.rejection_reason = rejection_reason
                    request_obj.save()
                    # send_reject_email(request_obj, rejection_reason)
                    break
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        redirect_url = reverse('garbage:home_page')
        return Response({"redirect_url": redirect_url}, status=status.HTTP_200_OK)

class CustomerSubscriptionListView(APIView):
    def get(self, request, pk):
        if request.user.id != pk:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        
        customer = get_object_or_404(CustomUser.active_objects, customer_location__isnull=False, id=pk)
        all_customer_request = CollectionRequest.active_objects.filter(customer=customer)
        serializer = CollectionRequestSerializer(all_customer_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def send_accept_email(request_obj):
    subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} is now {request_obj.status}"
    message = f"Your request has been accepted and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}"
    send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com'])


def send_reject_email(request_obj, rejection_reason):
    subject = f"Your Garbage Collection Request for plan: {request_obj.plan.status} {request_obj.plan.price} {request_obj.status}"
    message = f"Your request has been rejected and the status is now {request_obj.status} by {request_obj.garbage_collector.user.company_name}. " \
            f"Reason for rejection: {rejection_reason}"
    send_mail(subject, message, 'adebusolayeye@gmail.com', [request_obj.customer.email, 'adebusolayeye@gmail.com'])

class CustomerSubscribe(APIView):

    def post(self, request, id):
        if not request.user.customer_location:
            return Response("Forbidden", status=status.HTTP_403_FORBIDDEN)
        garbage_collector = GarbageCollector.accepted_collectors.filter(user_id=id).first()
        print(garbage_collector)
        plans = CollectionPlan.active_objects.filter(garbage_collector=garbage_collector)
        # company = GarbageCollector.accepted_collectors.filter(id=pk, user_id=id).first()

        serializer = CollectionRequestSubscribeSerializer(data=request.data, instance=plans)
        if serializer.is_valid():
            plan_id = serializer.validated_data.get('plan')
            print(plan_id)
            address = serializer.validated_data.get('address')
            print(address)

            # Create the CollectionRequest object
            CollectionRequest.objects.create(
                garbage_collector=garbage_collector,
                customer=request.user,
                plan=plan_id,
                location=request.user.customer_location,
                address=address
            )

            return Response({"message": "Collection request created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyCollectionRequestAPIView(APIView):
    def get(self, request):
        if not request.user.garbage_collector_location:
            return HttpResponseForbidden()

        company_request = GarbageCollector.accepted_collectors.filter(user=request.user).first()
        all_request = CollectionRequest.active_objects.filter(garbage_collector=company_request)

        if not all_request:
            return Response({"message": "No requests found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CollectionRequestSerializer(all_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
