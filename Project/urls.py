from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('home/', views.home, name='home'),
    path('timetable/<int:pk>/', views.view_timetable, name='view_timetable'),
    path('assign/<int:pk>/', views.assign_subject, name='assign_subject'),
    path('manage/<int:class_id>/', views.manage_page, name='manage_page'),
    path('logout/', views.logout_view, name='logout'),
]
