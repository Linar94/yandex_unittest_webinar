from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.index, name='index'),
    path('group/new/', views.group_new, name='group_new_url'),
    path('group/<int:pk>/edit/', views.group_edit, name='group_edit_url'),
    path("post/new/", views.new_post, name="new_post"),
]