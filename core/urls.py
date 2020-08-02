from django.urls import path, re_path
from .views import (
    CheckoutView,
    HomeView,
    OrderSummaryView,
    ItemDetailView,
    add_to_cart,
    AddCouponView,
    remove_from_cart,
    minus_item_from_cart,
    toggle_pre_delete_item_from_cart,
    PaymentView,
    RequestRefundView,
)
app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('order-summary', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('add-coupon', AddCouponView.as_view(), name='add-coupon'),
    path('request-refund', RequestRefundView.as_view(), name='request-refund'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('minus-item-from-cart/<slug>',
         minus_item_from_cart, name='minus-item-from-cart'),
    path('toggle-pre-delete-item-from-cart/<slug>',
         toggle_pre_delete_item_from_cart, name='toggle-pre-delete-item-from-cart'),
]
