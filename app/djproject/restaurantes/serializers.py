from rest_framework_mongoengine import serializers
from rest_framework_mongoengine import viewsets

from .models import restaurant as restaurant_

class restaurantsSerializer(serializers.DocumentSerializer):

   class Meta:
       model = restaurant_
       fields = ('name', 'url', 'datetime', 'address', 'avg_stars', 'origin', 'reviews') 


class restaurantsViewSet(viewsets.ModelViewSet):
   lookup_field = 'name'
   serializer_class = restaurantsSerializer

   def get_queryset(self):
       return restaurant_.objects.all()
