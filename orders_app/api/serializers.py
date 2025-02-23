from django.db import transaction, models
from rest_framework import serializers
from django.contrib.auth import get_user_model

from orders_app.models import Order, Review
from offers_app.models import OfferDetail

User = get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all(), write_only=True)
    customer_user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id']
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'created_at', 'updated_at']
        write_only_fields = ['offer_detail_id']
        
    def create(self, validated_data):
        """
        Create a new order by populating fields from the offer details.
        """
        offer = validated_data.pop('offer_detail_id')
        validated_data.update({
            'title': offer.title,
            'revisions': offer.revisions,
            'delivery_time_in_days': offer.delivery_time_in_days,
            'price': offer.price,
            'features': offer.features,
            'offer_type': offer.offer_type,
            'business_user': offer.offer.user.id
        })
        return super().create(validated_data)
    
class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    rating = serializers.DecimalField(
        max_digits=3,
        decimal_places=1,
        coerce_to_string=False
    )

    class Meta:
        model = Review
        fields = ['id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Ensure that the current user has not already submitted a review for the specified business user.
        """
        request = self.context.get('request')
        if request and request.method == 'POST':
            reviewer = request.user
            business_user = data.get('business_user')
            if Review.objects.filter(reviewer=reviewer, business_user=business_user).exists():
                raise serializers.ValidationError("You have already submitted a review for this business user.")
        return data

    def create(self, validated_data):
        """
        Automatically assign the current user as the reviewer.
        """
        reviewer = self.context['request'].user
        validated_data['reviewer'] = reviewer
        return super().create(validated_data)