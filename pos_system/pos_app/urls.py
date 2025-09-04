from django.urls import path
from . import views

app_name = 'pos_app'

urlpatterns = [  

    path('', views.index, name='index'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'), 
    path('checkout/', views.checkout, name='checkout'),
    path('update_cart_quantity/', views.update_cart_quantity, name='update_cart_quantity'),
]
