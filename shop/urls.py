from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Cart-related URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/guest-checkout/', views.guest_checkout, name='guest_checkout'),
    path('cart/create-order/', views.create_order, name='create_order'),
    
    # Order-related URLs
    path('order/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    
    # Product URLs
    path('search/', views.search_products, name='search_products'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('', views.product_list, name='product_list'),
]
