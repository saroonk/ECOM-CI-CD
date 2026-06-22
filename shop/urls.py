from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    # path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),


    path('buy-now/<int:product_id>/', views.buy_now, name='buy_now'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('order-success/', views.payment_success_page, name='payment_success_page'),


    # path('updatequantity',views.updatequantity,name="updatequantity"),

    path('update-cart/', views.update_cart_quantity, name='update_cart_quantity'),



    path('contact/',views.contact,name ='contact')

]