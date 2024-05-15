from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe, Comment
from .forms import RecipeForm, RecipeSearchForm
from .forms import CommentForm, RatingForm
from .forms import SignUpForm

def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Перенаправление на страницу входа после регистрации
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def user_profile(request):
    # Получаем рецепты, созданные пользователем
    user_recipes = Recipe.objects.filter(author=request.user)
    # Получаем рецепты, которые пользователь лайкал
    liked_recipes = request.user.recipe_likes.all()

    context = {
        'user_recipes': user_recipes,
        'liked_recipes': liked_recipes
    }
    return render(request, 'recipes/user_profile.html', context)


def recipe_list(request):
    Recipe.objects.filter(cuisine__isnull=True).update(cuisine='Русская')
    query = request.GET.get('query', '')
    cuisine = request.GET.get('cuisine', '')
    recipes = Recipe.objects.all()
    if query:
        recipes = recipes.filter(title__icontains=query)
    if cuisine:
        recipes = recipes.filter(cuisine__iexact=cuisine)
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})


def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    comments = recipe.comments.all()

    # Обработка формы комментариев
    if 'submit_comment' in request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            return redirect('recipe_detail', id=recipe.id)
    else:
        comment_form = CommentForm()

    # Обработка формы рейтинга
    if 'rate_recipe' in request.POST:
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            recipe.update_rating(int(rating_form.cleaned_data['rating']))
            return redirect('recipe_detail', id=recipe.id)
    else:
        rating_form = RatingForm()

    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form
    })

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user  # Автоматически устанавливаем автора рецепта
            recipe.save()
            form.save_m2m()
            return redirect('recipe_detail', id=recipe.id)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def recipe_update(request, id):
    recipe = Recipe.objects.get(id=id)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', id=recipe.id)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form})

@login_required
def like_recipe(request, id):
    recipe = Recipe.objects.get(id=id)
    if recipe.likes.filter(id=request.user.id).exists():
        recipe.likes.remove(request.user)
    else:
        recipe.likes.add(request.user)
    return redirect('recipe_detail', id=id)

def recipe_search(request):
    form = RecipeSearchForm(request.GET)
    recipes = Recipe.objects.all()

    if request.GET.get('ingredients'):
        recipes = recipes.filter(ingredients__in=request.GET.getlist('ingredients'))

    if request.GET.get('exclude_ingredients'):
        recipes = recipes.exclude(ingredients__in=request.GET.getlist('exclude_ingredients'))

    return render(request, 'recipes/search.html', {'form': form, 'recipes': recipes})



def like_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('recipe_detail', id=comment.recipe.id)

def dislike_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.dislikes.filter(id=request.user.id).exists():
        comment.dislikes.remove(request.user)
    else:
        comment.dislikes.add(request.user)
    return redirect('recipe_detail', id=comment.recipe.id)
