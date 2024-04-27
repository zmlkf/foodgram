from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import constants
from .models import (Favorite, Follow, Ingredient, IngredientAmount, Recipe,
                     ShoppingCart, Tag, User)


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 1
    min_num = constants.MIN_TAG_AMOUNT


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    extra = 1
    min_num = constants.MIN_INGREDIENT_AMOUNT


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name',
                    'last_name', 'recipe_count', 'follower_count')
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')

    @admin.display(description='Recipes')
    def recipe_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Followers')
    def follower_count(self, obj):
        return obj.follower.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientAmountInline, TagInline)
    list_display = ('name', 'author', 'favorite_count')
    list_filter = ('author', 'name', 'tags__name')
    search_fields = ('name', 'author__username')

    @admin.display(description='Favorites')
    def favorite_count(self, obj):
        return obj.favorites.count()


@admin.register(IngredientAmount)
class IngredientAmountAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'recipe', 'amount')
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient__name', 'recipe__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user__username', 'author__username')
