from ..models import CollectionPlan, CollectionRequest, Location
from rest_framework import serializers
from accounts.models import GarbageCollector, CustomUser

# Garbage collectors
# can view collection requests
# can accept or reject (with reason) collection requests
# can create collection plans(daily, weekly) with prices

# .all--->remove add specific fields
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Location
        fields=("name",)


class CompanyCustomUserSerializer(serializers.ModelSerializer):
    garbage_collector_location = serializers.SerializerMethodField()

    def get_garbage_collector_location(self, obj):
        return [location.name for location in obj.garbage_collector_location.all()]

    class Meta:
        model = CustomUser
        fields = ("company_name", "garbage_collector_location")


class GarbageCollectorSerializer(serializers.ModelSerializer):
    user=CompanyCustomUserSerializer()    
    class Meta:
        model = GarbageCollector
        fields = ("id", "user", )
        read_only_fields= ['user']


class CollectionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPlan
        fields = ('status', 'price', )
    

class CollectionPlanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionPlan
        fields = ('id','status', 'price',)


class GarbageDetailCollectorSerializer(serializers.ModelSerializer):
    user=CompanyCustomUserSerializer()    
    my_plans = CollectionPlanDetailSerializer(many=True, read_only=True)
    class Meta:
        model = GarbageCollector
        fields = ("id", "user", "my_plans")
        read_only_fields= ['user']


class CollectionRequestSerializer(serializers.ModelSerializer):
    plan= CollectionPlanDetailSerializer()
    class Meta:
        model = CollectionRequest
        fields = ('plan', 'address')


class RequestRejectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ['rejection_reason']

class CollectionRequestSubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollectionRequest
        fields = ('plan', 'address')