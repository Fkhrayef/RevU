from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from datetime import datetime, timedelta
from .models import User, Category, Course, Lesson, Video, Comment, UserProgress, Difficulty, Quiz, Question, AnswerChoice, UserResponse, QuizAttempt


def index(request):
    activeCourses = Course.objects.filter(isActive=True)
    allCategories = Category.objects.all()
    return render(request, "revuCMS/index.html", {
        "courses": activeCourses,
        "categories": allCategories
    })

def displayCategory(request):
    if request.method == "POST":
        categoryFromForm = request.POST["category"]
        category = Category.objects.get(categoryName=categoryFromForm)
        activeCourses = Course.objects.filter(isActive=True, category=category)
        allCategories = Category.objects.all()
        return render(request, "revuCMS/index.html", {
            "courses": activeCourses,
            "categories": allCategories
        })

def course(request, id):
    courseData = Course.objects.get(pk=id)
    isEnrolled = request.user in courseData.enrollment.all()
    allComments = Comment.objects.filter(course=courseData)
    return render(request, "revuCMS/course.html", {
        "course": courseData,
        "isEnrolled": isEnrolled,
        "allComments": allComments
    })

def search(request):
    if request.method == "POST":
        searchQuery = request.POST["q"]
        courseSearch = Course.objects.filter(title__icontains=searchQuery)
        return render(request, "revuCMS/search.html", {
            "searchQuery": searchQuery,
            "courseSearch": courseSearch
        })

def manage(request):
    activeCourses = Course.objects.filter(isActive=True)
    return render(request, "revuCMS/manage.html", {
        "courses": activeCourses
    })

def createCourse(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "revuCMS/create.html", {
            "categories": allCategories
        })
    else:
        # Get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        imageurl = request.POST["imageurl"]
        category = request.POST["category"]
        # Who is the user
        currentUser = request.user
        # Get all content about the particular category
        categoryData = Category.objects.get(categoryName=category)
        # Create a new Course object
        newCourse = Course(
            title=title,
            description=description,
            imageUrl=imageurl,
            category=categoryData,
            owner=currentUser
        )
        newCourse.save()
        return HttpResponseRedirect(reverse(manage))

def deleteCourse(request, id):
    courseData = Course.objects.get(pk=id)
    courseData.delete()
    return HttpResponseRedirect(reverse(manage))

def editCourse(request, id):
    if request.method == "GET":
        courseData = Course.objects.get(pk=id)
        allCategories = Category.objects.all()
        return render(request, 'revuCMS/editCourse.html', {
            "course": courseData,
            "categories": allCategories
        })
    else:
        # Getting the Course by id
        courseId = request.POST["id"]
        courseData = Course.objects.get(pk=courseId)
        
        # Getting the new edited values
        title = request.POST["title"]
        description = request.POST["description"]
        imageUrl = request.POST["imageurl"]
        category = request.POST["category"]
        
        # Converting category to its object instance
        categoryData = Category.objects.get(categoryName=category)

        # Updating the old values
        courseData.title=title
        courseData.description=description
        courseData.imageUrl=imageUrl
        courseData.category=categoryData

        # Saving the new values
        courseData.save()

        # Redirecting to the Manage Courses page
        return HttpResponseRedirect(reverse("editCourse", args=(id, )))

def enroll(request, id):
    courseData = Course.objects.get(pk=id)
    currentUser = request.user
    courseData.enrollment.add(currentUser)
    return HttpResponseRedirect(reverse("courseContent", args=(id, )))

def disenroll(request, id):
    courseData = Course.objects.get(pk=id)
    currentUser = request.user
    courseData.enrollment.remove(currentUser)
    return HttpResponseRedirect(reverse("course", args=(id, )))

def addComment(request, id):
    currentUser = request.user
    courseData = Course.objects.get(pk=id)
    message = request.POST["newComment"]
    newComment = Comment(
        user=currentUser,
        course=courseData,
        message=message
    )
    newComment.save()
    return HttpResponseRedirect(reverse("course", args=(id, )))

def enrolledCourses(request):
    currentUser = request.user
    courses = currentUser.CourseEnrollment.all()
    return render(request, "revuCMS/enrolledCourses.html", {
        "courses": courses
    })

