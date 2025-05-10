from django.shortcuts import render, redirect, get_object_or_404
from .models import Course, Progress
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def get_published_courses(request):
    courses = Course.objects.filter(status='published')
    context = {
        'courses': courses
    }
    return render(request, 'courses/courses_list.html', context)

@login_required
def my_courses(request):
    try:
        enrolled_courses = Course.objects.filter(
            progress__student=request.user
        ).distinct()
        context = {
            'courses': enrolled_courses,
            'username': request.user.name
        }
        return render(request, 'courses/my_courses.html', context)
    except Exception as e:
        return render(request, 'courses/error.html', {'error_message': str(e)}, status=500)

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
                return render(request, 'courses/enroll_success.html', {
                    'course': course,
                    'username': request.user.name
                })            
            else:
                messages.warning(request, 'Вы уже записаны на этот курс!')
                return redirect('my_courses')
            
        except Exception as e:
            messages.error(request, f'Ошибка записи: {str(e)}')
            return redirect('get_published_courses')
