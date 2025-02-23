from django.contrib import admin
from offers_app.models import Offer, OfferDetail

class OfferDetailInline(admin.TabularInline):
    """
    Inline admin descriptor for OfferDetail model.
    Displays OfferDetail objects in a tabular inline inside the Offer admin page.
    """
    model = OfferDetail
    extra = 0  # No extra empty forms
    readonly_fields = ('id',)

class OfferAdmin(admin.ModelAdmin):
    """
    Admin configuration for Offer model.
    """
    list_display = ('id', 'title', 'user', 'min_price', 'min_delivery_time', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at', 'user')
    ordering = ('-updated_at',)
    inlines = [OfferDetailInline]  # Include details inline

class OfferDetailAdmin(admin.ModelAdmin):
    """
    Admin configuration for OfferDetail model.
    """
    list_display = ('id', 'offer', 'title', 'offer_type', 'price', 'delivery_time_in_days', 'revisions')
    list_filter = ('offer_type', 'offer')
    search_fields = ('title', 'offer__title')
    ordering = ('id',)

admin.site.register(Offer, OfferAdmin)
admin.site.register(OfferDetail, OfferDetailAdmin)