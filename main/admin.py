from django.contrib import admin

# Register your models here.
from .models import Category, Product, CartProduct, Cart, Order, Customer

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)


class CartProductInLine(admin.TabularInline):
    model = CartProduct
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ("id", "customer", "phone", "address", "status", "buying_type", "order_date", "created_at")
    fields = ("id", "customer", "phone", "address", "status", "buying_type", "comment", "created_at", "cart")
    readonly_fields = ("id", "customer", "phone", "address", "buying_type", "comment", "created_at")
    list_filter = ['status']
    list_editable = ['status', 'order_date']
    inlines = (CartProductInLine,)

