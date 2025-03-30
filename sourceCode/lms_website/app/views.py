from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Users, Courses, Videos

User = get_user_model()

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kiểm tra tài khoản trong hệ thống
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Điều hướng đến trang chính sau khi đăng nhập thành công
        else:
            messages.error(request, "Invalid username or password")  # Hiển thị lỗi nếu đăng nhập sai
            return redirect("login")  # Quay lại trang đăng nhập
    else:
        return render(request, "pages/login.html")

def signup_view(request):
    if request.method == "POST":
        full_name = request.POST.get("fullName")  # Lấy họ tên
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        # ✅ Kiểm tra dữ liệu hợp lệ
        if not all([full_name, username, email, password, confirm_password]):
            messages.error(request, "Vui lòng nhập đầy đủ thông tin.")
            return redirect("signup")

        if password != confirm_password:
            messages.error(request, "Mật khẩu nhập lại không khớp.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Tên người dùng đã tồn tại.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email đã được sử dụng.")
            return redirect("signup")

        # ✅ Tách họ và tên
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # ✅ Tạo user mới
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
        )
        
        user.set_password(password)  # Băm mật khẩu đúng chuẩn Django
        user.save()  # Lưu user vào cơ sở dữ liệu

        messages.success(request, "Đăng ký thành công! Bạn có thể đăng nhập.")
        return redirect("login")

    return render(request, "pages/signup.html")

def start_view(request):
    return render(request, "index.html")

def home_view(request):
    return render(request, "pages/home.html")

def allcources_view(request):
    return render(request, "pages/courses.html")

def todo_view(request):
    return render(request, "pages/todo.html")

def account_view(request):
    return render(request, "pages/account.html")

