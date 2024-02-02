from django.utils import timezone
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
    
    def is_completed(self, user):
        return all(video.user_progress.filter(user=user, is_completed=True).exists() for video in self.videos.all())

class Video(models.Model):
    title = models.CharField(max_length=100)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True, related_name='lesson')
    video = models.CharField(max_length=300)

    def __str__(self):
        return self.title
    
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='userProgress')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True, related_name='videoProgress')
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.video.title} - Completed: {self.is_completed}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name="courseComment")
    message = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user} comment on {self.course}"

# Quiz
class Difficulty(models.Model):
    difficulty = models.CharField(max_length=6)

    def __str__(self):
        return self.difficulty

class Quiz(models.Model):
    title = models.CharField(max_length=100)
    number_of_questions = models.IntegerField(blank=True, null=True)
    duration = models.PositiveIntegerField(help_text="duration of the quiz in minutes")
    required_score_to_pass = models.IntegerField(blank=True, null=True ,help_text="required score in %")
    difficulty = models.CharField(max_length=6, blank=True, null=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, blank=True, null=True, related_name='quizLesson')
    

    def __str__(self):
        return self.title
    
    def get_question(self):
        return self.question_set.all()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)
    
    def __str__(self):
        return self.question_text

class AnswerChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.answer_text} Correct Answer: {self.is_correct}"

class UserResponse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(AnswerChoice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} "
    
class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    score = models.IntegerField(default=0, blank=True, null=True)
    correct_answers_count = models.IntegerField(default=0)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s attempt on {self.quiz.title}"