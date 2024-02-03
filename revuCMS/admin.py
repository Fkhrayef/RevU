from django.contrib import admin

from .models import User, Category, Course, Lesson, Video, Comment, UserProgress, Quiz, Question, AnswerChoice, UserResponse, Difficulty, QuizAttempt, Award, Badge
# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Course)
admin.site.register(Lesson)
admin.site.register(Video)
admin.site.register(Comment)
admin.site.register(UserProgress)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(AnswerChoice)
admin.site.register(UserResponse)
admin.site.register(Difficulty)
admin.site.register(QuizAttempt)
admin.site.register(Award)
admin.site.register(Badge)