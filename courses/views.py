import os
import json
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from .models import Course, Progress
from authorization.models import User


def get_published_courses(request):# ✅
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
        #return render(request, 'courses_list.html', context)
        return render(request, 'main_str.html', context)
    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('home')

@login_required# ✅
def my_courses(request):
    try:
        user = request.user
        if(user.role.lower()=="student"):
            enrolled_courses = Course.objects.filter(progress__student=user).distinct()
            all_published_courses = Course.objects.filter(status='published')
            unenrolled_courses = all_published_courses.exclude(course_id__in=enrolled_courses.values_list('course_id', flat=True)  )# ✅ теперь верно
            context = {
                'enrolled_courses': enrolled_courses,
                'unenrolled_courses': unenrolled_courses,
                'username': user.name
            }
            return render(request, 'lkstudent2.html', context)
        else:
            return redirect('teacher_courses')
    except Exception as e:
        print("ERROR:", str(e))  # выведет ошибку в консоль
        traceback.print_exc()    # выведет стек ошибки
        return render(request, 'error.html', {'error': str(e)})
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('')

@login_required
def course_manage(request):
    try:
        user = request.user
        if(user.role.lower()=="teacher" or user.role.lower()=="VerifiedTeacher"):
            return redirect('teacher_courses')
        else:
            return redirect('my_courses')
    except Exception as e:
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('home')

@login_required
def teacher_courses(request):
    try:
        user = request.user
        if(user.role.lower() == "student"):
            return redirect('my_courses')
        if(user.role.lower() == "teacher"):
            messages.error(request, "Ваш профиль ожидает верификации, после подтвержения вам станет доступно создание своих курсов и отслеживание прогресса по ним. Это может занять некоторое время, пока вы можете ознакомиться с доступными курсами и записаться на них, пройдя регистрацию в качестве студента. ")
            return render(request, 'teacher-page-no-verified.html')
        teacher_courses = Course.objects.filter(teacher=user, status__in=['draft', 'published'])
        context = {
            'teacher_courses': teacher_courses,
            'username': user.name
        }
        return render(request, 'lk_prepod.html', context)
    except Exception as e:
        print(e)
        messages.error(request, f"Ошибка: {str(e)}")
        return redirect('home')

@login_required
def get_all_courses_info(request):
    user = request.user
    if user.role.lower() != "VerifiedTeacher":
        return JsonResponse({'error': 'Forbidden'}, status=403)

    topics_path = os.path.join(os.path.dirname(__file__), 'topics.json')
    with open(topics_path, 'r', encoding='utf-8') as file:
            topics_data = json.load(file)

    tests_path = os.path.join(os.path.dirname(__file__), 'tests.json')
    with open(tests_path, 'r', encoding='utf-8') as file:
            tests_data = json.load(file)
    
    teacher_info = {
        "userName": user.name,
        "avatarUrl": request.build_absolute_uri(f"/media/{user.avatar}")
    }

    tests_dict = {test['test_id']: test for test in tests_data}
    topics_by_course = {entry["course_id"]: entry["topics"] for entry in topics_data}
    courses_data = []
    for course in Course.objects.filter(teacher=user):

        sections = []
        course_topics = topics_by_course.get(course.course_id, [])

        for topic in course_topics:
            section = {
                "id": topic["topic_id"],
                "title": topic["title"],
                "description": topic["description"],
                "elements": []
            }

            for lesson in topic.get("lessons", []):
                section["elements"].append({
                    "type": "lesson",
                    "title": lesson["title"],
                    "description": lesson.get("text", ""),
                    "lesson_id": lesson["lesson_id"]
                })


            if "test_id" in topic:
                test_id = topic["test_id"]
                test_info = tests_dict.get(test_id, {})
                
                test_element = {
                    "type": "test",
                    "name": f"Тест к теме {topic['title']}",
                    "test_id": test_id,
                    "questions": test_info.get("questions", []), 
                    "settings": test_info.get("settings", {}) 
                }
                section["elements"].append(test_element)

            
            for media in topic.get("images", []):
                section["elements"].append({
                    "type": "media",
                    "url": media,
                    "media_type": "image"
                })
                
            for video in topic.get("videos", []):
                section["elements"].append({
                    "type": "media",
                    "url": video,
                    "media_type": "video"
                })
            
            sections.append(section)


        student_ids = Progress.objects.filter(course_id=course.course_id).values_list('student', flat=True).distinct()
        students = User.objects.filter(id__in=student_ids)
        
        students_data = []
        for student in students:
            progress_date = Progress.objects.filter(student=student, course_id=course.course_id).order_by('date')
            if progress_date.exists():
                start_date = progress_date.first().date
                last_date = progress_date.last().date
                start_date_str = f"{(timezone.now().date() - start_date).days} дней назад"
                last_date_str = f"{(timezone.now().date() - last_date).days} дней назад"
            else:
                start_date_str = last_date_str = "Дата не найдена"
            progress_topic = Progress.objects.filter(student=student, course_id=course.course_id, topic_id=0).first()
            students_dict = {
                "id": student.id,
                "name": student.name,
                "startDate": start_date_str,
                "endDate": last_date_str, 
                "lessonsCompleted": Progress.objects.filter(student=student, course_id=course.course_id, test_id__isnull=False).count(),
                "status": "Пройдено" if progress_topic.success and progress_topic.topic_id == 0 else "Не пройден"
            }
            students_data.append(students_dict)

        students_count = Progress.objects.filter(course=course).values('student').distinct().count()
        completed_students_count = Progress.objects.filter(course=course, topic_id=0, success=True).values('student').distinct().count()
        if students_count > 0:
            completion_rate = int((completed_students_count / students_count) * 100)
        else:
            completion_rate = 0

        completed_students = Progress.objects.filter(course=course, topic_id=0, success=True).values_list('student', flat=True).distinct()
        average_score = (Progress.objects.filter(course=course, student__in=completed_students).aggregate(avg_score=Avg('score'))['avg_score'])
        average_score = int(average_score) if average_score is not None else 0

        course_dict = {
            "id": course.course_id,
            "name": course.title,
            "isVisible": course.status != "archived",
            "isPublished": course.status == "published",
            "statistics": {"isExpanded": False},
            "stats": {
                "totalStudents": students_count,
                "completionRate": completion_rate,
                "certificatesIssued": completed_students_count,
                "incompleteCourses": students_count - completed_students_count,
                "averageScore": average_score 
            },
            "sections": sections
        }
        courses_data.append(course_dict)


    response_data = {
        "teacherInfo": teacher_info,
        "courses": courses_data,
        "students": students_data
    }

    print(response_data)
    return render(request, 'teacher-page.html', context=response_data)


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

def yslov_ych_view(request):
    return render(request, 'yslov_ych.html')

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