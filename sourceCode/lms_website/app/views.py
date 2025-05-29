from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Question, User, Course, Lesson, Contact, Enrollment, CourseCategory, Blog, BlogComment, Chapter
from django.db.models import Count
from .forms import CourseForm, BlogForm, ProfileForm, BlogCommentForm  # Sẽ tạo ở bước 2
from django.core.paginator import Paginator
import re
from django.db import transaction
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.utils import timezone

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kiểm tra tài khoản trong hệ thống
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("start")  # Điều hướng đến trang chính sau khi đăng nhập thành công
        else:
            messages.error(request, "Invalid username or password")  # Hiển thị lỗi nếu đăng nhập sai
            return redirect("login")  # Quay lại trang đăng nhập
    else:
        return render(request, "app/login.html")

def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST.get('role')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'app/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'app/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'app/signup.html')

        # Tạo mã xác nhận và lưu vào session
        verification_code = str(random.randint(100000, 999999))
        request.session['signup_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'email': email,
            'password': password,
            'role': role,
            'verification_code': verification_code,
        }

        # Gửi email xác nhận
        send_mail(
            subject="Your Verification Code",
            message=f"Your verification code is: {verification_code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        messages.info(request, "A verification code has been sent to your email. Please enter it to complete registration.")
        return redirect('signup')  # Tạo view & template verify_email.html để nhập mã

    return render(request, 'app/signup.html')

def start_view(request):
    popular_courses = Course.objects.order_by('-rating', '-register_count')[:6]
    if hasattr(Blog, 'views'):
        popular_blogs = Blog.objects.order_by('-views')[:3]
    else:
        popular_blogs = Blog.objects.order_by('-created_at')[:3]
    return render(request, "app/index.html", {
        "popular_courses": popular_courses,
        "popular_blogs": popular_blogs
    })

def blog_view(request):
    # Lấy tất cả bài viết, sắp xếp mới nhất trước
    blogs = Blog.objects.order_by('-created_at')
    # 3 bài viết mới nhất
    latest_blogs = Blog.objects.order_by('-created_at')[:3]
    # 3 bài viết nổi bật nhất (nếu có trường 'views', nếu không thì lấy 3 bài đầu)
    if hasattr(Blog, 'views'):
        popular_blogs = Blog.objects.order_by('-views')[:3]
    else:
        popular_blogs = blogs[:3]
    return render(request, "app/blog.html", {
        "blogs": blogs,
        "latest_blogs": latest_blogs,
        "popular_blogs": popular_blogs,
    })

def about_view(request):
    return render(request, "app/about.html")

def contact_view(request):
    # dùng model qu
    return render(request, "app/practice.html")

def course_view(request):
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', 'newest')
    courses = Course.objects.all()

    if category_id:
        courses = courses.filter(categories__id=category_id)

    # Annotate số lượng đăng ký
    courses = courses.annotate(enroll_count=Count('enrollment'))

    # Sắp xếp theo lựa chọn
    if sort == "newest":
        courses = courses.order_by('-created_at')
    elif sort == "oldest":
        courses = courses.order_by('created_at')
    elif sort == "az":
        courses = courses.order_by('courseName')
    elif sort == "za":
        courses = courses.order_by('-courseName')
    elif sort == "enroll_desc":
        courses = courses.order_by('-enroll_count')
    elif sort == "enroll_asc":
        courses = courses.order_by('enroll_count')

    categories = CourseCategory.objects.all()
    paginator = Paginator(courses, 10)  # 10 courses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    print("Total courses:", courses.count())
    return render(request, "app/course.html", {
        "categories": categories,
        "page_obj": page_obj,
    })

def course_inner_view(request, courseID):
    course = Course.objects.get(courseID=courseID)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    return render(request, "app/course-inner.html", {
        "course": course,
        "is_enrolled": is_enrolled,
    })

def lesson_view(request, courseID, lesson_id):
    course = get_object_or_404(Course, courseID=courseID)
    lesson = get_object_or_404(Lesson, lessonID=lesson_id, course=course)
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    # Chuyển hướng template theo loại bài học
    if lesson.lesson_type == Lesson.QUESTION:
        return render(request, "app/question.html", {
            "course": course,
            "lesson": lesson,
            "is_enrolled": is_enrolled,
        })
    else:
        return render(request, "app/video.html", {
            "course": course,
            "lesson": lesson,
            "is_enrolled": is_enrolled,
        })

def blog_comment_view(request, courseID, lesson_id):
    if request.method == "POST":
        comment = request.POST.get("comment")
        lesson = Lesson.objects.get(lessonID=lesson_id)
        lesson.comments.create(comment=comment, user=request.user)  # Giả sử bạn có một model Comment liên kết với Lesson
        return redirect("lesson", courseID=courseID, lesson_id=lesson_id)
    return redirect("lesson", courseID=courseID, lesson_id=lesson_id)

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            if not user.check_password(old_password):
                return JsonResponse({'status': 'error', 'message': 'Mật khẩu cũ không đúng.'}, status=400)
            # Tạo mã xác nhận và lưu vào session
            verification_code = str(random.randint(100000, 999999))
            request.session['change_password_code'] = verification_code
            request.session['change_password_new'] = new_password
            request.session['change_password_time'] = timezone.now().isoformat()
            # Gửi email mã xác nhận
            send_mail(
                subject="Xác nhận đổi mật khẩu LMS",
                message=f"Mã xác nhận đổi mật khẩu của bạn là: {verification_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return JsonResponse({'status': 'ok', 'message': 'Mã xác nhận đã được gửi tới email của bạn.'})
        elif action == 'verify_password_code':
            code = request.POST.get('verify_code')
            session_code = request.session.get('change_password_code')
            new_password = request.session.get('change_password_new')
            code_time = request.session.get('change_password_time')
            if not (session_code and new_password and code_time):
                return JsonResponse({'status': 'error', 'message': 'Phiên xác nhận không hợp lệ.'}, status=400)
            # Kiểm tra mã và thời gian (5 phút)
            if code != session_code:
                return JsonResponse({'status': 'error', 'message': 'Mã xác nhận không đúng.'}, status=400)
            from datetime import datetime, timedelta
            code_time = datetime.fromisoformat(code_time)
            if timezone.now() - code_time > timedelta(minutes=5):
                return JsonResponse({'status': 'error', 'message': 'Mã xác nhận đã hết hạn.'}, status=400)
            # Đổi mật khẩu
            user.set_password(new_password)
            user.save()
            # Xóa session
            del request.session['change_password_code']
            del request.session['change_password_new']
            del request.session['change_password_time']
            return JsonResponse({'status': 'ok', 'message': 'Đổi mật khẩu thành công.'})
        else:
            # Xử lý cập nhật thông tin cá nhân
            form = ProfileForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                email = form.cleaned_data['email']
                if User.objects.exclude(pk=user.pk).filter(email=email).exists():
                    form.add_error('email', 'Email này đã được sử dụng bởi tài khoản khác.')
                else:
                    form.save()
                    messages.success(request, "Cập nhật thông tin thành công.")
                    return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'app/profile.html', {'form': form, 'user': user})

@login_required
def my_courses_view(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    created_courses = list(Course.objects.filter(created_by=request.user))

    # Annotate số lượng học viên cho mỗi course
    all_courses = enrolled_courses + created_courses
    courses_with_count = Course.objects.filter(pk__in=[c.pk for c in all_courses]).annotate(student_count=Count('enrollment'))

    # Tạo dict id->course để lấy đúng số lượng học viên cho từng course
    course_dict = {c.pk: c for c in courses_with_count}
    enrolled_courses = [course_dict[c.pk] for c in enrolled_courses if c.pk in course_dict]
    created_courses = [course_dict[c.pk] for c in created_courses if c.pk in course_dict]

    return render(request, "app/my_courses.html", {
        "enrolled_courses": enrolled_courses,
        "created_courses": created_courses,
    })

def logout_view(request):
    logout(request)
    # messages.success(request, "Logged out successfully.")
    return redirect("home")

@login_required
def enroll_course_view(request, courseID):
    course = get_object_or_404(Course, courseID=courseID)
    user = request.user

    # Kiểm tra đã đăng ký chưa
    if Enrollment.objects.filter(user=user, course=course).exists():
        messages.info(request, "Bạn đã đăng ký khóa học này rồi.")
        return redirect('course_detail', courseID=courseID)

    # Đăng ký mới
    Enrollment.objects.create(user=user, course=course)
    course.register_count += 1
    course.save()
    messages.success(request, "Đăng ký khóa học thành công!")
    return redirect('course_detail', courseID=courseID)

def get_youtube_embed_code(youtube_url):
    regex = r'(?:youtube\.com.*(?:\?|&)v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, youtube_url)
    if match:
        lesson_id = match.group(1)
        return (
            '<div class="youtube-embed-responsive">'
            f'<iframe src="https://www.youtube.com/embed/{lesson_id}" '
            'frameborder="0" allowfullscreen></iframe>'
            '</div>'
        )
    return ''

def get_custom_youtube_embed(
    youtube_url,
    title="YouTube lesson player",
    autoplay=1,
    origin=None,
    extra_params=""
):
    import re
    regex = r'(?:youtube\.com.*(?:\?|&)v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, youtube_url or "")
    if match:
        lesson_id = match.group(1)
        src = f"https://www.youtube-nocookie.com/embed/{lesson_id}?theme=light&rel=0&enablejsapi=1"
        if origin:
            src += f"&origin={origin}"
        if autoplay:
            src += "&autoplay=1"
        if extra_params:
            src += f"&{extra_params.lstrip('&')}"
        return (
            f'<iframe '
            f'width="100%" height="100%" '
            f'src="{src}" '
            f'title="{title}" '
            f'frameborder="0" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
            f'referrerpolicy="strict-origin-when-cross-origin" '
            f'allowfullscreen="true" '
            f'enablejsapi="1"'
            f'></iframe>'
        )
    return ''

@login_required
def new_blog_view(request):
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()
            return redirect('blog')  # hoặc redirect tới trang chi tiết bài viết
    else:
        form = BlogForm()
    return render(request, 'app/new-blog.html', {'form': form})

def blog_detail_view(request, blog_id):
    blog = get_object_or_404(Blog, pk=blog_id)
    comments = blog.comments.filter(parent__isnull=True).order_by('-created_at')
    comment_form = BlogCommentForm()

    if request.method == 'POST':
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.blog = blog
            new_comment.user = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent_comment = BlogComment.objects.get(id=parent_id, blog=blog)
                    new_comment.parent = parent_comment
                except BlogComment.DoesNotExist:
                    pass
            new_comment.save()
            return redirect('blog_detail', blog_id=blog.id)

    return render(request, 'app/post.html', {
        'blog': blog,
        'comments': comments,
        'comment_form': comment_form,
    })

@login_required
def delete_course_view(request, courseID):
    course = get_object_or_404(Course, courseID=courseID)
    # Kiểm tra quyền xóa
    if request.user != course.created_by:
        messages.error(request, "You are not authorized to delete this course.")
        return redirect("my_courses")
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully.")
        return redirect("my_courses")
    return render(request, "app/confirm_delete_course.html", {"course": course})

def category_search_ajax(request):
    q = request.GET.get('q', '')
    categories = CourseCategory.objects.filter(name__icontains=q).order_by('name')
    data = [{'id': c.id, 'name': c.name} for c in categories]
    return JsonResponse({'results': data})

@login_required
def create_lesson_view(request, courseID, chapterID=None):
    course = get_object_or_404(Course, pk=courseID)
    chapter = None
    if chapterID:
        chapter = get_object_or_404(Chapter, pk=chapterID)
    if request.method == 'POST':
        title = request.POST.get('title')
        lesson_type = request.POST.get('lesson_type', Lesson.THEORY)
        youtube_url = request.POST.get('youtube_url', '')
        question_list_title = request.POST.get('question_list_title', '')

        embed_code = ''
        if lesson_type == Lesson.THEORY and youtube_url:
            # embed_code = get_youtube_embed_code(youtube_url)
            embed_code = get_custom_youtube_embed(
                        youtube_url=youtube_url,
                        width="100%",
                        height="100%",
                        extra_params="vq=hd720"
                    )

        lesson = Lesson.objects.create(
            course=course,
            chapter=chapter,
            title=title,
            lesson_type=lesson_type,
            youtube_url=youtube_url if lesson_type == Lesson.THEORY else None,
            embed_code=embed_code,
            question_list_title=question_list_title if lesson_type == Lesson.QUESTION else None,
        )
        messages.success(request, "lesson created successfully.")
        return redirect('course_detail', courseID=courseID)
    return render(request, 'app/create_course.html', {
        'course': course,
        'chapter': chapter,
    })

@login_required
def enroll_course(request, courseID):
    course = get_object_or_404(Course, pk=courseID)
    user = request.user

    # Kiểm tra đã đăng ký chưa
    if Enrollment.objects.filter(user=user, course=course).exists():
        messages.info(request, "Bạn đã đăng ký khóa học này rồi.")
        return redirect('course_detail', courseID=courseID)

    # Đăng ký mới
    Enrollment.objects.create(user=user, course=course)
    course.register_count += 1
    course.save()
    messages.success(request, "Đăng ký khóa học thành công!")
    return redirect('course_detail', courseID=courseID)
@login_required
def study_course(request, courseID):
    course = get_object_or_404(Course, pk=courseID)

    # Kiểm tra quyền truy cập: chỉ học viên đã đăng ký mới được học
    if not Enrollment.objects.filter(user=request.user, course=course).exists() and request.user != course.created_by:
        messages.error(request, "Bạn cần đăng ký khóa học để truy cập nội dung này.")
        return redirect('course_detail', courseID=courseID)

    chapters = course.chapters.prefetch_related('lessons').order_by('order')
    current_lesson = None
    current_type = None

    lesson_id = request.GET.get('lesson')
    quiz_id = request.GET.get('quiz')

    if lesson_id:
        current_lesson = get_object_or_404(Lesson, pk=lesson_id, course=course, lesson_type='theory')
        current_type = "lesson"
    elif quiz_id:
        current_lesson = get_object_or_404(Lesson, pk=quiz_id, course=course, lesson_type='question')
        current_type = "quiz"

    context = {
        'course': course,
        'chapters': chapters,
        'current_lesson': current_lesson,
        'current_type': current_type,
    }
    return render(request, 'app/study-course.html', context)

import re

def extract_youtube_id(youtube_url):
    """
    Trả về lesson ID từ một URL YouTube bất kỳ.
    """
    regex = r'(?:youtube\.com.*(?:\?|&)v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(regex, youtube_url or "")
    if match:
        return match.group(1)
    return ""

@login_required
def edit_course_view(request, courseID):
    course = get_object_or_404(Course, courseID=courseID)
    if request.user != course.created_by:
        messages.error(request, "You are not have permited to edit this course.")
        return redirect("my_courses")
    if request.method == "POST":
        # ... cập nhật trường cơ bản như cũ ...
        course.courseName = request.POST.get("courseName")
        thumbnail = request.FILES.get("thumbnail")
        if thumbnail:
            course.thumbnail = thumbnail
        course.description = request.POST.get("description")
        course.price = request.POST.get("price")
        course.duration = request.POST.get("duration")
        course.level = request.POST.get("level")
        course.language = request.POST.get("language")
        course.category = request.POST.get("category")
        # Cập nhật categories
        category_ids = request.POST.getlist("categories")
        if category_ids:
            course.categories.set(category_ids)

        # --- CHAPTER ---
        old_chapter_ids = set(course.chapters.values_list('id', flat=True))
        new_chapter_ids = set()
        chapter_num = 1
        while True:
            chapter_title = request.POST.get(f'chapter_title_{chapter_num}')
            chapter_id = request.POST.get(f'chapter_id_{chapter_num}')
            if not chapter_title:
                break
            if chapter_id:
                chapter = Chapter.objects.get(pk=chapter_id, course=course)
                chapter.title = chapter_title
                chapter.order = chapter_num
                chapter.save()
                new_chapter_ids.add(chapter.id)
            else:
                chapter = Chapter.objects.create(course=course, title=chapter_title, order=chapter_num)
                new_chapter_ids.add(chapter.id)
            # --- VIDEO ---
            old_lesson_ids = set(chapter.lessons.values_list('id', flat=True))
            new_lesson_ids = set()
            lesson_num = 1
            while True:
                lesson_title = request.POST.get(f'lesson_title_{chapter_num}_{lesson_num}')
                lesson_type = request.POST.get(f'lesson_type_{chapter_num}_{lesson_num}')
                youtube_url = request.POST.get(f'youtube_url_{chapter_num}_{lesson_num}')
                question_list_title = request.POST.get(f'question_list_title_{chapter_num}_{lesson_num}')
                lesson_id = request.POST.get(f'lesson_id_{chapter_num}_{lesson_num}')
                if not lesson_title and not question_list_title:
                    break
                embed_code = ''
                # Nếu là lý thuyết và có youtube_url thì sinh embed_code
                if lesson_type == 'theory' and youtube_url:
                    embed_code = get_custom_youtube_embed(
                        youtube_url=youtube_url,
                        extra_params="vq=hd720"
                    )
                if lesson_id:
                    lesson = Lesson.objects.get(pk=lesson_id, chapter=chapter)
                    lesson.title = lesson_title or (question_list_title or '')
                    lesson.lesson_type = lesson_type
                    lesson.youtube_url = youtube_url if lesson_type == 'theory' else None
                    lesson.embed_code = embed_code if lesson_type == 'theory' else None
                    lesson.question_list_title = question_list_title if lesson_type == 'question' else None
                    lesson.save()
                    new_lesson_ids.add(lesson.id)
                else:
                    lesson = Lesson.objects.create(
                        course=course,
                        chapter=chapter,
                        title=lesson_title or (question_list_title or ''),
                        lesson_type=lesson_type,
                        youtube_url=youtube_url if lesson_type == 'theory' else None,
                        embed_code=embed_code if lesson_type == 'theory' else None,
                        question_list_title=question_list_title if lesson_type == 'question' else None,
                    )
                    new_lesson_ids.add(lesson.id)
                # --- QUESTION ---
                if lesson_type == 'question':
                    old_question_ids = set(lesson.questions.values_list('id', flat=True))
                    new_question_ids = set()
                    question_num = 1
                    while True:
                        q_text = request.POST.get(f'question_text_{chapter_num}_{lesson_num}_{question_num}')
                        question_id = request.POST.get(f'question_id_{chapter_num}_{lesson_num}_{question_num}')
                        if not q_text:
                            break
                        answer_a = request.POST.get(f'answer_a_{chapter_num}_{lesson_num}_{question_num}')
                        answer_b = request.POST.get(f'answer_b_{chapter_num}_{lesson_num}_{question_num}')
                        answer_c = request.POST.get(f'answer_c_{chapter_num}_{lesson_num}_{question_num}')
                        answer_d = request.POST.get(f'answer_d_{chapter_num}_{lesson_num}_{question_num}')
                        correct_answer = request.POST.get(f'correct_answer_{chapter_num}_{lesson_num}_{question_num}')
                        if question_id:
                            q = Question.objects.get(pk=question_id, lesson=lesson)
                            q.question_text = q_text
                            q.answer_a = answer_a
                            q.answer_b = answer_b
                            q.answer_c = answer_c
                            q.answer_d = answer_d
                            q.correct_answer = correct_answer
                            q.save()
                            new_question_ids.add(q.id)
                        else:
                            q = Question.objects.create(
                                lesson=lesson,
                                question_text=q_text,
                                answer_a=answer_a,
                                answer_b=answer_b,
                                answer_c=answer_c,
                                answer_d=answer_d,
                                correct_answer=correct_answer,
                            )
                            new_question_ids.add(q.id)
                        question_num += 1
                    # XÓA QUESTION KHÔNG CÒN
                    for qid in old_question_ids - new_question_ids:
                        Question.objects.filter(pk=qid).delete()
                lesson_num += 1
            # XÓA VIDEO KHÔNG CÒN
            for vid in old_lesson_ids - new_lesson_ids:
                Lesson.objects.filter(pk=vid).delete()
            chapter_num += 1
        # XÓA CHAPTER KHÔNG CÒN
        for cid in old_chapter_ids - new_chapter_ids:
            Chapter.objects.filter(pk=cid).delete()

        messages.success(request, "Course updated successfully.")
        return redirect("my_courses")
    return render(request, "app/edit_course.html", {"course": course})

@login_required
def create_course_view(request):
    if not request.user.is_authenticated or (request.user.role != 'instructor' and request.user.role != 'admin'):
        messages.error(request, "You must be logged in as an instructor or an administrator to create a course.")
        return redirect('my_courses')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            # Xử lý categories (ManyToMany)
            category_ids = []
            for cat in request.POST.getlist('categories'):
                try:
                    cat_id = int(cat)
                    category_ids.append(cat_id)
                except ValueError:
                    # Nếu là tên mới, tạo mới category
                    category_obj, _ = CourseCategory.objects.get_or_create(name=cat)
                    category_ids.append(category_obj.id)
            if category_ids:
                course.categories.set(category_ids)
            form.save_m2m()

            # Xử lý chapter và lesson (Video)
            chapter_num = 1
            while True:
                chapter_title = request.POST.get(f'chapter_title_{chapter_num}')
                if not chapter_title:
                    break
                chapter = Chapter.objects.create(course=course, title=chapter_title, order=chapter_num)
                lesson_num = 1
                while True:
                    lesson_title = request.POST.get(f'lesson_title_{chapter_num}_{lesson_num}')
                    lesson_type = request.POST.get(f'lesson_type_{chapter_num}_{lesson_num}')
                    youtube_url = request.POST.get(f'youtube_url_{chapter_num}_{lesson_num}')
                    question_list_title = request.POST.get(f'question_list_title_{chapter_num}_{lesson_num}')
                    if not lesson_title and not question_list_title:
                        break
                    embed_code = ''
                    if lesson_type == 'theory' and youtube_url:
                        embed_code = get_custom_youtube_embed(
                            youtube_url=youtube_url,
                            extra_params="vq=hd720"
                        )
                    Lesson.objects.create(
                        course=course,
                        chapter=chapter,
                        title=lesson_title or (question_list_title or ''),
                        lesson_type=lesson_type,
                        youtube_url=youtube_url if lesson_type == 'theory' else None,
                        embed_code=embed_code if lesson_type == 'theory' else None,
                        question_list_title=question_list_title if lesson_type == 'question' else None,
                    )
                    lesson_num += 1
                chapter_num += 1

            messages.success(request, "Course created successfully.")
            return redirect('course_detail', courseID=course.courseID)
    else:
        form = CourseForm()
    return render(request, 'app/create_course.html', {'form': form})

@csrf_exempt
def verify_email(request):
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        signup_data = request.session.get('signup_data')
        if not signup_data:
            messages.error(request, "Session expired. Please register again.")
            return redirect('signup')

        if code == signup_data.get('verification_code'):
            # Tạo user
            user = User(
                first_name=signup_data['first_name'],
                last_name=signup_data['last_name'],
                username=signup_data['username'],
                email=signup_data['email'],
                role=signup_data['role'],
            )
            user.set_password(signup_data['password'])
            user.save()
            # Xóa session
            del request.session['signup_data']
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid verification code. Please try again.")
            return redirect('signup')  # hoặc render lại signup.html với form nhập mã

    return redirect('signup')

def resend_verification_code(request):
    signup_data = request.session.get('signup_data')
    if not signup_data:
        messages.error(request, "Session expired. Please register again.")
        return redirect('signup')

    # Tạo mã mới và gửi lại
    verification_code = str(random.randint(100000, 999999))
    signup_data['verification_code'] = verification_code
    request.session['signup_data'] = signup_data

    send_mail(
        subject="Your Verification Code",
        message=f"Your verification code is: {verification_code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[signup_data['email']],
        fail_silently=False,
    )
    messages.info(request, "A new verification code has been sent to your email.")
    return redirect('signup')

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def clear_signup_session(request):
    if 'signup_data' in request.session:
        del request.session['signup_data']
    return HttpResponse("ok")

def course_search_ajax(request):
    q = request.GET.get('q', '')
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', 'newest')
    courses = Course.objects.all()
    if category_id:
        courses = courses.filter(categories__id=category_id)
    if q:
        courses = courses.filter(courseName__icontains=q)
    courses = courses.annotate(enroll_count=Count('enrollment'))
    # Sắp xếp như cũ...
    # (copy logic sort từ course_view)
    data = []
    for c in courses[:20]:  # Giới hạn 20 kết quả
        data.append({
            'courseID': c.courseID,
            'courseName': c.courseName,
            'description': c.description[:120] + ('...' if len(c.description) > 120 else ''),
            'thumbnail': c.thumbnail.url if c.thumbnail else '/media/thumbnails/default-product-card.webp',
            'category': c.category.name if hasattr(c, 'category') and c.category else '',
        })
    return JsonResponse({'courses': data})

def blog_search_ajax(request):
    q = request.GET.get('q', '')
    blogs = Blog.objects.all()
    if q:
        blogs = blogs.filter(title__icontains=q)
    data = []
    for b in blogs[:20]:  # Giới hạn 20 kết quả
        data.append({
            'id': b.id,
            'title': b.title,
            'author': b.author.get_full_name() if hasattr(b.author, 'get_full_name') else b.author.username,
            'created_at': b.created_at.strftime('%d/%m/%Y'),
            'content_preview': b.content[:120] + ('...' if len(b.content) > 120 else ''),
            'avatar': b.author.avatar.url if hasattr(b.author, 'avatar') and b.author.avatar else '/static/images/avatar-default.png',
            'url': f"/blog/{b.id}/",
        })
    return JsonResponse({'blogs': data})

@login_required
def my_blog_view(request):
    user_blogs = Blog.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'app/my_blog.html', {'user_blogs': user_blogs})

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully.")
            return redirect('my_blogs')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BlogForm(instance=blog)
    return render(request, 'app/edit_blog.html', {'form': form, 'blog': blog})

@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)
    if request.method == 'POST':
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect('my_blogs')
    return render(request, 'app/confirm_delete_blog.html', {'blog': blog})