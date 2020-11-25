from rest_framework import serializers
from .models import LID, LIT, CBS

class LIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = LID
        fields = '__all__'

class LITSerializer(serializers.ModelSerializer):
    class Meta:
        model = LIT
        fields = '__all__'

class CBSSerializer(serializers.ModelSerializer):
    class Meta:
        model = CBS
        fields = '__all__'