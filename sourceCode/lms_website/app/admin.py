from django.contrib import admin
from .models import Users, Courses, Videos, Posts

# Hiển thị chi tiết Users trong admin
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "created_at")  # Cột hiển thị
    search_fields = ("first_name", "last_name", "email")  # Cho phép tìm kiếm
    list_filter = ("created_at",)  # Bộ lọc
    ordering = ("id",)  # Sắp xếp theo ID

# Hiển thị Courses trong admin
@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")  
    search_fields = ("name",)  
    list_filter = ("created_at",)

# Hiển thị Videos trong admin
@admin.register(Videos)
class VideosAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")  
    search_fields = ("name",)  
    list_filter = ("created_at",)

# Hiển thị Posts trong admin
@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")  
    search_fields = ("title",)  
    list_filter = ("created_at",)
    ordering = ("id",)
