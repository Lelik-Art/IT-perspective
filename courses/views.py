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
from authorization.models import User
from django.http import HttpResponseBadRequest

def get_published_courses(request):
    courses = Course.objects.filter(status='published').select_related('teacher')
    try:
        course_list = []
        for course in courses:
            course_list.append({
                'id': course.course_id,
                'title': course.title,
                'teacher_name': course.teacher.name,
                'course_cover': course.cover_image,
            })
        context = {
            'courses': course_list
        }
        return render(request, 'courses_list.html', context)
    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('home')

@login_required
def my_courses(request):
    try:
        user = request.user
        if user.role == "Teacher":
            messages.warning(request, "Ваш профиль не верифицирован")
        enrolled_courses = Course.objects.filter(progress__student=user).distinct()
        all_published_courses = Course.objects.filter(status='published')
        unenrolled_courses = all_published_courses.exclude(id__in=enrolled_courses.values_list('id', flat=True))
        context = {
            'enrolled_courses': enrolled_courses,
            'unenrolled_courses': unenrolled_courses,
            'username': user.name
        }
        return render(request, 'my_courses.html', context)

    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('my_courses')

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
                messages.success(request, "Вы подписались на курс")        
            else:
                messages.warning(request, 'Вы уже записаны на этот курс!')
                return redirect('course_info')

        except Exception as e:
            messages.error(request, f'Ошибка записи: {str(e)}')
            return redirect('course_info')

@login_required
def course_info_view(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return HttpResponseBadRequest("Не передан course_id")
    try:
        course = Course.objects.select_related('teacher').get(course_id=course_id)
    except Course.DoesNotExist:
        messages.error(request, f"Курс не найден")
        return redirect('course_info')
    
    json_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)
    except FileNotFoundError:
        messages.error(request, f"Файл topics.json не найден")
        return redirect('course_info')

    course_topics = next((entry for entry in topics_data if entry['course_id'] == int(course_id)), None)

    if not course_topics:
        messages.error(request, f"Не найден курс с данным ID")
        return redirect('course_info')

    context = {
        'course': course,
        'teacher': course.teacher,
        'topics': course_topics.get('topics', [])
    }
    return render(request, 'course_info.html', context)

@login_required
def course_enroll(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return HttpResponseBadRequest("Не передан course_id")
    try:
        course = Course.objects.select_related('teacher').get(course_id=course_id)
    except Course.DoesNotExist:
        messages.error(request, f"Курс не найден")
        return redirect('course-enroll')
    
    json_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)
    except FileNotFoundError:
        messages.error(request, f"Файл topics.json не найден")
        return redirect('course-enroll')

    course_topics = next((entry for entry in topics_data if entry['course_id'] == int(course_id)), None)

    if not course_topics:
        messages.error(request, f"Не найден курс с данным ID")
        return redirect('course-enroll')

    context = {
        'course': course,
        'teacher': course.teacher,
        'topics': course_topics.get('topics', [])
    }
    return render(request, 'course_enroll.html', context)


# def save_course_content(request):
#     if request.method == 'POST':
#         course_id = request.POST.get('course_id')
#         if not course_id:
#             return HttpResponse("Нет course_id", status=400)
        
#         try:
#             course = Course.objects.get(course_id=course_id)
#         except Course.DoesNotExist:
#             return HttpResponse("Курс не найден", status=404)

#         topics = []
#         topic_index = 1
#         while True:
#             topic_title = request.POST.get(f'topic_{topic_index}_title')
#             if not topic_title:
#                 break

#             topic = {
#                 "topic_id": topic_index,
#                 "title": topic_title,
#                 "order": topic_index,
#                 "test_id": topic_index,
#                 "lessons": []
#             }

#             lesson_index = 1
#             while True:
#                 lesson_title = request.POST.get(f'topic_{topic_index}_lesson_{lesson_index}_title')
#                 lesson_text = request.POST.get(f'topic_{topic_index}_lesson_{lesson_index}_text')
#                 if not lesson_title:
#                     break

#                 lesson = {
#                     "lesson_id": lesson_index,
#                     "title": lesson_title,
#                     "text": lesson_text or '',
#                     "order": lesson_index
#                 }
#                 topic["lessons"].append(lesson)
#                 lesson_index += 1

#             topics.append(topic)
#             topic_index += 1

#         image_files = request.FILES.getlist('images')
#         material_files = request.FILES.getlist('materials')
#         video_files = request.FILES.getlist('videos')

#         image_paths = []
#         for file in image_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_images', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             image_paths.append(path)

#         material_paths = []
#         for file in material_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_materials', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             material_paths.append(path)

#         video_paths = []
#         for file in video_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_videos', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             video_paths.append(path)

#         data = {
#             "course_id": int(course_id),
#             "description": "Описание", 
#             "topics": topics,
#             "images": image_paths,
#             "materials": material_paths,
#             "videos": video_paths
#         }

#         json_path = os.path.join(settings.MEDIA_ROOT, 'topics.json')

#         if os.path.exists(json_path):
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 existing_data = json.load(f)
#         else:
#             existing_data = []

#         for i, item in enumerate(existing_data):
#             if item.get("course_id") == int(course_id):
#                 existing_data[i] = data
#                 break
#         else:
#             existing_data.append(data)

