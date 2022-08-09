from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import *

urlpatterns = [
   path('cart/', CartView.as_view(), name='cart'),
   path('change-qty/<str:slug>/', ChangeQTYView.as_view(), name='change_qty'),
   path('add-to-cart/<str:slug>/', AddToCartView.as_view(), name='add_to_cart'),
   path('remove-from-cart/<str:slug>/', DeleteFromCartView.as_view(), name='remove_from_cart'),
   path('checkout', CheckoutView.as_view(), name='checkout'),
   path('make-order/', MakeOrderView.as_view(), name='make_order'),
   path('profile/', ProfileView.as_view(), name='profile'),
   path('', MainView.as_view(), name='main'),
   path('login/', LoginView.as_view(), name='login'),
   path('registration/', RegisterUserView.as_view(), name='registration'),
   path('logout/', LogoutView.as_view(next_page="/"), name='logout'),
   path('<str:slug>/', ProductList.as_view(), name='category'),
   path('products/<str:slug>/', ProductDetailView.as_view(), name='product_detail'),
]

