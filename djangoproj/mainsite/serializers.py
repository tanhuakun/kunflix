from .models import Show, Requests
from rest_framework import serializers

class ShowShortSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Show
        fields = ['title', 'image', 'episodes', 'year']