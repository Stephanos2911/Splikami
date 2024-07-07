from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),  # Default route
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('knowledge/', views.knowledge, name='knowledge'),
    path('education/', views.education, name='education'),
    path('technology/', views.technology, name='technology'),
    path('guidance/', views.guidance, name='guidance'),
    path('information/', views.information, name='information'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('splikami_online/', views.splikami_online, name='splikami_online'),
    path('contact/', views.contact, name='contact'),
]
