"""exchange URL Configuration

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
from django.contrib import admin
from django.urls import path,re_path
from django.conf.urls import url
from app.views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name="home"),
    path('signup/', signup_view, name="signup"),
    path('logout/', auth_views.LogoutView.as_view(template_name='home.html'), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name="login"),
    path('balance/', balance_view, name="balance"),
    path('bookorder/', book_order_view, name="bookorder"),
    path('placeneworder/', place_new_order_view, name="placeneworder"),
    path('cancel_order/<int:pk>/', cancel_order_view, name="cancel_order"),
    re_path("place_order/", place_order_request_view, name="place_order"),
    path("createdata", createdata, name="createdata"),

]
