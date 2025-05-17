from django.urls import path
from .views import get_published_courses, my_courses, enroll_to_course, course_info_view, course_enroll, course_view

urlpatterns = [
    # path('edit-course', save_course_content, name='edit-course'),
    path('', get_published_courses, name='home'),
    path('my-courses', my_courses, name='my_courses'),
    path('course-enroll', course_enroll, name='course-enroll'),
    path('enroll', enroll_to_course, name='enroll_to_course'),
    path('course-info', course_info_view, name='course_info'),
    path('course-view', course_view, name='course_view')
]
