from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

USER_NAME_LENGTH = 150
EMAIL_LENGTH = 254
TEXT_LENGTH = 50
TITLE_LENGTH = 255
RECIPE_NAME_LENGTH = 200
NAME_LENGTH = 256
COLOR_LENGTH = 7
SLUG_LENGTH = 50
MEASUREMENT_UNIT_LENGTH = 50
QUANTITY_DIGITS = 6
QUANTITY_DECIMAL_PLACES = 2

EMAIL_ADDRESS = 'email address'
FIRST_NAME = 'first name'
LAST_NAME = 'last name'
USER = 'user'
USERS = 'users'
TAG = 'tag'
TAGS = 'tags'
TAG_COLOR = 'tag color code'
ERROR_TAG_COLOR = 'Color must be in HEX format'
TAG_SLUG = 'tag slug'
INGREDIENT = 'ingredient'
INGREDIENTS = 'ingredients'
INGREDIENT_MEASUREMENT_UNIT = 'ingredient measurement unit'
ERROR_INGREDIENT_MESSAGE = 'such ingredient already exists'
RECIPE_AUTHOR = 'recipe author'
RECIPE = 'recipe'
RECIPES = 'recipes'
RECIPE_IMAGE = 'recipe image'
RECIPE_DESCRIPTION = 'recipe description'
RECIPE_INGREDIENTS = 'recipe ingredients'
RECIPE_TAGS = 'recipe tags'
RECIPE_COOKING_TIME = 'recipe cooking time in minutes'
ERROR_COOKING_TIME = 'cooking time cannot be less than one minute'
INGREDIENT_AMOUNT = 'ingredient amount'
RECIPE_IN_SHOPPING_CART = 'recipe already in shopping cart'
RECIPE_IN_FAVORITE = 'recipe already in favorites'
ALREADY_FOLLOW = 'you already follow this author'
FOLLOWS = 'follows'


class User(AbstractUser):
    """
    Custom user model with email as username.
    """
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    email = models.EmailField(
        EMAIL_ADDRESS,
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        FIRST_NAME,
        max_length=USER_NAME_LENGTH,
    )
    last_name = models.CharField(
        LAST_NAME,
        max_length=USER_NAME_LENGTH,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = USER
        verbose_name_plural = USERS

    def __str__(self):
        return self.username[:TEXT_LENGTH]


class Tag(models.Model):
    """
    Model representing a tag.
    """
    name = models.CharField(
        TAG,
        max_length=NAME_LENGTH,
        unique=True
    )
    color = models.CharField(
        TAG_COLOR,
        max_length=COLOR_LENGTH,
        validators=[RegexValidator(
            regex='^#([A-Fa-f0-9]{6})$', message=ERROR_TAG_COLOR)
        ]
    )
    slug = models.SlugField(
        TAG_SLUG,
        unique=True,
        max_length=SLUG_LENGTH
    )

    class Meta:
        ordering = ('id',)
        verbose_name = TAG
        verbose_name_plural = TAGS

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class Ingredient(models.Model):
    """
    Model representing an ingredient.
    """
    name = models.CharField(
        INGREDIENT,
        max_length=NAME_LENGTH
    )
    measurement_unit = models.CharField(
        INGREDIENT_MEASUREMENT_UNIT,
        max_length=MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        default_related_name = 'ingredients'
        ordering = ('id',)
        verbose_name = INGREDIENT
        verbose_name_plural = INGREDIENTS
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name=ERROR_INGREDIENT_MESSAGE
            ),
        )

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class Recipe(models.Model):
    """
    Model representing a recipe.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=RECIPE_AUTHOR
    )
    name = models.CharField(
        RECIPE,
        max_length=RECIPE_NAME_LENGTH
    )
    image = models.ImageField(
        RECIPE_IMAGE,
        upload_to='recipes/'
    )
    text = models.TextField(
        RECIPE_DESCRIPTION
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name=RECIPE_INGREDIENTS,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=RECIPE_TAGS
    )
    cooking_time = models.PositiveIntegerField(
        RECIPE_COOKING_TIME,
        validators=(MinValueValidator(1, message=ERROR_COOKING_TIME),)
    )

    class Meta:
        ordering = ('-id',)
        default_related_name = 'recipes'
        verbose_name = RECIPE
        verbose_name_plural = RECIPES

    def __str__(self):
        return self.name[:TEXT_LENGTH]


class IngredientAmount(models.Model):
    """
    Model representing the amount of an ingredient in a recipe.
    """
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=INGREDIENT
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=RECIPE
    )
    amount = models.FloatField(
        INGREDIENT_AMOUNT,
    )

    class Meta:
        default_related_name = 'ingredient_amounts'

    def __str__(self):
        return (f'{self.ingredient.name}: '
                f'{self.amount} {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """
    Model representing a favorite recipe for a user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=USER
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=RECIPE
    )

    class Meta:
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name=RECIPE_IN_FAVORITE),
        )


class ShoppingCart(models.Model):
    """
    Model representing a recipe in a user's shopping cart.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=USER
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=RECIPE
    )

    class Meta:
        default_related_name = 'cart_items'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name=RECIPE_IN_SHOPPING_CART),
        )


class Follow(models.Model):
    """
    Model representing a user following another user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=USER
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=USER
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name=ALREADY_FOLLOW),
        )

    def __str__(self):
        return f'{self.user} {FOLLOWS} {self.author}'[:50]
