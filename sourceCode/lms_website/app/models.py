from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):  # ✅ Kế thừa từ AbstractUser
    avatar = models.ImageField(upload_to="images/", null=True, blank=True)
    created_at = models.DateField(default=now)  # Ngày tạo tài khoản mặc định là ngày hiện tại
    updated_at = models.DateField(auto_now=True)  # Cập nhật tự động

    def __str__(self):
        return self.username

# Courses Model
class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images/")
    userList = models.JSONField(default=list)
    videosList = models.JSONField(default=list)  # Sửa lỗi thiếu giá trị mặc định
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Giá mặc định là 0.00
    birthDate = models.DateField(default=now)  # Ngày sinh mặc định là ngày hiện tại
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)  # Cập nhật tự động

    def __str__(self):
        return self.name

# Videos Model
class Videos(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    video = models.URLField()
    image = models.ImageField(upload_to="images/")
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)  # Cập nhật tự động

    def __str__(self):
        return self.name
