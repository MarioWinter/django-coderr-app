from django.db import transaction, models
from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from user_auth_app.api.serializers import UserSerializer



class OfferDetailSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
    user_details = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    min_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    min_delivery_time = serializers.IntegerField(read_only=True)
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']

    def validate_details(self, value):
            
            if self.context['request'].method == 'POST':
                if len(value) != 3:
                    raise serializers.ValidationError("Es sind 3 Angebotsdetails erforderlich.")
                
                types = {detail['offer_type'] for detail in value}
                if types != {'basic', 'standard', 'premium'}:
                    raise serializers.ValidationError("Alle drei Typen müssen vorhanden sein.")
            
            
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
            agg = offer.details.aggregate(
                min_price=models.Min('price'),
                min_delivery_time=models.Min('delivery_time_in_days')
            )
            offer.min_price = agg['min_price']
            offer.min_delivery_time = agg['min_delivery_time']
            offer.save(update_fields=['min_price', 'min_delivery_time'])
            return offer
    
    def update(self, instance, validated_data):
            details_data = validated_data.pop('details', None)
            
            with transaction.atomic():
                instance = super().update(instance, validated_data)
                
                if details_data is not None:
                    for detail_data in details_data:
                        offer_type = detail_data['offer_type']
                        try:
                            detail = instance.details.get(offer_type=offer_type)
                            for key, value in detail_data.items():
                                setattr(detail, key, value)
                            detail.save()
                        except OfferDetail.DoesNotExist:
                            raise serializers.ValidationError(
                                f"Detail mit Typ {offer_type} existiert nicht"
                            )
                agg = instance.details.aggregate(
                    min_price=models.Min('price'),
                    min_delivery_time=models.Min('delivery_time_in_days')
                )
                instance.min_price = agg['min_price']
                instance.min_delivery_time = agg['min_delivery_time']
                instance.save(update_fields=['min_price', 'min_delivery_time'])
                return instance
   