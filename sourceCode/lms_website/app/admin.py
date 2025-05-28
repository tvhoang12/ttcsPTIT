from django.contrib import admin
from .models import User
from .models import Course
from .models import Contact
from .models import Lesson
from .models import Enrollment
from .models import TeachingAssignment, CourseCategory, Blog, Question

# Register your models here.
admin.site.register(User)
admin.site.register(Course)
admin.site.register(Contact)
admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(TeachingAssignment)
admin.site.register(CourseCategory)
admin.site.register(Blog)
admin.site.register(Question)
