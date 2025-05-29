from django.urls import path
from . import views
from .views import chat_api_view


urlpatterns = [
    path('', views.character_list, name='character_list'),
    path('chat/', views.chat_view, name='chat'),
    path('admin/characters/', views.admin_character_list, name='admin_character_list'),
    path('admin/characters/add/', views.admin_character_form, name='add_character'),
    path('admin/characters/<int:id>/edit/', views.admin_character_form, name='edit_character'),
    path('api/chat/', chat_api_view, name='chat_api'),
]
