from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    pass

class Category(models.Model):
    categoryName = models.CharField(max_length=20)

    def __str__(self):
        return self.categoryName

class Course(models.Model):
    title = models.CharField(max_length=20)
    description = models.CharField(max_length=100)
    imageUrl = models.CharField(max_length=300, default=None)
    isActive = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True, related_name="category")
    enrollment = models.ManyToManyField(User, blank=True, null=True, related_name="CourseEnrollment")

    def __str__(self):
        return self.title

class Lesson(models.Model):
    title = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name='course')

    def __str__(self):
        return self.title

class Video(models.Model):
    title = models.CharField(max_length=100)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True, related_name='lesson')
    video = models.CharField(max_length=300)

    def __str__(self):
        return self.title
