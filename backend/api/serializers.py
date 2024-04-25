import base64

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (ImageField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField,
                                        SerializerMethodField, ValidationError)

from recipes.models import (ALREADY_FOLLOW, Favorite, Follow, Ingredient,
                            IngredientAmount, Recipe, ShoppingCart, Tag)

User = get_user_model()

ERROR_NO_INGREDIENT_ID = 'Ingredient ID is required'
ERROR_INGREDIENT_DB = 'Ingredient with ID {} does not exist in the database'
ERROR_NO_INGREDIENT = 'At least one ingredient must be specified!'
ERROR_DUPLICATE_INGREDIENT = ('Ingredient with ID {} '
                              'already exists in the recipe')
ERROR_AMOUNT_ZERO = ('Ingredient with ID {} must have a quantity '
                     'greater than zero!')
ERROR_NO_TAGS = 'At least one tag must be selected!'
ERROR_DUPLICATE_TAGS = 'Tags must be unique!'
ERROR_FOLLOW = 'Cannot follow yourself'


class Base64ImageField(ImageField):
    """
    Custom ImageField to handle base64 encoded images.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Custom user creation serializer.
    """
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """
    Custom user serializer.
    """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        """
        Check if the requesting user is subscribed to the author.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, author=author).exists()
        return False


class TagSerializer(ModelSerializer):
    """
    Serializer for tags.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(ModelSerializer):
    """
    Serializer for ingredients.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(ModelSerializer):
    """
    Serializer for ingredient amounts.
    """
    id = IntegerField()

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class SimpleRecipeSerializer(ModelSerializer):
    """
    Serializer for simple recipe representation.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class RecipeSerializer(ModelSerializer):
    """
    Serializer for recipe representation.
    """
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_ingredients(self, recipe):
        """
        Get ingredients for the recipe.
        """
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredient_amounts__amount'),
        )
        return ingredients

    def get_is_favorited(self, recipe):
        """
        Check if the requesting user has favorited the recipe.
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=recipe).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        """
        Check if the recipe is in the requesting user's shopping cart.
        """
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).exists()
        return False


class RecipeCreateSerializer(ModelSerializer):
    """
    Serializer for creating recipes.
    """
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        """
        Validate recipe data.
        """
        ingredients = data.get('ingredients', None)
        if not ingredients or len(ingredients) < 1:
            raise ValidationError(ERROR_NO_INGREDIENT)
        ingredient_objects = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            amount = ingredient.get('amount')
            if not ingredient_id:
                raise ValidationError(ERROR_NO_INGREDIENT_ID)
            try:
                ingredient_obj = Ingredient.objects.get(pk=ingredient_id)
            except ObjectDoesNotExist:
                raise ValidationError(
                    ERROR_INGREDIENT_DB.format(ingredient_id))
            if ingredient_obj in ingredient_objects:
                raise ValidationError(
                    ERROR_DUPLICATE_INGREDIENT.format(ingredient_id))
            if amount <= 0:
                raise ValidationError(
                    ERROR_AMOUNT_ZERO.format(ingredient_id))
            ingredient_objects.append(ingredient_obj)

        tags = data.get('tags', None)
        if not tags or len(tags) < 1:
            raise ValidationError({'tags': ERROR_NO_TAGS})
        if len(set(tags)) != len(tags):
            raise ValidationError({'tags': ERROR_DUPLICATE_TAGS})
        return data

    def create_ingredient_amount(self, ingredients, recipe):
        """
        Create ingredient amounts for the recipe.
        """
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """
        Create a new recipe.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredient_amount(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        """
        Update an existing recipe.
        """
        tags = validated_data.pop('tags')
        recipe.tags.clear()
        recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        recipe.ingredients.clear()
        self.create_ingredient_amount(ingredients, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        """
        Convert instance to representation.
        """
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data


class FollowSerializer(CustomUserSerializer):
    """
    Serializer for user follows.
    """
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_recipes(self, author):
        """
        Get recipes authored by the user.
        """
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        recipes = (author.recipes.all()[:int(limit)]
                   if limit
                   else author.recipes.all())
        return SimpleRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, author):
        """
        Get the count of recipes authored by the user.
        """
        return author.recipes.count()

    def validate(self, data):
        """
        Validate follow data.
        """
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(ALREADY_FOLLOW)
        if user == author:
            raise ValidationError(ERROR_FOLLOW)
        return data
