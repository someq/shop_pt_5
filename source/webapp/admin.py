from django.contrib import admin
from .models import Product, Cart, Order, OrderProduct


class ProductAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    list_display = ('pk', 'name', 'amount', 'price')
    list_display_links = ('pk', 'name')
    search_fields = ('name',)


# Бонус
class OrderProductAdmin(admin.TabularInline):
    model = OrderProduct
    fields = ('product', 'qty')
    extra = 0


# Бонус
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'phone', 'created_at')
    list_display_links = ('pk', 'name')
    ordering = ('-created_at',)
    inlines = (OrderProductAdmin,)


admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
