from django.contrib import admin

from .models import Product, CartItem, Order, OrderItem,Cart,Contact
# Register your models here.



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    search_fields = ('name',)
    list_filter = ('price',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'subtotal')
    search_fields = ('product__name',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'subtotal')
    search_fields = ('product__name', 'order__user__username')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_id', 'created_at')
    search_fields = ('user__username', 'session_id')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'payment_status')
    


   


@admin.register(Contact)
class CustomContact(admin.ModelAdmin):
    list_display=('name','email')