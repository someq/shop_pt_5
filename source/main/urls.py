"""hello URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from webapp.views import IndexView, ProductView, ProductCreateView, \
    ProductUpdateView, ProductDeleteView, CartView, CartAddView, \
    CartDeleteView, CartDeleteOneView, OrderCreateView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),

    path('', IndexView.as_view(), name='index'),
    path('product/<int:pk>/', ProductView.as_view(), name='product_view'),
    path('products/add/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    path('cart/', CartView.as_view(), name='cart_view'),
    path('product/<int:pk>/add-to-cart/', CartAddView.as_view(), name='product_add_to_cart'),
    path('cart/<int:pk>/delete/', CartDeleteView.as_view(), name='cart_delete'),
    path('cart/<int:pk>/delete-one/', CartDeleteOneView.as_view(), name='cart_delete_one'),
    path('order/create/', OrderCreateView.as_view(), name='order_create'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
