from colorfield.fields import ColorField
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator
)
from django.db import models

from backend.settings import (
    INGRED_MAX_LENGHT,
    LENGTH_TEXT,
    RECIPE_NAME_MAX_LENGHT,
    TAG_COLOR_LENGHT,
    TAG_NAME_LENGHT,
    TAG_SLUG_LENGHT
)
from users.models import User

COLOR_PALETTE = [
    ("#00f040", "zavtrak", ),
    ("#f0b400", "obed", ),
    ("#ff0055", "uzhin", ),
]


class Tag(models.Model):
    """Класс тегов."""

    name = models.CharField(
        max_length=TAG_NAME_LENGHT,
        verbose_name='Hазвание',
        unique=True,
        db_index=True
    )

    color = ColorField(
        default='#00f040',
        choices=COLOR_PALETTE,
        max_length=TAG_COLOR_LENGHT,
        verbose_name='цвет',
        unique=True
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_LENGHT,
        verbose_name='slug',
        unique=True,
        validators=[RegexValidator(
            regex=r'^[-a-zA-Z0-9_]+$',
            message='Слаг тега содержит недопустимый символ'
        )]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.slug[:LENGTH_TEXT]


class Ingredient(models.Model):
    """Ингредиенты."""

    name = models.CharField(
        max_length=INGRED_MAX_LENGHT,
        verbose_name='Hазвание',
        db_index=True
    )
    measurement_unit = models.CharField(
        max_length=INGRED_MAX_LENGHT,
        verbose_name='единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name[:LENGTH_TEXT]


class Recipe(models.Model):
    """Рецепты."""

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        related_name='recipes',
        verbose_name='ингредиенты'

    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='изображение'
    )
    name = models.CharField(
        max_length=RECIPE_NAME_MAX_LENGHT,
        verbose_name='Hазвание',
        validators=[RegexValidator(
            regex=r'^[а-яА-ЯЁё\s]+$',
            message='Не допустимое название!'
        )],
        db_index=True
    )
    text = models.TextField(verbose_name='описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1'
            ),
            MaxValueValidator(
                360,
                message='Время приготовления не может быть больше 360'
            ),
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации',
        db_index=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name[:LENGTH_TEXT]


class IngredientAmount(models.Model):
    """Связка рецептов и ингредиентов.
    Количества ингредиента."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиента не может быть нулевым'
            ),
            MaxValueValidator(
                1000,
                message='Количество ингредиента не может быть больше тысячи'
            )
        ],
    )

    class Meta:
        verbose_name = 'Соответствие ингредиента и рецепта'
        verbose_name_plural = 'Таблица соответствия ингредиентов и рецептов'
        ordering = ('recipe',)
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.recipe} содержит ингредиент/ты {self.ingredient}'


class UserRecipeModel(models.Model):
    """Абстрактная модель"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('recipe',)
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique favourite')]


class Favorite(UserRecipeModel):
    """Класс для добавления рецептов в избранное."""
    class Meta:
        default_related_name = 'favoriting'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'


class ShoppingCart(UserRecipeModel):
    """Класс для составления списка покупок."""
    class Meta:
        default_related_name = 'shopping_cart'
        verbose_name = 'Рецепт пользователя для списка покупок'
        verbose_name_plural = 'Рецепты пользователей для списка покупок'

    def __str__(self):
        return f'{self.recipe.name} в списке покупок у {self.user.username}'
