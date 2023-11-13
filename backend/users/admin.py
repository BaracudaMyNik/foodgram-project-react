from django.contrib import admin

from backend.settings import LIST_PER_PAGE

from .models import Subscription, User

# from gjango.contrib.auth.models import Group
# from rest_framework.authtoken.models import TokenProxy


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Класс настройки раздела пользователей."""

    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'is_admin'
        # 'recipes_count',
        # 'follows_count'
    )
    '''
    # выводим кол-во рецептов и подписчиков в листе пользователей

    @admin.display(description='Количество рецептов у пользователя')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков у пользователя')
    def follows_count(self, obj):
        return obj.recipes.count()
    '''

    empty_value_display = 'значение отсутствует'
    list_editable = ('is_admin',)
    list_filter = ('username', 'email')
    list_per_page = LIST_PER_PAGE
    search_fields = ('username',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Класс настройки раздела подписок."""

    list_display = (
        'pk',
        'author',
        'subscriber',
    )

    list_editable = ('author', 'subscriber')
    list_filter = ('author',)
    list_per_page = LIST_PER_PAGE
    search_fields = ('author',)


admin.site.site_title = 'Администрирование Foodgram'
admin.site.site_header = 'Администрирование Foodgram'
# admin.site.unregister(Group)
# admin.site.unregister(TokenProxy)