def courseContent(request, id):
    courseData = Course.objects.get(pk=id)
    lessons = Lesson.objects.filter(course=courseData)

    lesson_data = []

    for lesson in lessons:
        videos = Video.objects.filter(lesson=lesson)
        quizzes = Quiz.objects.filter(lesson=lesson)
        lesson_data.append({'lesson': lesson, 'videos': videos, 'quizzes': quizzes})


    # Get UserProgress information for each video
    currentUser = request.user
    for item in lesson_data:
        for video in item['videos']:
            user_progress = UserProgress.objects.filter(user=currentUser, video=video).first()
            video.is_completed = user_progress.is_completed if user_progress else False

    return render(request, 'revuCMS/courseContent.html', {
        "course": courseData,
        'lessons_with_videos': lesson_data,
    })

def mark_videos_completed(request, id):
    currentUser = request.user
    video = Video.objects.get(pk=id)
    if request.method == "POST":

        userProgress, created = UserProgress.objects.get_or_create(user=currentUser, video=video)
        isCompleted = request.POST.get('isCompleted', False) == 'on'
        userProgress.is_completed = isCompleted
        userProgress.save()

        return HttpResponseRedirect(reverse("courseContent", args=(video.lesson.course.id, )))


def addLesson(request, id):
    # Get the Lesson
    courseData = Course.objects.get(id=id)

    if request.method == "GET":
        return render(request, "revuCMS/addLesson.html",{
            'course': courseData
        })
    else:
        # Get the data from the form
        title = request.POST["title"]
        # Create a new Lesson object
        newLesson = Lesson(
            title=title,
            course=courseData
        )
        newLesson.save()
        return HttpResponseRedirect(reverse("courseContent", args=(id, )))

def deleteLesson(request, id):
    # Get the Lesson
    lessonData = Lesson.objects.get(pk=id)
    # Get the course to redirect
    courseData = lessonData.course
    # Delete the object
    lessonData.delete()
    return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def editLesson(request, id):
    # Get the Lesson
    lessonData = Lesson.objects.get(pk=id)
    # Get the course to redirect
    courseData = lessonData.course
    # Get all courses
    allCourses = Course.objects.all()

    if request.method == "GET":
        return render(request, 'revuCMS/editLesson.html', {
            "lesson": lessonData,
            "courses": allCourses
        })
    else:
        # Getting the new edited values
        title = request.POST["title"]
        # course = request.POST["course"] (This section is to change the course of the lesson)
        
        # Converting Course to its object instance
        # courseData = Course.objects.get(title=course) (This section is to change the course of the lesson)

        # Updating the old values
        lessonData.title=title
        # lessonData.course=courseData (This section is to change the course of the lesson)

        # Saving the new values
        lessonData.save()

        # Redirecting to the Course Content page
        return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def addVid(request, id):
    # Get the Lesson
    lessonData = Lesson.objects.get(id=id)
    # Get the Course
    courseData = lessonData.course

    if request.method == "GET":
        return render(request, "revuCMS/addVid.html",{
            'lesson': lessonData
        })
    else:
        # Get the data from the form
        title = request.POST["title"]
        vidurl = request.POST["vidurl"]
        lesson = lessonData
        # Create a new Video object
        newVid = Video(
            title=title,
            video=vidurl,
            lesson=lesson,
        )
        newVid.save()
        return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))
    
def deleteVid(request, id):
    # Get the Video
    vidData = Video.objects.get(pk=id)
    # Get the course to redirect
    lessonData = vidData.lesson
    courseData = lessonData.course
    # Delete the object
    vidData.delete()
    return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def editVid(request, id):
    # Get the Video, Lesson and Course
    vidData = Video.objects.get(pk=id)
    lessonData = vidData.lesson
    courseData = lessonData.course
    # Get all the lessons of the course
    allLessons = Lesson.objects.filter(course=courseData.id)

    if request.method == "GET":
        return render(request, 'revuCMS/editVid.html', {
            "video": vidData,
            "lessons": allLessons
        })
    else:
        # Getting the new edited values
        title = request.POST["title"]
        lesson = request.POST["lesson"]
        
        # Converting lesson to its object instance
        lessonData = Lesson.objects.get(title=lesson)

        # Updating the old values
        vidData.title=title
        vidData.lesson=lessonData

        # Saving the new values
        vidData.save()

        # Redirecting to the Course Content page
        return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def profile(request):
    currentUser = request.user
    if request.method == "GET":
        return render(request, 'revuCMS/profile.html', {
            "user": currentUser
        })
    else:
        # Getting the new edited values
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        username = request.POST["username"]
        email = request.POST["email"]

        # Updating the old values
        currentUser.first_name=fname
        currentUser.last_name=lname
        currentUser.username=username
        currentUser.email=email

        # Saving the new values
        currentUser.save()

        # Redirecting to the Manage Courses page
        return HttpResponseRedirect(reverse(profile))

