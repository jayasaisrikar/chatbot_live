from django.contrib import admin
from django.urls import path
from chatbot_app import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add_articles/<int:num_articles>/', views.add_articles, name='add_articles'),
    path('chatbot/', views.chatbot, name='chatbot'),
]
