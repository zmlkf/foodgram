from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import (decorators, exceptions, permissions, status,
                            viewsets)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import (FollowSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          SimpleRecipeSerializer, TagSerializer)
from recipes.models import (Favorite, Follow, Ingredient, IngredientAmount,
                            Recipe, ShoppingCart, Tag)

User = get_user_model()

RECIPE_ALREADY_IN_LIST = 'Recipe already added to {}'
RECIPE_DOES_NOT_EXIST = 'Recipe with ID {} does not exist in the database'
ERROR_DELETE_SUBSCRIPTION = 'Subscription does not exist'
RECIPE_NOT_IN_LIST = 'Recipe was not added to {}'


class CustomUserViewSet(UserViewSet):
    """
    Custom user view set with additional actions.
    """

    @decorators.action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        """
        Retrieve user's own profile.
        """
        return Response(
            self.get_serializer(request.user).data,
            status=status.HTTP_200_OK
        )

    @decorators.action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """
        Subscribe or unsubscribe from another user.
        """
        user = request.user
        author = get_object_or_404(User, pk=self.kwargs.get('id'))
        if request.method == 'POST':
            serializer = FollowSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        try:
            Follow.objects.get(user=user, author=author).delete()
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(ERROR_DELETE_SUBSCRIPTION)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """
        List user's subscriptions.
        """
        return self.get_paginated_response(
            FollowSerializer(self.paginate_queryset(
                User.objects.filter(following__user=request.user)),
                many=True,
                context={'request': request}
            ).data
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View set for tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View set for ingredients.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    View set for recipes.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'delete', 'patch')

    def perform_create(self, serializer):
        """
        Assign current user as the author when creating a recipe.
        """
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """
        Use different serializer for creating and retrieving recipes.
        """
        return (RecipeSerializer
                if self.request.method in permissions.SAFE_METHODS
                else RecipeCreateSerializer)

    @decorators.action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """
        Add or remove a recipe from favorites.
        """
        if request.method == 'POST':
            return self.add_to_list(Favorite, request.user, pk)
        return self.remove_from_list(Favorite, request.user, pk)

    @decorators.action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """
        Add or remove a recipe from shopping cart.
        """
        if request.method == 'POST':
            return self.add_to_list(ShoppingCart, request.user, pk)
        return self.remove_from_list(ShoppingCart, request.user, pk)

    def add_to_list(self, model_class, user, pk):
        """
        Add recipe to the specified list.
        """
        try:
            recipe = Recipe.objects.get(pk=pk)
            model_class.objects.create(user=user, recipe=recipe)
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(RECIPE_DOES_NOT_EXIST.format(pk))
        except IntegrityError:
            raise exceptions.ValidationError(RECIPE_ALREADY_IN_LIST.format(
                model_class.__class__.__name__))
        return Response(
            SimpleRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    def remove_from_list(self, model_class, user, pk):
        """
        Remove recipe from the specified list.
        """
        try:
            model_class.objects.get(
                user=user,
                recipe=get_object_or_404(Recipe, pk=pk)
            ).delete()
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(RECIPE_NOT_IN_LIST.format(
                model_class.__class__.__name__))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Generate and download shopping cart as a text file.
        """
        shopping_cart = IngredientAmount.objects.filter(
            recipe__cart_items__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(ingredient_total=Sum('amount'))
        content = '\n'.join(((f'- {item.get("ingredient__name")} '
                              f'({item.get("ingredient__measurement_unit")}) '
                              f'— {item.get("ingredient_total")}')
                            for item in shopping_cart))
        response = HttpResponse(
            content, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_cart.txt"')
        return response
