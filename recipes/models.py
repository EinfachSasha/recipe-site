from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Категория')

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Ингредиент')
    category = models.ForeignKey(Category, related_name='ingredients', on_delete=models.CASCADE, verbose_name='Категория')

    def __str__(self):
        return self.name



class Recipe(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    photo = models.ImageField(upload_to='recipes_photos/', blank=True, null=True, verbose_name='Фото')
    cuisine = models.CharField(max_length=100, null=True, blank=True, choices=(
        ('Итальянская', 'Итальянская'),
        ('Французская', 'Французская'),
        ('Грузинская', 'Грузинская'),
        ('Русская', 'Русская'),
        ('Китайская', 'Китайская'),
        ('Другое', 'Другое'),
    ), verbose_name='Кухня')
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes', blank=True, verbose_name='Ингредиенты')

    likes = models.ManyToManyField(User, related_name='recipe_likes', verbose_name='Лайки')
    
    total_rating = models.IntegerField(default=0, verbose_name='Суммарный рейтинг')
    number_of_ratings = models.IntegerField(default=0, verbose_name='Количество оценок')
    
    def update_rating(self, new_rating):
        self.total_rating += new_rating
        self.number_of_ratings += 1
        self.save()

    def average_rating(self):
        if self.number_of_ratings > 0:
            return self.total_rating / self.number_of_ratings
        return 0


    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title
    
    

    
class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments', verbose_name='Рецепт')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True, verbose_name='Лайки')
    dislikes = models.ManyToManyField(User, related_name='comment_dislikes', blank=True, verbose_name='Дизлайки')

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return f'Комментарий от {self.author} к {self.recipe}'
    

    

