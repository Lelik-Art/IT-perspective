from django.urls import path
from .views import get_published_courses, my_courses, enroll_to_course, course_info_view, course_enroll, yslov_ych_view, course_manage, teacher_courses, get_all_courses_info, course_view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('edit-course', save_course_content, name='edit-course'),
    path('', get_published_courses, name='home'),
    path('courses', course_manage, name='courses'),
    path('my-courses', my_courses, name='my_courses'),
    path('teacher-courses', teacher_courses, name='teacher_courses'),
    path('edit-courses', get_all_courses_info, name='edit_courses'),
    path('course-enroll', course_enroll, name='course-enroll'),
    path('enroll', enroll_to_course, name='enroll_to_course'),
    path('course-info', course_info_view, name='course_info'),
    path('yslov_ych', yslov_ych_view, name='yslov_ych'),
    path('course-view', course_view, name='course_view')
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)