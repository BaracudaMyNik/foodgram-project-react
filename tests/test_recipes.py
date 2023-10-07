import json
import pytest
import re

from recipes.models import Favorite, Recipe, ShoppingCart


class TestRecipes:
    url = '/api/recipes/'
    fields_create_update = ['id', 'ingredients', 'tags', 'author', 'image',
                            'is_favorited', 'is_in_shopping_cart', 'name',
                            'text', 'cooking_time']

    @pytest.mark.django_db(transaction=True)
    def test_recipes_list_and_detail(self, client, user_client, another_user,
                                     recipe, tag, tag_2, ingredient,
                                     ingredient_2, amount, amount_2):
        url_detail = f'{self.url}{str(recipe.id)}/'
        code_expected = 200
        response = client.get(self.url, content_type='application/json')
        response_auth = user_client.get(
            self.url,
            content_type='application/json'
        )
        response_detail = client.get(
            url_detail,
            content_type='application/json'
        )
        response_detail_auth = user_client.get(
            url_detail,
            content_type='application/json'
        )
        data = response.json()
        data_auth = response_auth.json()
        response_data = data['results']
        response_data_auth = data_auth['results']
        response_data_detail = response_detail.json()
        response_data_detail_auth = response_detail_auth.json()
        test_recipe = response_data[0]

        image_expected = '/media/' + r'\w'
        tags_expected = [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            },
            {
                'id': tag_2.id,
                'name': tag_2.name,
                'color': tag_2.color,
                'slug': tag_2.slug
            }
        ]
        author_expected = {
            'email': another_user.email,
            'id': another_user.id,
            'username': another_user.username,
            'first_name': another_user.first_name,
            'last_name': another_user.last_name,
            'is_subscribed': another_user.is_subscribed
        }
        ingredients_expected = [
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': amount.amount
            },
            {
                'id': ingredient_2.id,
                'name': ingredient_2.name,
                'measurement_unit': ingredient_2.measurement_unit,
                'amount': amount_2.amount
            }
        ]
        data_expected = {
            'id': recipe.id,
            'is_favorited': recipe.is_favorited,
            'is_in_shopping_cart': recipe.is_in_shopping_cart,
            'name': recipe.name,
            'text': recipe.text,
            'cooking_time': recipe.cooking_time
        }

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{self.url}` '
            f'возвращается код {code_expected}'
        )
        assert response_data == response_data_auth, (
            f'Проверьте, что результат GET запроса на `{self.url}` '
            f'от анонима не отличается от результата запроса от '
            f'авторизованного пользователя'
        )
        assert response_data_detail == response_data_detail_auth, (
            f'Проверьте, что результат GET запроса на `{url_detail}` '
            f'от анонима не отличается от результата запроса от '
            f'авторизованного пользователя'
        )
        assert test_recipe == response_data_detail, (
            f'Проверьте, что при GET запросе на `{self.url}`, данные рецепта '
            f'с id `{str(recipe.id)}` не отличаются от данных в запросе на '
            f'`{url_detail}`'
        )
        assert type(data) == type(response_data_detail) == dict, (
            f'Проверьте, что при GET запросах на `{self.url}` и на '
            f'`{url_detail}` возвращается словарь'
        )
        assert len(response_data) == data['count'] == Recipe.objects.count(), (
            f'Проверьте, что при GET запросе на `{self.url}` '
            f'возвращается весь список пользователей'
        )
        assert re.match(image_expected, test_recipe['image']), (
            f'Убедитесь, что поле `image` содержит корректные данные'
        )
        for field in data_expected.items():
            assert field[0] in test_recipe.keys(), (
                f'Проверьте, что добавили поле `{field[0]}` в список полей '
                f'`fields` сериализатора модели Recipe'
            )
            assert field[1] == test_recipe[field[0]], (
                f'Убедитесь, что поле `{field[0]}` содержит корректные данные'
            )
        for field in author_expected.items():
            assert field[0] in test_recipe['author'].keys(), (
                f'Убедитесь, что поле `{field[0]}` присутствует в поле '
                f'`author` после успешного GET запроса'
            )
            assert field[1] == test_recipe['author'][field[0]], (
                f'Убедитесь, что поле `{field[0]}` в поле `author` '
                f'содержит корректные данные'
            )
        ingredients_tags_expected = {
            'ingredients': ingredients_expected,
            'tags': tags_expected
        }
        for checked, expected in ingredients_tags_expected.items():
            for i in range(len(expected)):
                for field in expected[i].items():
                    assert field[0] in test_recipe[checked][i].keys(), (
                        f'Убедитесь, что поле `{field[0]}` присутствует '
                        f'в поле `{checked}` после успешного GET запроса'
                    )
                    assert field[1] == test_recipe[checked][i][field[0]], (
                        f'Убедитесь, что значение поля `{field[0]}` в поле '
                        f'`{checked}` содержит корректные данные'
                    )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_detail_update_delete__not_found(self, user_client, user):
        url = f'{self.url}404/'
        code_expected = 404
        data_expected = {'detail': 'Страница не найдена.'}
        response_detail = user_client.get(url, content_type='application/json')
        response_update = user_client.put(url, content_type='application/json')
        response_delete = user_client.delete(
            url,
            content_type='application/json'
        )
        requests = {
            'GET': response_detail,
            'PUT': response_update,
            'DELETE': response_delete
        }

        for request, response in requests.items():
            assert response.status_code == code_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'на несуществующий рецепт, возвращается код '
                f'{code_expected}'
            )
            assert response.json() == data_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'на несуществующий рецепт, возвращается сообщение: '
                f'{data_expected["detail"]}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_create__not_auth(self, client, tag, ingredient, image):
        recipes_count = Recipe.objects.count()
        code_expected = 401
        ingredients_data = [
            {
                'id': ingredient.id,
                'amount': 2.5
            }
        ]
        data = {
            'ingredients': ingredients_data,
            'tags': [tag.id],
            'image': image,
            'name': 'Рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 1
        }
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}
        response = client.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` '
            f'от неавторизованного пользователя, возвращается статус '
            f'{code_expected}'
        )
        assert Recipe.objects.count() == recipes_count, (
            f'Проверьте, что при POST запросе на `{self.url}` '
            f'от неавторизованного пользователя, не создается новый рецепт'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` '
            f'от неавторизованного пользователя, возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_create__empty_request_data(self, user_client, recipe_2):
        urls = {
            'POST': self.url,
            'PUT': f'{self.url}{str(recipe_2.id)}/'
        }
        recipes_count = Recipe.objects.count()
        code_expected = 400
        empty_data = {}
        response_check_1 = user_client.get(
            urls['PUT'],
            content_type='application/json'
        )
        response_create = user_client.post(
            urls['POST'],
            data=json.dumps(empty_data),
            content_type='application/json'
        )
        response_update = user_client.put(
            urls['PUT'],
            data=json.dumps(empty_data),
            content_type='application/json'
        )
        response_check_2 = user_client.get(
            urls['PUT'],
            content_type='application/json'
        )
        requests = {
            'POST': response_create,
            'PUT': response_update
        }
        required_field = ['Обязательное поле.']
        data_expected = {
            'ingredients': required_field,
            'tags': required_field,
            'image': ['Ни одного файла не было отправлено.'],
            'name': required_field,
            'text': required_field,
            'cooking_time': required_field
        }
        for request, response in requests.items():
            assert response.status_code == code_expected, (
                f'Проверьте, что при {request} запросе на `{urls[request]}` '
                f'без данных, возвращается статус {code_expected}'
            )
            for field in data_expected.items():
                assert field[0] in response.json().keys(), (
                    f'Проверьте, что поле `{field[0]}` является обязательным'
                )
                assert field[1] == response.json()[field[0]], (
                    f'Убедитесь, что значение поля `{field[0]}` после '
                    f'{request} запроса без данных: `{field[1]}`'
                )
        assert Recipe.objects.count() == recipes_count, (
            f'Проверьте, что при POST запросе на `{urls["POST"]}` '
            f'без данных, не создается новый рецепт'
        )
        assert response_check_1.json() == response_check_2.json(), (
            f'Проверьте, что при PUT запросе на `{urls["PUT"]}` '
            f'без данных, рецепт не изменяется'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_create__invalid_request_data(self, user_client):
        recipes_count = Recipe.objects.count()
        code_expected = 400
        invalid_id = 404
        invalid_ingredients_data = [
            {
                'id': invalid_id,
                'amount': 0
            }
        ]
        invalid_data = {
            'ingredients': invalid_ingredients_data,
            'tags': [invalid_id, 4546],
            'image': 'invalid_image',
            'name': 'рецепт',
            'text': 'Описание',
            'cooking_time': 0
        }
        response = user_client.post(
            self.url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        response_data = response.json()
        id_expected = [f'Недопустимый первичный ключ "{invalid_id}" - объект '
                       f'не существует.']
        ingredients_expected = [
            {
                'id': id_expected,
                'amount': ['Убедитесь, что это значение больше либо '
                           'равно 0.01.']
            }
        ]
        data_expected = {
            'ingredients': ingredients_expected,
            'tags': id_expected,
            'image': ['Загрузите правильное изображение. Файл, который вы '
                      'загрузили, поврежден или не является изображением.'],
            'name': ['Название должно начинаться с заглавной буквы!'],
            'text': ['Описание должно содержать от 10 символов!'],
            'cooking_time': ['Убедитесь, что это значение больше либо '
                             'равно 1.']
        }

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` с невалидными '
            f'данными, возвращается статус {code_expected}'
        )
        assert Recipe.objects.count() == recipes_count, (
            f'Проверьте, что при POST запросе на `{self.url}` с невалидными '
            f'данными не создается новый рецепт'
        )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Убедитесь, что поле `{field[0]}` проверяется на валидность'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что поле `{field[0]}` после POST запроса '
                f'с невалидными данными выдает соответствующую ошибку'
            )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_create__valid_request_data(self, user_client, user, tag,
                                                tag_2, image, ingredient,
                                                ingredient_2):
        recipes_count = Recipe.objects.count()
        code_expected = 201
        amount_1 = 0.1
        amount_2 = 10
        valid_ingredients_data = [
            {
                'id': ingredient.id,
                'amount': amount_1
            },
            {
                'id': ingredient_2.id,
                'amount': amount_2
            }
        ]
        valid_data = {
            'ingredients': valid_ingredients_data,
            'tags': [tag.id, tag_2.id],
            'image': image,
            'name': 'Рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 30
        }

        author_expected = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': user.is_subscribed
        }
        tags_expected = [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            },
            {
                'id': tag_2.id,
                'name': tag_2.name,
                'color': tag_2.color,
                'slug': tag_2.slug
            },
        ]
        ingredients_expected = [
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': amount_1
            },
            {
                'id': ingredient_2.id,
                'name': ingredient_2.name,
                'measurement_unit': ingredient_2.measurement_unit,
                'amount': amount_2
            }
        ]
        image_expected = '/media/recipes/' + r'\w'
        data_expected = {
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'name': 'Рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 30
        }
        response = user_client.post(
            self.url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` с валидными '
            f'данными, возвращается статус {code_expected}'
        )
        assert Recipe.objects.count() == recipes_count + 1, (
            f'Проверьте, что при POST запросе на `{self.url}` с валидными '
            f'данными создается новый рецепт'
        )
        for field in self.fields_create_update:
            assert field in response_data.keys(), (
                f'Убедитесь, что поле `{field}` присутствует в выдаче '
                f'после успешного создания рецепта'
            )
        assert re.match(image_expected, response_data['image']), (
            f'Убедитесь, что поле `image` содержит корректные данные'
        )
        for field in data_expected.items():
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что поле `{field[0]}` содержит корректные данные'
            )
        for field in author_expected.items():
            assert field[0] in response_data['author'].keys(), (
                f'Убедитесь, что поле `{field[0]}` присутствует в поле '
                f'`author` после успешного создания рецепта'
            )
            assert field[1] == response_data['author'][field[0]], (
                f'Убедитесь, что поле `{field[0]}` в поле `author` '
                f'содержит корректные данные'
            )
        ingredients_tags_expected = {
            'ingredients': ingredients_expected,
            'tags': tags_expected
        }
        for checked, expected in ingredients_tags_expected.items():
            for i in range(len(expected)):
                for field in expected[i].items():
                    assert field[0] in response_data[checked][i].keys(), (
                        f'Убедитесь, что поле `{field[0]}` присутствует '
                        f'в поле `{checked}` после успешного создания '
                        f'рецепта'
                    )
                    assert field[1] == response_data[checked][i][field[0]], (
                        f'Убедитесь, что значение поля `{field[0]}` в поле '
                        f'`{checked}` содержит корректные данные'
                    )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_update_delete__not_auth(self, client, recipe_2, tag_2,
                                             ingredient_2, amount_2, image):
        url = f'{self.url}{str(recipe_2.id)}/'
        recipes_count = Recipe.objects.count()
        code_expected = 401
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}
        valid_ingredients_data = [
            {
                'id': ingredient_2.id,
                'amount': amount_2.amount
            }
        ]
        valid_data = {
            'ingredients': valid_ingredients_data,
            'tags': [tag_2.id],
            'image': image,
            'name': 'Измененное название рецепта',
            'text': 'Измененное описание рецепта',
            'cooking_time': 30
        }
        response_before = client.get(url, content_type='application/json')
        response_update = client.put(
            url,
            data=valid_data,
            content_type='application/json'
        )
        response_delete = client.delete(url, content_type='application/json')
        response_after = client.get(url, content_type='application/json')
        requests = {
            'PUT': response_update,
            'DELETE': response_delete
        }

        for request, response in requests.items():
            assert response.status_code == code_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'от неавторизованного пользователя, возвращается статус '
                f'{code_expected}'
            )
            assert response.json() == data_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'от неавторизованного пользователя, возвращается сообщение: '
                f'{data_expected["detail"]}'
            )
        assert response_before.json() == response_after.json(), (
            f'Проверьте, что при PUT запросе на `{url}` '
            f'от неавторизованного пользователя, рецепт не изменяется'
        )
        assert Recipe.objects.count() == recipes_count, (
            f'Проверьте, что при DELETE запросе на `{url}` '
            f'от неавторизованного пользователя, рецепт не удаляется'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_update_delete__not_owner(self, user_client, recipe,
                                              tag, ingredient, amount, image):
        url = f'{self.url}{str(recipe.id)}/'
        recipes_count = Recipe.objects.count()
        code_expected = 403
        data_expected = {'detail': 'У вас недостаточно прав для выполнения '
                                   'данного действия.'}
        valid_ingredients_data = [
            {
                'id': ingredient.id,
                'amount': amount.amount
            }
        ]
        valid_data = {
            'ingredients': valid_ingredients_data,
            'tags': [tag.id],
            'image': image,
            'name': 'Измененное название рецепта',
            'text': 'Измененное описание рецепта',
            'cooking_time': 30
        }
        response_check_1 = user_client.get(
            url,
            content_type='application/json'
        )
        response_update = user_client.put(
            url,
            data=valid_data,
            content_type='application/json'
        )
        response_delete = user_client.delete(
            url,
            content_type='application/json'
        )
        response_check_2 = user_client.get(
            url,
            content_type='application/json'
        )
        requests = {
            'PUT': response_update,
            'DELETE': response_delete
        }

        for request, response in requests.items():
            assert response.status_code == code_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'от пользователя, не являющегося автором рецепта, '
                f'возвращается статус {code_expected}'
            )
            assert response.json() == data_expected, (
                f'Проверьте, что при {request} запросе на `{url}` '
                f'от пользователя, не являющегося автором рецепта, '
                f'возвращается сообщение: {data_expected["detail"]}'
            )
        assert response_check_1.json() == response_check_2.json(), (
            f'Проверьте, что при PUT запросе на `{url}` '
            f'от пользователя, не являющегося автором рецепта, '
            f'рецепт не изменяется'
        )
        assert Recipe.objects.count() == recipes_count, (
            f'Проверьте, что при DELETE запросе на `{url}` '
            f'от пользователя, не являющегося автором рецепта, '
            f'рецепт не удаляется'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_update__valid_request_data(self, user_client, user, tag,
                                                tag_2, image, ingredient,
                                                ingredient_2, amount, amount_2,
                                                recipe_2):
        url = f'{self.url}{str(recipe_2.id)}/'
        code_expected = 200
        valid_ingredients_data = [
            {
                'id': ingredient.id,
                'amount': amount.amount
            },
            {
                'id': ingredient_2.id,
                'amount': amount_2.amount
            }
        ]
        valid_data = {
            'ingredients': valid_ingredients_data,
            'tags': [tag.id, tag_2.id],
            'image': image,
            'name': 'Измененное название рецепта',
            'text': 'Измененное описание рецепта',
            'cooking_time': 30
        }

        tags_expected = [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            },
            {
                'id': tag_2.id,
                'name': tag_2.name,
                'color': tag_2.color,
                'slug': tag_2.slug
            },
        ]
        ingredients_expected = [
            {
                'id': ingredient.id,
                'name': ingredient.name,
                'measurement_unit': ingredient.measurement_unit,
                'amount': amount.amount
            },
            {
                'id': ingredient_2.id,
                'name': ingredient_2.name,
                'measurement_unit': ingredient_2.measurement_unit,
                'amount': amount_2.amount
            }
        ]
        image_expected = '/media/' + r'\w'
        data_expected = {
            'is_favorited': False,
            'is_in_shopping_cart': False,
            'name': 'Измененное название рецепта',
            'text': 'Измененное описание рецепта',
            'cooking_time': 30
        }
        response = user_client.patch(
            url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        response_data = response.json()
        response_changed = user_client.get(
            url,
            content_type='application/json'
        )
        response_data_changed = response_changed.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при PUT запросе на `{url}` с валидными '
            f'данными, возвращается статус {code_expected}'
        )
        for field in self.fields_create_update:
            assert field in response_data.keys(), (
                f'Убедитесь, что поле `{field}` присутствует в выдаче '
                f'после успешного изменения рецепта'
            )
        assert re.match(image_expected, response_data['image']), (
            f'Убедитесь, что поле `image` содержит корректные данные'
        )
        assert response_data['image'] == response_data_changed['image'], (
            f'Проверьте, что поле `image` успешно изменилось'
        )
        for field in data_expected.items():
            assert (field[1]
                    == response_data[field[0]]
                    == response_data_changed[field[0]]), (
                f'Убедитесь, что поле `{field[0]}` содержит корректные данные '
                f' и изменилось в базе данных'
            )
        assert response_data['author'] == response_data_changed['author'], (
            f'Убедитесь, что поле `author` не изменилось, после изменения '
            f'рецепта'
        )
        ingredients_tags_expected = {
            'ingredients': ingredients_expected,
            'tags': tags_expected
        }
        for checked, expected in ingredients_tags_expected.items():
            for i in range(len(expected)):
                for field in expected[i].items():
                    assert field[0] in response_data[checked][i].keys(), (
                        f'Убедитесь, что поле `{field[0]}` присутствует '
                        f'в поле `{checked}` после успешного изменения '
                        f'рецепта'
                    )
                    assert field[1] == response_data[checked][i][field[0]], (
                        f'Убедитесь, что значение поля `{field[0]}` в поле '
                        f'`{checked}` содержит корректные данные'
                    )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_update_delete__owner(self, user_client, recipe_2):
        url = f'{self.url}{str(recipe_2.id)}/'
        recipes_count = Recipe.objects.count()
        code_expected = 204
        response = user_client.delete(
            url,
            content_type='application/json'
        )

        assert response.status_code == code_expected, (
            f'Проверьте, что при DELETE запросе на `{url}` '
            f'на свой существующий рецепт, возвращается код '
            f'{code_expected}'
        )
        assert Recipe.objects.count() == recipes_count - 1, (
            f'Проверьте, что при DELETE запросе на `{url}` '
            f'на свой существующий рецепт, он удаляется'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_tag_filter(self, user_client, recipe, recipe_2, tag_2):
        code_expected = 200
        response = user_client.get(
            f'{self.url}?tags=test_tag_2',
            content_type='application/json'
        )
        response_data = response.json()
        tag_expected = {
            'id': tag_2.id,
            'name': tag_2.name,
            'color': tag_2.color,
            'slug': tag_2.slug
        }

        assert response.status_code == code_expected, (
            f'Убедитесь, что при GET запросе на `{self.url}?tags=test_tag_2` '
            f'с фильтром тегов, возвращается код {code_expected}'
        )
        assert len(response_data['results']) == Recipe.objects.filter(tags=tag_2).count(), (
            f'Проверьте, что при GET запросе на `{self.url}?tags=test_tag_2` '
            f'с фильтром тегов, возвращается количество рецептов, подходящее '
            f'под заданный фильтр'
        )
        assert tag_expected in response_data['results'][0]['tags'], (
            f'Убедитесь, что при GET запросе на `{self.url}?tags=test_tag_2`, '
            f'в рецептах в результатах запроса присутствует тег, указанный '
            f'в фильтре'
        )


class TestFavoritesAndShoppingCart:

    @pytest.mark.django_db(transaction=True)
    def test_favorites_shop_cart_create__not_auth(self, client, recipe):
        urls = {
            f'/api/recipes/{str(recipe.id)}/favorite/': Favorite.objects,
            f'/api/recipes/{str(recipe.id)}/shopping_cart/':
                ShoppingCart.objects
        }
        code_expected = 401
        for url, obj in urls.items():
            count = obj.count()
            response = client.post(
                url,
                content_type='application/json'
            )
            response_data = response.json()
            data_expected = {'detail': 'Учетные данные не были предоставлены.'}

            assert response.status_code == code_expected, (
                f'Проверьте, что при POST запросе на `{url}` от анонимного '
                f'пользователя, возвращается статус {code_expected}'
            )
            assert obj.count() == count, (
                f'Проверьте, что при POST запросе на `{url}` от анонимного '
                f'пользователя, не создается объект модели в базе данных'
            )
            assert response_data == data_expected, (
                f'Убедитесь, что при POST запросе на `{url}` от анонимного '
                f'пользователя, возвращается сообщение: '
                f'{data_expected["detail"]}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_favorites_shop_cart_create__auth_user(self, user_client, user,
                                                   recipe, recipe_2):
        urls = {
            f'/api/recipes/{str(recipe.id)}/favorite/':
                (Favorite.objects, 'favorite', 'is_favorited',
                 Recipe.objects.filter(favorites__user=user),
                 Recipe.objects.exclude(favorites__user=user)),
            f'/api/recipes/{str(recipe.id)}/shopping_cart/':
                (ShoppingCart.objects, 'shopping_cart', 'is_in_shopping_cart',
                 Recipe.objects.filter(shopping_cart__user=user),
                 Recipe.objects.exclude(shopping_cart__user=user))
        }
        code_expected = 201
        for url, obj in urls.items():
            count = obj[0].count()
            response = user_client.post(
                url,
                content_type='application/json'
            )
            response_check = user_client.get(
                f'/api/recipes/{str(recipe.id)}/',
                content_type='application/json'
            )
            response_filter = user_client.get(
                f'/api/recipes/?{obj[2]}=1',
                content_type='application/json'
            )
            response_double = user_client.post(
                url,
                content_type='application/json'
            )
            response_data = response.json()
            response_data_check = response_check.json()
            response_data_filter = response_filter.json()
            response_data_double = response_double.json()
            image_expected = '/media/' + r'\w'
            data_expected = {
                'id': recipe.id,
                'name': recipe.name,
                'cooking_time': recipe.cooking_time
            }
            double_expected = {'errors': 'Рецепт уже добавлен'}

            assert response.status_code == code_expected, (
                f'Проверьте, что при POST запросе на `{url}` от '
                f'авторизованного пользователя, возвращается статус '
                f'{code_expected}'
            )
            assert obj[0].count() == count + 1, (
                f'Проверьте, что при POST запросе на `{url}` от '
                f'авторизованного пользователя, создается объект модели '
                f'`{obj[1]}` в базе данных'
            )
            assert response_data_double == double_expected, (
                f'Убедитесь, что нельзя добавить рецепт в список дважды'
            )
            assert response_data_check[obj[2]] is True, (
                f'Убедитесь, что после добавления рецепта в список, поле '
                f'рецепта `{obj[2]}` имеет значение `True`'
            )
            assert len(response_data_filter['results']) == obj[3].count(), (
                f'Проверьте, что при GET запросе с фильтрацией на '
                f'`/api/recipes/?{obj[2]}=1`, возвращаются все рецепты '
                f'со значением поля `{obj[2]}` - True'
            )
            assert len(response_data_filter['results']) == obj[4].count(), (
                f'Проверьте, что при GET запросе с фильтрацией на '
                f'`/api/recipes/?{obj[2]}=0`, возвращаются все рецепты '
                f'со значением поля `{obj[2]}` - False'
            )
            assert response_data_filter['results'][0][obj[2]] is True, (
                f'Убедитесь, что при GET запросе с фильтрацией на '
                f'`/api/recipes/?{obj[2]}=1`, значение поля `{obj[2]}` - True'
            )
            assert 'image' in response_data.keys(), (
                f'Убедитесь, что поле `image` присутствует в выдаче'
            )
            assert re.match(image_expected, response_data['image']), (
                f'Убедитесь, что поле `image` содержит корректные данные'
            )
            for field in data_expected.items():
                assert field[0] in response_data.keys(), (
                    f'Убедитесь, что поле `{field[0]}` присутствует '
                    f'в выдаче после успешного добавления рецепта в список'
                )
                assert field[1] == response_data[field[0]], (
                    f'Убедитесь, что значение поля `{field[0]}` после '
                    f'успешного добавления рецепта в список, содержит '
                    f'корректные данные'
                )

    @pytest.mark.django_db(transaction=True)
    def test_favorites_shop_cart_delete__not_auth(self, client, user_client,
                                                  recipe_2):
        urls = {
            f'/api/recipes/{str(recipe_2.id)}/favorite/': Favorite.objects,
            f'/api/recipes/{str(recipe_2.id)}/shopping_cart/':
                ShoppingCart.objects
        }
        code_expected = 401
        for url, obj in urls.items():
            user_client.post(
                url,
                content_type='application/json'
            )
            count = obj.count()
            response = client.delete(
                url,
                content_type='application/json'
            )
            response_data = response.json()
            data_expected = {'detail': 'Учетные данные не были предоставлены.'}

            assert response.status_code == code_expected, (
                f'Проверьте, что при DELETE запросе на `{url}` от анонимного '
                f'пользователя, возвращается статус {code_expected}'
            )
            assert obj.count() == count, (
                f'Проверьте, что при DELETE запросе на `{url}` от анонимного '
                f'пользователя, не создается объект модели в базе данных'
            )
            assert response_data == data_expected, (
                f'Убедитесь, что при DELETE запросе на `{url}` от анонимного '
                f'пользователя, возвращается сообщение: '
                f'{data_expected["detail"]}'
            )

    @pytest.mark.django_db(transaction=True)
    def test_favorites_shop_cart_delete__auth_user(self, user_client,
                                                   recipe_2):
        urls = {
            f'/api/recipes/{str(recipe_2.id)}/favorite/':
                (Favorite.objects, 'favorite', 'is_favorited'),
            f'/api/recipes/{str(recipe_2.id)}/shopping_cart/':
                (ShoppingCart.objects, 'shopping_cart', 'is_in_shopping_cart')
        }
        code_expected = 204
        for url, obj in urls.items():
            user_client.post(
                url,
                content_type='application/json'
            )
            count = obj[0].count()
            response_before = user_client.get(
                f'/api/recipes/{str(recipe_2.id)}/',
                content_type='application/json'
            )
            response = user_client.delete(
                url,
                content_type='application/json'
            )
            response_after = user_client.get(
                f'/api/recipes/{str(recipe_2.id)}/',
                content_type='application/json'
            )
            response_double = user_client.delete(
                url,
                content_type='application/json'
            )
            response_data_before = response_before.json()
            response_data_after = response_after.json()
            response_data_double = response_double.json()
            double_expected = {'errors': 'Рецепт не найден в списке'}

            assert (response_data_before[obj[2]]
                    != response_data_after[obj[2]]), (
                f'Убедитесь, что значение поля `{obj[2]}` до DELETE запроса '
                f'отличается от значения этого поля после удаления из списка'
            )
            assert response.status_code == code_expected, (
                f'Проверьте, что при DELETE запросе на `{url}` от '
                f'авторизованного пользователя, возвращается статус '
                f'{code_expected}'
            )
            assert response_double.status_code == 400, (
                f'Проверьте, что при попытке удалить из избранного рецепт, '
                f'который не был туда добавлен, возвращается статус 400'
            )
            assert obj[0].count() == count - 1, (
                f'Проверьте, что при DELETE запросе на `{url}` от '
                f'авторизованного пользователя, удаляется объект модели '
                f'`{obj[1]}` в базе данных'
            )
            assert response_data_double == double_expected, (
                f'Проверьте, что нельзя удалить рецепт из списка, '
                f'если он не был в него добавлен'
            )

    @pytest.mark.django_db(transaction=True)
    def test_download_shop_cart__not_auth(self, client):
        url = '/api/recipes/download_shopping_cart/'
        code_expected = 401
        response = client.get(
            url,
            content_type='application/json'
        )
        response_data = response.json()
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}

        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе на `{url}` от анонимного '
            f'пользователя, возвращается статус {code_expected}'
        )
        assert response_data == data_expected, (
            f'Убедитесь, что при GET запросе на `{url}` от анонимного '
            f'пользователя, возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_recipes_favorite_shop_cart_filters(self, user_client, user,
                                                recipe, recipe_2):
        urls = {
            '/api/recipes/?is_favorited=1': [
                f'/api/recipes/{str(recipe_2.id)}/favorite/',
                'is_favorited'
            ],
            '/api/recipes/?is_in_shopping_cart=1': [
                f'/api/recipes/{str(recipe_2.id)}/shopping_cart/',
                'is_in_shopping_cart'
            ]
        }
        code_expected = 200
        for url, obj in urls.items():
            user_client.post(
                obj[0],
                content_type='application/json'
            )
            response = user_client.get(url, content_type='application/json')
            response_data = response.json()

            assert response.status_code == code_expected, (
                f'Убедитесь, что при GET запросе на `{url}` с фильтром, '
                f'возвращается код {code_expected}'
            )
            assert response_data['results'][0][obj[1]] is True, (
                f'Убедитесь, что при GET запросе на `{url}` с фильтром, '
                f'в рецептах в результатах запроса значение поля '
                f'`{obj[1]}` - True'
            )
            if obj[1] == 'is_favorited':
                assert len(response_data['results']) == Recipe.objects.filter(
                    favorites__user=user
                ).count(), (
                    f'Проверьте, что при GET запросе на '
                    f'`/api/recipes/?is_favorited=1` с фильтром, возвращается '
                    f'количество рецептов, подходящее под заданный фильтр'
                )
            else:
                assert len(response_data['results']) == Recipe.objects.filter(
                    shopping_cart__user=user
                ).count(), (
                    f'Проверьте, что при GET запросе на '
                    f'`/api/recipes/?is_in_shopping_cart=1` с фильтром, '
                    f'возвращается количество рецептов, подходящее под '
                    f'заданный фильтр'
                )
