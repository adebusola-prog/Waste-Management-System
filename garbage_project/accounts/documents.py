from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import Completion

from .models import GarbageCollector, CustomUser
from garbage_app.models import Location


@registry.register_document
class CustomUserDocument(Document):
    class Index:
        name = 'customuser_index'

    first_name = fields.TextField()
    middle_name = fields.TextField()
    company_name = fields.TextField()
    username = fields.TextField()
    last_name = fields.TextField()
    email = fields.TextField()
    customer_location = fields.NestedField(properties={
        'name': fields.TextField()
    })
    garbage_collector_location = fields.NestedField(properties={
        'name': fields.TextField()
    })
   

    class Django:
        model = CustomUser

@registry.register_document
class GarbageCollectorDocument(Document):
    class Index:
        name = 'garbagecollector_index'

    user = fields.ObjectField(properties={
        'first_name': fields.TextField(),
        'middle_name': fields.TextField(),
        'company_name': fields.TextField(),
        'username': fields.TextField(),
        'last_name': fields.TextField(),
        'email': fields.TextField(),
        'customer_location': fields.NestedField(properties={
            'name': fields.TextField()
        }),
        'garbage_collector_location': fields.NestedField(properties={
            'name': fields.TextField()
        }),
       
    })
    

    class Django:
        model = GarbageCollector

@registry.register_document
class LocationDocument(Document):
    class Index:
        name = 'location_index'

    name = fields.TextField()

    class Django:
        model = Location
