"""
URL configuration for lms_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.start_view, name="start"),
    
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("home/", views.home_view, name="home"),
    path("allcources/", views.allcources_view, name="allcources"),
    path("todo/", views.todo_view, name="todo"),
    path("account/", views.account_view, name="account"),
]
