from django.core.exceptions import ValidationError
from oil_transport.deliveries.models import DeliveryStation, Delivery
from datetime import date
from django.utils import timezone

class MultipleSerializerMixin:

    list_serializer_class = None
    detail_serializer_class = None
    update_serializer_class = None
    create_serializer_class = None


    def get_serializer_class(self):
        if self.action == 'create' and self.create_serializer_class is not None:
            return self.create_serializer_class
        if self.action == 'list' and self.list_serializer_class is not None:
            return self.list_serializer_class
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        if self.action in ['update', 'partial_update'] and self.update_serializer_class is not None:
            return self.update_serializer_class

        return super().get_serializer_class()
    
