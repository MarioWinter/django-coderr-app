from django.contrib import admin
from orders_app.models import Order, Review

class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model.
    """
    list_display = ('id', 'title', 'customer_user', 'business_user', 'price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title',)
    ordering = ('-created_at',)

class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for Review model.
    """
    list_display = ('id', 'business_user', 'reviewer', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('reviewer__username', 'business_user__username')
    ordering = ('-created_at',)

admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
