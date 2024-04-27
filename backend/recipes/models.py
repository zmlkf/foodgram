from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from . import constants
from .utils import generate_random_color
from .validators import validate_username


class User(AbstractUser):
    """
    Custom user model with email as username.
    """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')
    username = models.CharField(
        constants.USERNAME,
        max_length=constants.MAX_LENGTH_USERNAME,
        help_text=(constants.USERNAME_HELP_TEXT),
        unique=True,
        validators=(validate_username,),
    )
    email = models.EmailField(
        constants.EMAIL_ADDRESS,
        max_length=constants.EMAIL_LENGTH,
        unique=True,
    )
    password = models.CharField(
        constants.PASSWORD,
        max_length=constants.PASSWORD_LENGTH
    )
    first_name = models.CharField(
        constants.FIRST_NAME,
        max_length=constants.USER_NAME_LENGTH,
    )
    last_name = models.CharField(
        constants.LAST_NAME,
        max_length=constants.USER_NAME_LENGTH,
    )

    class Meta:
        ordering = ('username',)
        verbose_name = constants.USER
        verbose_name_plural = constants.USERS

    def __str__(self):
        return self.username[:constants.TEXT_LENGTH]


class Tag(models.Model):
    """
    Model representing a tag.
    """

    name = models.CharField(
        constants.TAG,
        max_length=constants.NAME_TAG_LENGTH,
        unique=True
    )
    color = ColorField(
        format='hex',
        verbose_name=constants.TAG_COLOR,
        max_length=constants.COLOR_LENGTH,
        unique=True,
        default=generate_random_color
    )
    slug = models.SlugField(
        constants.TAG_SLUG,
        unique=True,
        max_length=constants.SLUG_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = constants.TAG
        verbose_name_plural = constants.TAGS

    def __str__(self):
        return self.name[:constants.TEXT_LENGTH]


class Ingredient(models.Model):
    """
    Model representing an ingredient.
    """

    name = models.CharField(
        constants.INGREDIENT,
        max_length=constants.NAME_INGREDIENT_LENGTH
    )
    measurement_unit = models.CharField(
        constants.INGREDIENT_MEASUREMENT_UNIT,
        max_length=constants.MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        default_related_name = 'ingredients'
        ordering = ('name',)
        verbose_name = constants.INGREDIENT
        verbose_name_plural = constants.INGREDIENTS
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name=constants.ERROR_INGREDIENT_MESSAGE
            ),
        )

    def __str__(self):
        return self.name[:constants.TEXT_LENGTH]


class Recipe(models.Model):
    """
    Model representing a recipe.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=constants.RECIPE_AUTHOR
    )
    name = models.CharField(
        constants.RECIPE,
        max_length=constants.RECIPE_NAME_LENGTH
    )
    image = models.ImageField(
        constants.RECIPE_IMAGE,
        upload_to='recipes/'
    )
    text = models.TextField(
        constants.RECIPE_DESCRIPTION
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name=constants.RECIPE_INGREDIENTS,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name=constants.RECIPE_TAGS
    )
    cooking_time = models.PositiveIntegerField(
        constants.RECIPE_COOKING_TIME,
        validators=(MinValueValidator(
            constants.MIN_COOKING_TIME,
            message=constants.ERROR_COOKING_TIME.format(
                constants.MIN_COOKING_TIME)),
        )
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=constants.PUB_DATE
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        verbose_name = constants.RECIPE
        verbose_name_plural = constants.RECIPES

    def __str__(self):
        return self.name[:constants.TEXT_LENGTH]


class IngredientAmount(models.Model):
    """
    Model representing the amount of an ingredient in a recipe.
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name=constants.INGREDIENT
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=constants.RECIPE
    )
    amount = models.PositiveIntegerField(
        constants.INGREDIENT_AMOUNT,
        validators=(MinValueValidator(
            constants.MIN_INGREDIENT_AMOUNT,
            message=constants.ERROR_INGREDIENT_AMOUNT.format(
                constants.MIN_INGREDIENT_AMOUNT)),
        )
    )

    class Meta:
        verbose_name = constants.INGREDIENT_AMOUNT
        verbose_name_plural = constants.INGREDIENT_AMOUNTS
        default_related_name = 'ingredient_amounts'
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name=constants.INGREDIENT_IN_RECIPE.format(
                    'ingredient.name', 'recipe.name')
            ),
        )

    def __str__(self):
        return (f'{self.ingredient.name[:constants.TEXT_LENGTH]}: '
                f'{self.amount} {self.ingredient.measurement_unit}')


class Favorite(models.Model):
    """
    Model representing a favorite recipe for a user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=constants.USER
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=constants.RECIPE
    )

    class Meta:
        verbose_name = constants.FAVORITE
        verbose_name_plural = constants.FAVORITES
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=constants.ERROR_RECIPE_IN_FAVORITE
            ),
        )

    def __str__(self):
        return constants.RECIPE_IN_SHOPPING_CART.format(
            self.recipe[:constants.TEXT_LENGTH],
            self.user[:constants.TEXT_LENGTH]
        )


class ShoppingCart(models.Model):
    """
    Model representing a recipe in a user's shopping cart.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=constants.USER
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name=constants.RECIPE
    )

    class Meta:
        verbose_name = constants.SHOPPING_CART
        verbose_name_plural = constants.SHOPPING_CARTS
        default_related_name = 'cart_items'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name=constants.ERROR_RECIPE_IN_SHOPPING_CART),
        )

    def __str__(self):
        return constants.RECIPE_IN_SHOPPING_CART.format(
            self.recipe[:constants.TEXT_LENGTH],
            self.user[:constants.TEXT_LENGTH]
        )


class Follow(models.Model):
    """
    Model representing a user following another user.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=constants.USER
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=constants.USER
    )

    class Meta:
        verbose_name = constants.SUBSCRIPTION
        verbose_name_plural = constants.SUBSCRIPTIONS
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name=constants.ALREADY_FOLLOW),
        )

    def __str__(self):
        return constants.FOLLOWS.format(
            self.user[:constants.TEXT_LENGTH],
            self.author[:constants.TEXT_LENGTH]
        )
