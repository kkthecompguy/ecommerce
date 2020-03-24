from django.contrib import admin
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'recieved',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'coupon'
    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'recieved',
        'refund_requested',
        'refund_granted'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'street_address',
        'apparment_address',
        'country',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = [
        'default',
        'address_type',
        'country'
    ]
    search_fields = [
        'user__username',
        'street_address',
        'apparment_address',
        'zip'
    ]


# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)

admin.site.index_title = 'Get the best products form the best retailers. #1 stop shop'
admin.site.site_title = 'Allsafe Shop Limited'
admin.site.site_header = 'Ecommerce Management System'
