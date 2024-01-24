from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Course, Lesson, Video, Comment


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
        id = request.POST["id"]
        courseData = Course.objects.get(pk=id)
        
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
        lesson_data.append({'lesson': lesson, 'videos': videos})

    return render(request, 'revuCMS/courseContent.html', {
        "course": courseData,
        'lessons_with_videos': lesson_data,
    })

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
