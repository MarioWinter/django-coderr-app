from django.db import transaction, models
from rest_framework import serializers

from orders_app.models import Order
from offers_app.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all(),source='offer_detail_id', write_only=True)
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user' 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'customer_user', 'business_user' 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']
        
    def create(self, validated_data):
        offer = validated_data.pop('offer_detail')
        validated_data.update({
            'title': offer.title,
            'revisions': offer.revisions,
            'delivery_time_in_days': offer.delivery_time_in_days,
            'price': offer.price,
            'features': offer.features,
            'offer_type': offer.offer_type,
            'busines_user': self.context['request'].user.id
        })
        return super().create(validated_data)
    