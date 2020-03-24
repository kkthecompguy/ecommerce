from django.urls import path
from . import views

from django_filters.views import FilterView
from .models import Item

app_name = 'core'
urlpatterns = [
    path('', views.HomeView.as_view(), name='index'),
    path('product/<str:pk>/', views.product, name='product'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<str:pk>/', views.add_to_cart, name='add-to-cart'),
    path('add-coupon/', views.AddCoupon.as_view(), name='add-coupon'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('remove-from-cart/<str:pk>/',
         views.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<str:pk>/',
         views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('payment/<str:payment_option>/',
         views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RequestFundView.as_view(), name='request-refund'),
    path('register/', views.RegisterView.as_view(), name='register'),
    #     path('acc/login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('product/',
         FilterView.as_view(model=Item,                                               filterset_fields=['name', 'category']), name='product-filter'),
]
