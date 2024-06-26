from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Recipe, Comment, UserProfile
from .forms import RecipeForm, RecipeSearchForm
from .forms import CommentForm, RatingForm
from .forms import SignUpForm
from .forms import UserProfileForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Recipe, Comment
from .forms import CommentForm, RatingForm

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
    return render(request, 'profiles/user_profile.html', context)


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

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)  # Важно добавить request.FILES
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()
            return redirect('recipe_detail', id=recipe.id)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})

def recipe_detail(request, id):
    recipe = get_object_or_404(Recipe, id=id)
    comments = recipe.comments.all()

    # This will hold forms that might not be submitted yet.
    comment_form = CommentForm(request.POST or None)
    rating_form = RatingForm(request.POST or None)

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                return redirect('recipe_detail', id=recipe.id)
            else:
                # If the comment form is not valid, fall through to the render at the end of the view
                pass
        elif 'rate_recipe' in request.POST:
            if rating_form.is_valid():
                new_rating = int(rating_form.cleaned_data['rating'])
                recipe.update_rating(new_rating)
                return redirect('recipe_detail', id=recipe.id)
            else:
                # If the rating form is not valid, fall through to the render at the end of the view
                pass
        else:
            # In case there are other POST actions that are not handled
            return HttpResponse("Unhandled POST request.", status=400)

    # If not a POST request or no form was submitted, show the details page
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form
    })


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

@login_required
def update_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # Убедитесь, что 'profile' существует в urls.py
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'profiles/update_profile.html', {'form': form})


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()
