from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password


from .models import User
from .utils import generate_code, send_confirmation_email, send_restore_password_email

import re


def restore_password_view(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Ошибка получения кода')
        return redirect('login')
    
    try:
        user = User.objects.get(code=code)
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if(not validate_password(new_password)):
                messages.error(request, 'Пароль должен быть не менее 8 символов')
                return render(request, 'restore_password.html', {'code': code})
            
            if new_password != confirm_password:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'restore_password.html', {'code': code})

            user.set_password(new_password)
            user.code = None 
            user.save()
            messages.success(request, 'Пароль успешно обновлён')
            return redirect('login')
        
        return render(request, 'restore_password.html', {'code': code})

    except User.DoesNotExist:
        messages.error(request, 'Код недействителен или уже был использован')
        return redirect('login')


def forgive_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            messages.error(request, 'Вы не заполнили поле электронной почты')
        try:
            user = User.objects.get(email=email)
            if user.is_confirmed:
                code = generate_code()
                user.code = code
                user.save()
                send_restore_password_email(user)
                messages.success(request, 'Письмо отправлено на почту')
            else:
                messages.error(request, 'Данный аккаунт не подтверждён')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с введённым email не найден')
    return render(request, 'forgive_password.html')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if not email or not name or not password or not role:
            messages.error(request, 'Вы не заполнили одно из полей')
            return redirect("register")
            # return JsonResponse({'error': 'Вы не заполнили одно из полей'}, status=400)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email уже используется')
            return redirect("register")
            # return JsonResponse({'error': 'Email уже используется'}, status=400)
        if(not validate_email(email)):
            messages.error(request, 'Вы ввели не электронную почту')
            return redirect("register")
        	# return JsonResponse({'error': 'Вы ввели не электронную почту'}, status=400)
        if(not validate_password(password)):
            messages.error(request, 'Пароль должен состоять из не менее 8 символов и не более 64')
            return redirect("register")
        	# return JsonResponse({'error': 'Пароль должен состоять из не менее 8 символов и не более 64'}, status=400)
        code = generate_code()
        user = User.objects.create_user(email=email, password=password, name=name, role=role, code=code)
        send_confirmation_email(user)
        messages.success(request, 'Письмо отправлено на почту')
    return render(request, 'register.html')

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        print(email)
        password = request.POST.get('password')
        print(password)
        try:
            user = User.objects.get(email=email)
            print(user.email)
            print(user.password)
            if check_password(password, user.password):
                if user.is_confirmed:
                    user.is_active = True
                    user.save()
                    login(request, user)
                    return redirect("home")
                else:
                    messages.error(request, "Данный аккаунт не подтверждён.")
                    return redirect("login")
            else:
                messages.error(request, "Неверное имя пользователя или пароль.")
                return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Неверное имя пользователя или пароль.")
    return render(request, "login.html")

def confirm_view(request):
    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Ошибка получения кода')
        return redirect('register')
    
    try:
        user = User.objects.get(code=code, is_confirmed=False)
        user.is_confirmed = True
        user.is_active = True  
        user.code = None  
        user.save()

        login(request, user)

        messages.success(request, 'Регистрация успешно подтверждена!')
        return redirect('home')
        
    except User.DoesNotExist:
        messages.error(request, 'Код недействителен или уже был использован')
        return redirect('register')

def user_logout(request):
    logout(request)
    return redirect("login")

def validate_password(password):
    return 8 <= len(password) <= 63

def validate_email(email):
    email = email.strip()
    print(email)
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.fullmatch(email_pattern, email):
        print("False")
        return False
    else:
    	return True