#         with open(json_path, 'w', encoding='utf-8') as f:
#             json.dump(existing_data, f, ensure_ascii=False, indent=2)

#         return HttpResponse("Данные успешно сохранены", status=200)

#     elif request.method == 'GET':
#         course_id = request.GET.get('course_id')
#         if not course_id:
#             return HttpResponse("Нет course_id", status=400)

#         json_path = os.path.join(settings.MEDIA_ROOT, 'topics.json')
#         if os.path.exists(json_path):
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 courses_data = json.load(f)

#             course_data = next((course for course in courses_data if course["course_id"] == int(course_id)), None)
#             if not course_data:
#                 return HttpResponse("Курс не найден", status=404)

#             return render(request, 'edit_course.html', {'course_data': course_data})

#         return HttpResponse("Нет данных", status=404)



# def save_course_content(request):
#     if request.method == 'POST':
#         course_id = request.POST.get('course_id')
#         if not course_id:
#             return HttpResponse("Нет course_id", status=400)

#         try:
#             course = Course.objects.get(course_id=course_id)
#         except Course.DoesNotExist:
#             return HttpResponse("Курс не найден", status=404)

#         topics = []
#         topic_index = 1
#         while True:
#             topic_title = request.POST.get(f'topic_{topic_index}_title')
#             if not topic_title:
#                 break

#             topic = {
#                 "topic_id": topic_index,
#                 "title": topic_title,
#                 "order": topic_index,
#                 "test_id": topic_index, 
#                 "lessons": []
#             }

#             lesson_index = 1
#             while True:
#                 lesson_title = request.POST.get(f'topic_{topic_index}_lesson_{lesson_index}_title')
#                 lesson_text = request.POST.get(f'topic_{topic_index}_lesson_{lesson_index}_text')
#                 if not lesson_title:
#                     break

#                 lesson = {
#                     "lesson_id": lesson_index,
#                     "title": lesson_title,
#                     "text": lesson_text or '',
#                     "order": lesson_index
#                 }

#                 topic["lessons"].append(lesson)
#                 lesson_index += 1

#             topics.append(topic)
#             topic_index += 1

#         image_files = request.FILES.getlist('images')
#         material_files = request.FILES.getlist('materials')
#         video_files = request.FILES.getlist('videos')

#         image_paths = []
#         for file in image_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_images', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             material_paths.append(path)

#         material_paths = []
#         for file in material_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_materials', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             material_paths.append(path)

#         video_paths = []
#         for file in video_files:
#             filename = f"{get_random_string(8)}_{file.name}"
#             path = os.path.join('course_videos', str(course_id), filename)
#             full_path = os.path.join(settings.MEDIA_ROOT, path)
#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as dest:
#                 for chunk in file.chunks():
#                     dest.write(chunk)
#             video_paths.append(path)

#         data = {
#             "course_id": int(course_id),
#             "topics": topics,
#             "materials": material_paths,
#             "videos": video_paths
#         }

#         json_path = os.path.join(settings.MEDIA_ROOT, 'topics.json')

#         # Если файл существует, загружаем его
#         if os.path.exists(json_path):
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 existing_data = json.load(f)
#         else:
#             existing_data = []

#         existing_data.append(data)

#         with open(json_path, 'w', encoding='utf-8') as f:
#             json.dump(existing_data, f, ensure_ascii=False, indent=2)

#         return HttpResponse("Данные успешно сохранены", status=200)

#     return render(request, 'edit_course.html')

# def edit_course(request):
#     course_id = request.GET.get('course_id')

#     topics = []
#     materials = []
#     videos = []

#     if course_id:
#         json_path = os.path.join(settings.MEDIA_ROOT, 'topics.json')
#         if os.path.exists(json_path):
#             with open(json_path, 'r', encoding='utf-8') as f:
#                 all_data = json.load(f)
#                 for entry in all_data:
#                     if str(entry.get('course_id')) == str(course_id):
#                         topics = entry.get('topics', [])
#                         materials = entry.get('materials', [])
#                         videos = entry.get('videos', [])
#                         break

#     return render(request, 'edit_course.html', {
#         'course_id': course_id or '',
#         'topics': json.dumps(topics, ensure_ascii=False),
#         'materials': materials,
#         'videos': videos,
#     })

@login_required
def course_view(request):
    course_id = request.GET.get('course_id')
    if not course_id:
        return HttpResponseBadRequest("Не передан course_id")

    try:
        course = Course.objects.select_related('teacher').get(course_id=course_id)
    except Course.DoesNotExist:
        messages.error(request, "Курс не найден")
        return redirect('my_courses')

    json_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)
    except Exception as e:
        messages.error(request, f"Ошибка загрузки данных: {str(e)}")
        return redirect('my_courses')

    course_topics = next((entry for entry in topics_data if entry['course_id'] == int(course_id)), None)

    if not course_topics:
        messages.error(request, f"Не найден курс с данным ID")
        return redirect('my_courses')

    context = {
        'course': {
            'id': course.course_id,
            'title': course.title,
            'teacher': course.teacher.name,
            'cover': course.cover_image.url if course.cover_image else None,
            'status': course.get_status_display(),
        },
        'topics': course_topics.get('topics', []),
        'progress': Progress.objects.filter(
            student=request.user,
            course=course
        ).first()
    }
    return render(request, 'course_view.html', context)