# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Default route
    path("logout/", views.logout_view, name="logout_view"),
    path("login/", views.login_view, name="login_view"),
    path("register/", views.register_view, name="register_view"),
    path('contact_submit/', views.contact_submit, name='contact_submit'),
    path('aboutus/', views.aboutus, name='aboutus'),
    
    #education
    path('education/', views.education, name='education'),
    path('online_courses/', views.online_courses, name='online_courses'), 
    path('course/<int:course_id>/', views.open_course, name='open_course'),

    #archive
    path('archive/', views.archive, name='archive'), 
    path('archive/document/<int:id>/', views.view_document, name='view_document'), 
    path('archive/document/<int:id>/page/<int:page>/', views.view_document, name='view_document_page'), #view specific page
    path('archive/search/', views.archive_search, name='archive_search'),
    
    #events
    path('events/', views.events, name='events'),
    path('event/<int:event_id>/add-to-calendar/', views.generate_ics, name='generate_ics'),
]