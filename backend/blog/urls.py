from django.urls import path
from . import views

# Namespace allows us to use 'blog:post_list' in templates
# This prevents URL name conflicts when you have multiple apps
app_name = 'blog'

urlpatterns = [
    path('posts/', views.post_list, name='post_list'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
]