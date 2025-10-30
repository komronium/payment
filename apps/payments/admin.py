from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product_name', 'id')
    date_hierarchy = 'created_at'
    list_per_page = 25
    ordering = ('-id',)
    readonly_fields = ('created_at',)
    list_editable = ('status',)

    actions = ['mark_as_paid', 'mark_as_cancelled']

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(status='paid')
        self.message_user(request, f'Marked {updated} orders as paid.')
    mark_as_paid.short_description = 'Mark selected orders as paid'

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'Marked {updated} orders as cancelled.')
    mark_as_cancelled.short_description = 'Mark selected orders as cancelled'
