from django import forms
from .models import Recipe, Comment, Ingredient

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Обязательное поле. Укажите действующий адрес электронной почты.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        
class RecipeSearchForm(forms.Form):
    ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    exclude_ingredients = forms.ModelMultipleChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Исключить ингредиенты'
    )

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'cuisine', 'ingredients']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple
        }

class RatingForm(forms.Form):
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], label="Оценка")
