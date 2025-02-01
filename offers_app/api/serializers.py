from django.db import transaction
from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from user_auth_app.api.serializers import UserSerializer



class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']

    def validate_details(self, value):
            # Nur bei POST die volle Validierung
            if self.context['request'].method == 'POST':
                if len(value) != 3:
                    raise serializers.ValidationError("Es sind 3 Angebotsdetails erforderlich.")
                
                types = {detail['offer_type'] for detail in value}
                if types != {'basic', 'standard', 'premium'}:
                    raise serializers.ValidationError("Alle drei Typen müssen vorhanden sein.")
            
            # Bei PATCH nur Validierung der vorhandenen Daten
            else:
                seen_types = set()
                for detail in value:
                    offer_type = detail.get('offer_type')
                    if offer_type not in {'basic', 'standard', 'premium'}:
                        raise serializers.ValidationError(f"Ungültiger Typ: {offer_type}")
                    if offer_type in seen_types:
                        raise serializers.ValidationError(f"Doppelter Typ: {offer_type}")
                    seen_types.add(offer_type)
            
            return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        with transaction.atomic():
            offer = Offer.objects.create(**validated_data)
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)
            return offer
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details')
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if details_data is not None:
                instance.details.all().delete()
                for detail_data in details_data:
                    OfferDetail.objects.create(offer=instance, **detail_data)
            return instance
