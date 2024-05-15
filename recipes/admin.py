from django.contrib import admin
from .models import Ingredient, Category, Recipe

admin.site.register(Ingredient)
admin.site.register(Category)
admin.site.register(Recipe)
# Register your models here.
