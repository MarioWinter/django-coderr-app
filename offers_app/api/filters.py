import django_filters
from offers_app.models import Offer

class OfferFilter(django_filters.FilterSet):
    """
    FilterSet for filtering offers based on creator, price, and delivery time.
    """
    creator_id = django_filters.NumberFilter(field_name='user__id', lookup_expr='exact')
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    max_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte')
    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']