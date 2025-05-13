from django.db import models
from django.conf import settings

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('archived', 'Архивированно'),
    ], default='draft')
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    tags = models.ManyToManyField(Tag, through='CourseTag')

    # def __str__(self):
    #     return self.title


class CourseTag(models.Model):
    course = models.ForeignKey(Course, to_field='course_id', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, to_field='tag_id', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('course', 'tag')


class Progress(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, to_field='course_id', on_delete=models.CASCADE)
    topic_id = models.IntegerField(null=True)
    test_id = models.IntegerField(null=True)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('student', 'course', 'topic_id', 'test_id')
