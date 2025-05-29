from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings

class User(AbstractUser):
    id = models.AutoField(primary_key=True)  # Tự động tăng ID cho người dùng
    email = models.EmailField(unique=True, max_length=254, blank=True)  # Override email thành unique

    phone = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    # Vai trò của người dùng (student, instructor, admin)
    ROLE_CHOICES = [
        ('student', 'student'),
        ('instructor', 'instructor'),
        ('admin', 'admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    self_description = RichTextUploadingField(default="", blank=True, null=True)  # Mô tả bản thân viết bằng Markdown
    # Các khóa học đã tham gia (không có quyền chỉnh sửa nội dung)
    enrolled_courses = models.ManyToManyField(
        "app.Course",
        through="app.Enrollment",
        related_name="enrolled_students",
        verbose_name="Course",
        blank=True
    )

    # Các khóa học đã tạo (giảng viên)
    instructors = models.ManyToManyField(
        "app.Course",
        through="app.TeachingAssignment",
        related_name="instructed_courses",
        blank=True
    )

    def __str__(self):
        return self.username

# Khóa học
class Course(models.Model):
    courseID = models.AutoField(primary_key=True)  # Tự động tăng ID cho khóa học
    courseName = models.CharField(max_length=1000) # Tên khóa học
    thumbnail = models.ImageField(upload_to='thumbnails/', default="thumbnails/default-product-card.webp", null=True, blank=True)  # Thumbnail ảnh cho course
    
    description = models.TextField()  # Mô tả khóa học
    duration = models.CharField(max_length=100)  # Thời gian khóa học
    
    created_at = models.DateTimeField(auto_now_add=True)  # Ngày giờ khóa học được tạo
    level = models.CharField(max_length=50)  # Cấp độ khóa học (beginner, intermediate, advanced)
    language = models.CharField(max_length=50)  # Ngôn ngữ khóa học
    # Thay đổi ở đây: dùng ForeignKey thay cho CharField
    
    register_count = models.IntegerField(default=0)  # Số lượng người đăng ký khóa học
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5)  # Đánh giá khóa học (0-5)
    
    
    created_by = models.ForeignKey(
        "app.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_courses"
    )
    categories = models.ManyToManyField("app.CourseCategory", related_name="courses", blank=True)

    def __str__(self):
        return self.courseName

# Lesson khóa học (code HTML nhúng YouTube)
class Lesson(models.Model):
    THEORY = 'theory'
    QUESTION = 'question'
    LESSON_TYPE_CHOICES = [
        (THEORY, 'Lý thuyết'),
        (QUESTION, 'Câu hỏi'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    chapter = models.ForeignKey('Chapter', on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    title = models.CharField(max_length=100)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default=THEORY)
    # Lý thuyết
    youtube_url = models.URLField(blank=True, null=True)  # URL YouTube cho lesson lý thuyết
    embed_code = models.TextField(blank=True, null=True)  # HTML iframe hoặc mã nhúng YouTube
    # Câu hỏi
    question_list_title = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Chapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Chương {self.order}: {self.title}"

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=500)
    answer_a = models.CharField(max_length=200)
    answer_b = models.CharField(max_length=200)
    answer_c = models.CharField(max_length=200)
    answer_d = models.CharField(max_length=200)
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')]
    )

    def __str__(self):
        return self.question_text

# Liên hệ
class Contact(models.Model):
    userName = models.CharField(max_length=40)
    phoneNumber = models.CharField(max_length=20)
    emailAddress = models.CharField(max_length=40)

    # Các trường mở rộng
    address = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, null=True, blank=True)

    # Mã nhúng iframe
    facebook_iframe_code = models.TextField(null=True, blank=True)
    google_map_iframe_code = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.userName
    
class Enrollment(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    course = models.ForeignKey("app.Course", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)  # Thời điểm đăng ký
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # % tiến độ học

    class Meta:
        unique_together = ("user", "course")  # Mỗi user chỉ đăng ký 1 lần

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.courseName}"
# Giảng viên
# (người tạo khóa học)
class TeachingAssignment(models.Model):
    user = models.ForeignKey("app.User", on_delete=models.CASCADE)
    course = models.ForeignKey("app.Course", on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} teaches {self.course.courseName}"

class CourseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextUploadingField() # Nội dung bài viết viết bằng Markdown # Hình ảnh bài viết
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey("app.User", on_delete=models.CASCADE, related_name="blogs")
    views = models.PositiveIntegerField(default=0)  # Số lượt xem bài viết
    
    def __str__(self):
        return self.title

class BlogComment(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.blog}'