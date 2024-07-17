from rest_framework import serializers

from .models import Contact, Spam

class ContactSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone', 'email']

    def validate_phone(self, value):
        user = self.context['request'].user
        if Contact.objects.filter(user=user, phone=value).exists():
            raise serializers.ValidationError("This contact is already exists.")
        return value

class SpamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Spam
        fields = ['phone', 'report']

class SpamInputSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)