def quizInfo(request, id):
    quizData = Quiz.objects.get(pk=id)
    return render(request, 'revuCMS/quizInfo.html', {
            "quiz": quizData
        })

def startQuiz(request, id):
    quizData = Quiz.objects.get(pk=id)

    # Check if the user already has an active quiz attempt for this quiz
    active_attempt = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quizData,
        end_time__gte=datetime.now(),
        start_time__lte=datetime.now()
    ).first()

    if active_attempt:
        # Quiz attempt has already started, redirect or show an error message
        return HttpResponseRedirect(reverse("quizInfo", args=(id, )))
    
    # Check if the user already has a prev attempt for this quiz
    prev_attempt = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quizData,
    )

    if prev_attempt.exists():
        prev_attempt.delete()
    
    # Create a new quizAttempt instance
    quizAttempt = QuizAttempt.objects.create(
        user=request.user,
        quiz=quizData,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(minutes=quizData.duration)
    )

    # Retrieve and display quiz questions
    questions = quizData.question_set.all()
    
    return render(request, 'revuCMS/startQuiz.html', {
        "quiz": quizData,
        "quizAttempt": quizAttempt,
        "questions": questions
    })

def submitQuiz(request, id):

    if request.method == 'POST':
        quiz = Quiz.objects.get(pk=id)
        total_questions = quiz.question_set.count()
        currentUser = request.user 
        user_responses = []

        for i in range(1, total_questions + 1):
            # Get a Question and the selected answer for it:
            question_id = int(request.POST.get(f'questionId{i}'))
            question = Question.objects.get(pk=question_id)
            selected_answer_text = request.POST.get(f'answer{question_id}')
            
            # Get the AnswerChoice by the answer text:
            selected_choice = AnswerChoice.objects.get(
                question=question,
                answer_text=selected_answer_text
            )

            # Get the user quiz attempt
            quizAttempt = QuizAttempt.objects.get(
                user=currentUser,
                quiz = quiz
                )

            # Check if the selected answer is correct
            if selected_choice.is_correct:
                quizAttempt.correct_answers_count += 1

            # Create and save a UserResponse object
            user_response = UserResponse.objects.create(
                user=currentUser,
                question=question,
                selected_choice=selected_choice
            )
            user_responses.append(user_response)

            # Update the end time
            quizAttempt.end_time =datetime.now()

            quizAttempt.save()

        return HttpResponseRedirect(reverse("quizResult", args=(id, )))

    return redirect('index')

def quizResult(request, id):
    # Retrieve the quiz attempt, quiz, and user responses
    quiz_attempt = get_object_or_404(QuizAttempt, user=request.user, quiz_id=id)
    quiz = quiz_attempt.quiz
    user_responses = UserResponse.objects.filter(user=request.user, question__quiz=quiz)

    # Calculate the user's score
    score = (quiz_attempt.correct_answers_count / quiz.number_of_questions) * 100
    quiz_attempt.score = round(score, 2)

    # Check if passed or failed
    quiz_attempt.passed = quiz_attempt.score >= quiz.required_score_to_pass
    quiz_attempt.save()

    # Get all the questions of a quiz
    questions = Question.objects.filter(quiz=quiz)

    return render(request, 'revuCMS/quizResult.html', {
        'quiz': quiz,
        'questions': questions,
        'user_answers': user_responses,
        'score': quiz_attempt.score,
        'passed': quiz_attempt.passed
    })


