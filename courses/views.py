import os
import json
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Progress

def get_published_courses(request):
    courses = Course.objects.filter(status='published').select_related('teacher')
    json_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)
    except FileNotFoundError:
        return render(request, 'home.html', {'error': 'Файл не найден'})
    course_list = []
    for course in courses:
        topic_entry = next((item for item in topics_data if item.get('course_id') == course.course_id), {})
        description = topic_entry.get('description', 'Описание недоступно')
        course_list.append({
            'id': course.course_id,
            'title': course.title,
            'description': description,
            'teacher_name': course.teacher.name,
            'course_cover': course.cover_image,
        })
    context = {
        'courses': course_list
    }
    return render(request, 'home.html', context)

@login_required
def my_courses(request):
    try:
        user = request.user
        enrolled_courses = Course.objects.filter(progress__student=user).distinct()
        all_published_courses = Course.objects.filter(status='published')
        unenrolled_courses = all_published_courses.exclude(id__in=enrolled_courses.values_list('id', flat=True))
        context = {
            'enrolled_courses': enrolled_courses,
            'unenrolled_courses': unenrolled_courses,
            'username': user.name
        }
        return render(request, 'student_room.html', context)

    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)}, status=500)


@login_required
def enroll_to_course(request):
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course_id')
            course = get_object_or_404(Course, pk=course_id)

            if not Progress.objects.filter(student=request.user, course=course).exists():
                Progress.objects.create(
                    student=request.user,
                    course=course,
                    topic_id=None,
                    test_id=None,
                    score=0
                )
                print("Создан прогресс")
                return render(request, 'enroll_success.html', {
                    'course': course,
                    'username': request.user.name
                })            
            else:
                messages.warning(request, 'Вы уже записаны на этот курс!')
                return redirect('my_courses')

        except Exception as e:
            messages.error(request, f'Ошибка записи: {str(e)}')
            return redirect('get_published_courses')

@login_required
def course_info_view(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return HttpResponseBadRequest("Не передан course_id")
    try:
        course = Course.objects.select_related('teacher').get(course_id=course_id)
    except Course.DoesNotExist:
        return render(request, 'course_info.html', {'error': 'Курс не найден'})
    
    json_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)
    except FileNotFoundError:
        return render(request, 'course_info.html', {'error': 'Файл не найден'})

    course_topics = next((entry for entry in topics_data if entry['course_id'] == int(course_id)), None)

    if not course_topics:
        return render(request, 'course_info.html', {'error': 'Не найден курс с данным ID'})

    context = {
        'course': course,
        'teacher': course.teacher,
        'topics': course_topics.get('topics', []),
        'description': course_topics.get('description', ''),
    }
    return render(request, 'course_info.html', context)
