from django.urls import path
from .views import get_published_courses, my_courses, enroll_to_course, course_info_view

urlpatterns = [
    path('', get_published_courses, name='get_published_courses'),
    path('student-room', my_courses, name='my_courses'),
    path('enroll', enroll_to_course, name='enroll_to_course'),
    path('course-info', course_info_view, name='course_info'),
]
