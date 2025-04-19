from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    avatar = models.ImageField(upload_to="images/", null=True, blank=True)
    joined_courses = models.JSONField(default=list)  # Danh sách khóa học của người dùng
    # Danh sách video đã xem của người dùng
    videos = models.JSONField(default=list)  # Danh sách video đã xem của người dùng
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.username

# Courses Model
class Courses(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    # lấy id tác giả từ bảng Users
    author = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="courses", null=True, blank=True)
    thumbnail = models.ImageField(upload_to="images/", null=True, blank=True)
    userList = models.JSONField(default=list)
    videosList = models.JSONField(default=list)  # Sửa lỗi thiếu giá trị mặc định
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Giá mặc định là 0.00
    duration = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Thời gian mặc định là 0.00
    level = models.CharField(max_length=50, default="Beginner")  # Mức độ mặc định là "Beginner"
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)  # Đánh giá mặc định là 0.00
    rating = models.IntegerField(default=0)  # Số lượng đánh giá mặc định là 0
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

# Videos Model
class Videos(models.Model):
    id = models.AutoField(primary_key=True)
    incourse = models.ForeignKey(Courses, on_delete=models.CASCADE, related_name="videos", default=1)
    name = models.CharField(max_length=100)
    description = models.TextField()
    video = models.URLField(null=True, blank=True)  # URL video YouTube
    thumbnail = models.ImageField(upload_to="images/", null=True, blank=True)
    videoUp = models.FileField(upload_to="videos/", null=True, blank=True)
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)  # Cập nhật tự động

    def get_embed_url(self):
        """
        Chuyển đổi URL YouTube thành dạng nhúng (embed).
        """
        if "watch?v=" in self.video:
            return self.video.replace("watch?v=", "embed/")
        return self.video  # Nếu đã là embed link thì giữ nguyên

    def __str__(self):
        return self.name

class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    thumbnail = models.ImageField(upload_to="images/", null=True, blank=True)
    author = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)
    created_at = models.DateField(default=now)
    updated_at = models.DateField(auto_now=True)  # Cập nhật tự động

    def __str__(self):
        return self.title
 
def get_course_with_author(course_id):
    course = get_object_or_404(Courses, id=course_id)
    author = get_object_or_404(Users, id=course.author_id)  # Lấy thông tin tác giả
    course.authorname = f"{author.first_name} {author.last_name}"  # Gán tên tác giả vào course
    return course





