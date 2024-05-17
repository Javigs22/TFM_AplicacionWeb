from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.initial_menu, name = "initial_menu"),
    path("register", views.register, name = "register"),
    path('verificar-correo', views.verification, name = "verification"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("postlogin/", views.postlogin, name = "postlogin"),
    path("home/", views.home, name = "home"),
    path('createTest/', views.createTest, name='createTest'),
    path('questions/', views.questions, name='questions'),
    path('showTests/', views.showTests, name='showTests'),
    path('chooseSubject/', views.chooseSubject, name='chooseSubject'),
    path('questions/process_questions/', views.processSelectedQuestion),
    path('showTests/process_questions/', views.processSelectedQuestion),
    path('showTests/addQuestion/', views.addQuestion),
    path('showTests/updateTest/', views.updateTest),
    path('showTests/deleteTest/', views.deleteTest),
    path('createSubject/', views.createSubject, name='createSubject'),
    path('logout_extension/', views.logout_extension, name='logging_out'),
]

