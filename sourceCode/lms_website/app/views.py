from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
from django.core.paginator import Paginator
from app.models import Courses

from app.models import Posts

def home(request):
    return render(request, 'app/index.html')

def about(request):
    return render(request, 'app/about.html')

def blog(request):
    posts = Posts.objects.all().order_by('-created_at')  # Latest posts first
    return render(request, 'app/blog.html', {'posts': posts})

def post_detail(request, post_id):
    post = get_object_or_404(Posts, id=post_id)
    return render(request, 'app/post.html', {'post': post})

def courses(request):
    # Fetch all courses
    course_list = Courses.objects.all()
    
    # Set up pagination (20 courses per page)
    paginator = Paginator(course_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'courses_template.html', {'courses': page_obj, 'page_obj': page_obj})

def contact(request):
    return render(request, 'app/contact.html')