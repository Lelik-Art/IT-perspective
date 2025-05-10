from django.urls import path
from . import views

urlpatterns = [
    path('',views.get_published_courses ,name='get_published_courses'),
    path('my-courses',views.my_courses ,name='my_courses'),
    path('<int:pk>',views.enroll_to_course, name='enroll_to_course')
]