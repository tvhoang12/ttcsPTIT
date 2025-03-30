from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        # Kiểm tra tài khoản trong hệ thống
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Điều hướng đến trang chính sau khi đăng nhập thành công
        else:
            messages.error(request, "Invalid username or password")  # Hiển thị lỗi nếu đăng nhập sai

    return render(request, "pages/login.html")  # Render lại trang login nếu đăng nhập thất bại

def signup_view(request):
    if request.method == "POST":
        fullName = request.POST.get("fullName")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")

        # Xử lý đăng ký (chẳng hạn, kiểm tra với database)
        if email and username and password and confirm_password:
            if password == confirm_password:
                return HttpResponse(f"Đăng ký thành công! Email: {email}, Username: {username}, Password: {password}")
            else:
                return HttpResponse("Mật khẩu không khớp.")
        else:
            return HttpResponse("Vui lòng nhập đầy đủ thông tin.")

    return render(request, "pages/signup.html")  # Hiển thị trang signup nếu chưa submit form

from django.shortcuts import render

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

