from django.urls import path, include
from . import views
from .views import signup, user_profile, update_profile

from django.contrib import admin
from django.conf.urls import handler404
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static

def custom_page_not_found(request, exception):
    return render(request, '404.html', status=404)

# Set the handler404 to your custom 404 view
handler404 = custom_page_not_found

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', signup, name='signup'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipe/<int:id>/', views.recipe_detail, name='recipe_detail'),
    path('create/', views.recipe_create, name='recipe_create'),
    path('update/<int:id>/', views.recipe_update, name='recipe_update'),
    path('like/<int:id>/', views.like_recipe, name='like_recipe'),
    path('like_comment/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('dislike_comment/<int:comment_id>/', views.dislike_comment, name='dislike_comment'),
    path('accounts/profile/', user_profile, name='user_profile'),
    path('accounts/profile/update/', update_profile, name='update_profile'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
