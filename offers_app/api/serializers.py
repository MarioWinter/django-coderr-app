from django.db import transaction, models
from rest_framework import serializers
from rest_framework.reverse import reverse
from offers_app.models import Offer, OfferDetail
from user_auth_app.api.serializers import UserSerializer


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail model.
    """
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for the Offer model.
    The field 'details' is used for both input and output.
    On write operations, it accepts a list of detail objects.
    On read operations, the output is transformed (z.B. to only show URLs).
    """
    details = OfferDetailSerializer(many=True)
    user_details = UserSerializer(source='user', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    min_price = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2, coerce_to_string=False)
    min_delivery_time = serializers.IntegerField(read_only=True)
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        
    def to_representation(self, instance):
        """
        Overrides output representation.
        For GET requests: returns full response with extra aggregated fields and details as URLs.
        For POST and PATCH requests: returns a simplified response with only id, title, image, description, and nested details.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        view = self.context.get('view')
        if request:
            if request.method == 'GET':
                if view and getattr(view, 'action', None) == 'retrieve':
                    representation = {
                        'id': representation.get('id'),
                        'user': representation.get('user'),
                        'title': representation.get('title'),
                        'image': representation.get('image'),
                        'description': representation.get('description'),
                        'created_at': representation.get('created_at'),
                        'updated_at': representation.get('updated_at'),
                        'details': [
                            {
                                'id': detail.id,
                                'url': reverse('offerdetails-detail', kwargs={'pk': detail.id}, request=request)
                            }
                            for detail in instance.details.all()
                        ],
                        'min_price': representation.get('min_price'),
                        'min_delivery_time': representation.get('min_delivery_time')
                    }
                else:
                    representation['details'] = [
                    {
                        'id': detail.id,
                        'url': reverse('offerdetails-detail', kwargs={'pk': detail.id}, request=request)
                    }
                    for detail in instance.details.all()
                ]
            elif request.method == 'POST' or request.method == 'PATCH':
                representation = {
                    'id': representation.get('id'),
                    'title': representation.get('title'),
                    'image': representation.get('image'),
                    'description': representation.get('description'),
                    'details': representation.get('details')
                }
        return representation
                    
    def validate_details(self, value):
        """
        Validates that the details list contains exactly three unique offer types on POST requests.
        """
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
        """
        Creates an offer along with its details and calculates aggregated fields.
        """
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
        """
        Updates an offer and its details, recalculates aggregated fields, and ensures that no extra fields are provided.
        """
        extra_fields = set(self.initial_data.keys()) - set(self.fields.keys())
        if extra_fields:
            raise serializers.ValidationError({"detail": f"Extra fields not allowed: {', '.join(extra_fields)}"})
        
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
   