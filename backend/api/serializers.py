from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField,
                                        SerializerMethodField, ValidationError)

from . import constants, fields
from recipes.constants import ALREADY_FOLLOW
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)

User = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
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


class UserSerializer(UserSerializer):
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
        return (user
                and user.is_authenticated
                and author.following.filter(user=user).exists())


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
    amount = IntegerField(min_value=1)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate_id(self, id):
        if not Ingredient.objects.filter(pk=id).exists():
            raise ValidationError(constants.ERROR_NO_INGREDIENT_ID)
        return id


class IngredientRecipeSerializer(ModelSerializer):
    """
    Serializer for ingredient in a recipe.
    """

    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')


class SimpleRecipeSerializer(ModelSerializer):
    """
    Serializer for simple recipe representation.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(ModelSerializer):
    """
    Serializer for recipe representation.
    """

    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(
        source='ingredient_amounts', many=True, read_only=True,)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = fields.Base64ImageField()

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

    def get_is_favorited(self, recipe):
        """
        Check if the requesting user has favorited the recipe.
        """
        user = self.context.get('request').user
        return (user
                and user.is_authenticated
                and recipe.favorites.filter(user=user).exists())

    def get_is_in_shopping_cart(self, recipe):
        """
        Check if the recipe is in the requesting user's shopping cart.
        """
        user = self.context.get('request').user
        return (user
                and user.is_authenticated
                and recipe.cart_items.filter(user=user).exists())


class RecipeCreateSerializer(ModelSerializer):
    """
    Serializer for creating recipes.
    """

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    image = fields.Base64ImageField()

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
        ingredients = data.get('ingredients')
        if not ingredients:
            raise ValidationError(constants.ERROR_NO_INGREDIENT)
        ids = tuple(ingredient.get('id') for ingredient in ingredients)
        unique_ids = set(ids)
        if len(unique_ids) != len(ids):
            raise ValidationError(
                constants.ERROR_DUPLICATE_INGREDIENT.format(
                    (id for id in unique_ids if ids.count(id) > 1)))

        tags = data.get('tags')
        if not tags:
            raise ValidationError({'tags': constants.ERROR_NO_TAGS})
        if len(set(tags)) != len(tags):
            raise ValidationError({'tags': constants.ERROR_DUPLICATE_TAGS})
        return data

    def create_ingredient_amount(self, ingredients, recipe):
        """
        Create ingredient amounts for the recipe.
        """
        IngredientAmount.objects.bulk_create(
            IngredientAmount(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount')
            ) for ingredient in ingredients
        )

    def create(self, validated_data):
        """
        Create a new recipe.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **validated_data)
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


class FollowCreateSerializer(ModelSerializer):
    """
    Serializer for creating user follows.
    """

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data):
        """
        Validate follow data.
        """
        author = data.get('author')
        user = data.get('user')
        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(ALREADY_FOLLOW)
        if user == author:
            raise ValidationError(constants.ERROR_FOLLOW)
        return data

    def to_representation(self, instance):
        return FollowSerializer(instance.author, context=self.context).data


class FollowSerializer(UserSerializer):
    """
    Serializer for user follows.
    """

    recipes = SerializerMethodField()
    recipes_count = ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)

    def get_recipes(self, author):
        """
        Get recipes authored by the user.
        """
        request = self.context.get('request')
        recipes = author.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return SimpleRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data


class FavoriteSerializer(ModelSerializer):
    """
    Serializer for favorites.
    """

    class Meta:
        model = Favorite
        fields = '__all__'

    def to_representation(self, instance):
        return SimpleRecipeSerializer(instance.recipe).data


class ShoppingCartSerializer(FavoriteSerializer):
    """
    Serializer for shopping cart items.
    """

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
