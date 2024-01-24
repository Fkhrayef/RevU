from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.createCourse, name="create"),
    path("displayCategory", views.displayCategory, name="displayCategory"),
    path("course/<int:id>", views.course, name="course"),
    path("disenroll/<int:id>", views.disenroll, name="disenroll"),
    path("enroll/<int:id>", views.enroll, name="enroll"),
    path("enrolledCourses/", views.enrolledCourses, name="enrolledCourses"),
    path("enrolledCourses/courseContent/<int:id>", views.courseContent, name="courseContent"),
    path("search", views.search, name="search"),
    path("addComment/<int:id>", views.addComment, name="addComment"),
    path("manage", views.manage, name="manage"),
    path("deleteCourse/<int:id>", views.deleteCourse, name="deleteCourse"),
    path("editCourse/<int:id>", views.editCourse, name="editCourse"),
    path("profile", views.profile, name="profile"),
    path("addLesson/<int:id>", views.addLesson, name="addLesson"),
    path("deleteLesson/<int:id>", views.deleteLesson, name="deleteLesson"),
    path("editLesson/<int:id>", views.editLesson, name="editLesson"),
    path("addVid/<int:id>", views.addVid, name="addVid"),
    path("deleteVid/<int:id>", views.deleteVid, name="deleteVid"),
    path("editVid/<int:id>", views.editVid, name="editVid"),
]
