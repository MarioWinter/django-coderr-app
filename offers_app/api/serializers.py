from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from user_auth_app.api.serializers import UserSerializer



class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Es sind 3 Angebotsdetails (basic, standard, premium) sind erforderlich.")
        types = [detail['offer_type'] for detail in value]
        if set(types) != {'basic', 'standard', 'premium'}:
            raise serializers.ValidationError("Die Angebotsdetails müssen genau einen 'basic', 'standard' und 'premium'-Typ enthalten.")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