def addQuiz(request, id):
    # Get the Lesson
    lessonData = Lesson.objects.get(id=id)
    # Get the Course
    courseData = lessonData.course

    if request.method == "GET":

        difficulties = Difficulty.objects.all()
        return render(request, 'revuCMS/addQuiz.html', {
            "difficulties": difficulties,
            'lesson': lessonData
        })
    else:
        # Get the data from the form
        title = request.POST["quizTitle"]
        numOfQuestions = request.POST["quizNumOfQuestions"]
        duration = request.POST["quizDuration"]
        scoreToPass = request.POST["scoreToPass"]
        difficulty = request.POST["difficulty"]

        # Converting difficulty to its object instance
        difficultyData = Difficulty.objects.get(difficulty=difficulty)

        # Create a new Video object
        newQuiz = Quiz(
            title=title,
            number_of_questions=numOfQuestions,
            duration=duration,
            required_score_to_pass = scoreToPass,
            difficulty = difficultyData,
            lesson = lessonData
        )
        newQuiz.save()
        return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def editQuiz(request, id):
    # Get the Quiz, Lesson and Course
    quizData = Quiz.objects.get(pk=id)
    lessonData = quizData.lesson
    courseData = lessonData.course
    # Get all the lessons of the course
    allLessons = Lesson.objects.filter(course=courseData.id)
    # Get all difficulties
    difficulties = Difficulty.objects.all()

    if request.method == "GET":
        return render(request, 'revuCMS/editQuiz.html', {
            "quiz": quizData,
            "lessons": allLessons,
            "difficulties": difficulties
        })
    else:
        # Getting the new edited values
        title = request.POST["title"]
        numOfQuestions = request.POST["quizNumOfQuestions"]
        duration = request.POST["quizDuration"]
        scoreToPass = request.POST["scoreToPass"]
        difficulty = request.POST["difficulty"]
        lesson = request.POST["lesson"]
        
        # Converting lesson to its object instance
        lessonData = Lesson.objects.get(title=lesson)

        # Updating the old values
        quizData.title=title
        quizData.number_of_questions=numOfQuestions
        quizData.duration=duration
        quizData.required_score_to_pass=scoreToPass
        quizData.difficulty=difficulty
        quizData.lesson=lessonData

        # Saving the new values
        quizData.save()

        # Redirecting to the Course Content page
        return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def deleteQuiz(request, id):
    # Get the Quiz
    quizData = Quiz.objects.get(pk=id)
    # Get the course to redirect
    lessonData = quizData.lesson
    courseData = lessonData.course
    # Delete the object
    quizData.delete()
    return HttpResponseRedirect(reverse("courseContent", args=(courseData.id, )))

def manageQuiz(request, id):
    quizData = Quiz.objects.get(pk=id)
    questions = Question.objects.filter(quiz=quizData)
    return render(request, "revuCMS/manageQuiz.html", {
        "quiz": quizData,
        "questions": questions
    })

def addQuestion(request, id):
    # Get the Quiz
    quizData = Quiz.objects.get(id=id)

    if request.method == "GET":
        return render(request, "revuCMS/addQuestion.html",{
            'quiz': quizData
        })
    else:
        # Get the Question from the form
        question_text = request.POST["question_text"]
        
        # Create a new Question object
        newQuestion = Question(
            question_text=question_text,
            quiz = quizData
        )
        newQuestion.save()

        # Get the Answers from the form
        correct_answer = int(request.POST["correct_answer"])

        for i in range(1, 5):
            answer_text = request.POST[f"answer{i}"]
            is_correct = (i == correct_answer)

            newAnswer = AnswerChoice(
                question=newQuestion,
                answer_text=answer_text,
                is_correct=is_correct
            )
            newAnswer.save()

        return HttpResponseRedirect(reverse("manageQuiz", args=(id, )))

def editQuestion(request, id):
    questionData = Question.objects.get(pk=id)
    answers = questionData.answerchoice_set.all()

    if request.method == "GET":
        return render(request, "revuCMS/editQuestion.html",{
            "question": questionData,
            "answers": answers
        })
    else:
        # Get the Question from the form
        question_text = request.POST["question_text"]
        questionData.question_text = question_text
        questionData.save()

        # Get the Answers from the form
        for i in range(1, 5):
            answer_text = request.POST.get(f"answer{i}")
    
            # Retrieve the answer from the database based on some identifier, e.g., answer ID
            answer_id = request.POST.get(f"answer_id_{i}")
            answer = AnswerChoice.objects.get(id=answer_id)

            # Check if the current answer ID matches the submitted correct_answer value
            is_correct = str(answer.id) == request.POST.get("correct_answer")

            # Update the answer with the new values
            answer.answer_text = answer_text
            answer.is_correct = is_correct
            answer.save()

        return HttpResponseRedirect(reverse("manageQuiz", args=(questionData.quiz.id, )))

def deleteQuestion(request, id):
    # Get the Question
    questionData = Question.objects.get(pk=id)
    # Get the Quiz to redirect
    quizData = questionData.quiz
    # Delete the object
    questionData.delete()
    return HttpResponseRedirect(reverse("manageQuiz", args=(quizData.id, )))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "revuCMS/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "revuCMS/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "revuCMS/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "revuCMS/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "revuCMS/register.html")
