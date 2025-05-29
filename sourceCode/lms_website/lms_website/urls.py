"""CS361_G3_app URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.start_view, name="start"),
    path("home/", views.start_view, name="home"),
    #authentication
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('verify_email/', views.verify_email, name='verify_email'),
    path('resend_verification_code/', views.resend_verification_code, name='resend_verification_code'),
    path('clear_signup_session/', views.clear_signup_session, name='clear_signup_session'),
    
    path("profile/", views.profile_view, name="profile"),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    #blog
    path("about/", views.about_view, name="about"),
    path("blog/", views.blog_view, name="blog"),
    path("blog/<int:blog_id>/", views.blog_detail_view, name="blog_detail"),
    path('blog/new/', views.new_blog_view, name='new_blog'),
    path('blog/search/', views.blog_search_ajax, name='blog_search_ajax'),
    #courses
    path("courses/", views.course_view, name="courses"),
    path("contact/<int:userID>", views.contact_view, name="contact"),
    path("courses/<int:courseID>/", views.course_inner_view, name="course_detail"),
    path("courses/<int:courseID>/lesson/<int:lesson_id>/", views.lesson_view, name="lesson"),
    path('courses/<int:courseID>/enroll/', views.enroll_course_view, name='enroll_course'),
    path('courses/create/', views.create_course_view, name='create_course'),
    path("courses/<int:courseID>/edit/", views.edit_course_view, name="edit_course"),
    path("courses/<int:courseID>/delete/", views.delete_course_view, name="delete_course"),
    path('courses/<int:courseID>/study/', views.study_course, name='study_course'),
    #categories
    path('categories/search/', views.category_search_ajax, name='category_search_ajax'),
    path('courses/search/', views.course_search_ajax, name='course_search_ajax'),

    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)