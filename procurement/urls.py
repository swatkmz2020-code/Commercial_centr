from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.index, name='index'),
    path('orders/', views.orders_list, name='orders'),
    path('search/', views.product_search, name='search'),
    path('analysis/', views.price_analysis, name='analysis'),
]

