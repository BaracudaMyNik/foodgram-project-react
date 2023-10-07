import pytest
import re

from recipes.models import Recipe
from users.models import Subscription, User


class TestUsers:
    url = '/api/users/'

    @pytest.mark.django_db(transaction=True)
    def test_users_list(self, client, user_client, user, user_2):
        code_expected = 200
        response = client.get(self.url)
        response_auth = user_client.get(self.url)
        data = response.json()
        data_auth = response_auth.json()
        response_data = data['results']
        response_data_auth = data_auth['results']
        test_user = response_data[0]
        data_expected = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': user.is_subscribed
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
        assert type(data) == dict, (
            f'Проверьте, что при GET запросе на `{self.url}` '
            f'возвращается словарь'
        )
        assert len(response_data) == data['count'] == User.objects.count(), (
            f'Проверьте, что при GET запросе на `{self.url}` '
            f'возвращается весь список пользователей'
        )
        for field in data_expected.items():
            assert field[0] in test_user.keys(), (
                f'Проверьте, что добавили поле `{field[0]}` в список полей '
                f'`fields` сериализатора модели User'
            )
            assert field[1] == test_user[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` содержит '
                f'корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_users_create__empty_request_data(self, client, user):
        users_count = User.objects.count()
        code_expected = 400
        empty_data = {}
        response = client.post(self.url, data=empty_data)
        response_data = response.json()
        required_field = ['Обязательное поле.']
        data_expected = {
            'email': required_field,
            'username': required_field,
            'first_name': required_field,
            'last_name': required_field,
            'password': required_field
        }

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` без данных '
            f'возвращается статус {code_expected}'
        )
        assert User.objects.count() == users_count, (
            f'Проверьте, что при POST запросе на `{self.url}` без данных '
            f'не создается новый пользователь'
        )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Проверьте, что поле `{field[0]}` является обязательным'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` после POST '
                f'запроса без данных: `{field[1]}`'
            )

    @pytest.mark.django_db(transaction=True)
    def test_users_create__invalid_request_data(self, client, user):
        users_count = User.objects.count()
        code_expected = 400
        invalid_data = {
            'email': 'InvalidEmail',
            'username': 'Invalid/Username',
            'first_name': 'invalidName',
            'last_name': 'invalidLastName',
            'password': '12345678'
        }
        response = client.post(self.url, data=invalid_data)
        response_data = response.json()
        data_expected = {
            'email': ['Введите правильный адрес электронной почты.'],
            'username': ['Имя пользователя может содержать латиницу, цифры '
                         'и знаки @ / . / + / - / _'],
            'first_name': ['Имя должно начинаться с заглавной буквы!'],
            'last_name': ['Фамилия должна начинаться с заглавной буквы!'],
            'password': ['Введённый пароль слишком широко распространён.']
        }

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` с невалидными '
            f'данными, возвращается статус {code_expected}'
        )
        assert User.objects.count() == users_count, (
            f'Проверьте, что при POST запросе на `{self.url}` с невалидными '
            f'данными не создается новый пользователь'
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
    def test_users_create__existing_username_email(self, client, user):
        users_count = User.objects.count()
        code_expected = 400
        existing_data = {
            'email': user.email,
            'username': user.username,
            'first_name': 'Name',
            'last_name': 'Lastname',
            'password': 'Password654321'
        }
        response = client.post(self.url, data=existing_data)
        response_data = response.json()
        data_expected = {
            'email': ['Пользователь с таким Email уже существует.'],
            'username': ['Пользователь с таким Логин уже существует.']
        }

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` с существующими '
            f'данными, возвращается статус {code_expected}'
        )
        assert User.objects.count() == users_count, (
            f'Проверьте, что при POST запросе на `{self.url}` с существующими '
            f'данными не создается новый пользователь'
        )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Убедитесь, что поле `{field[0]}` проверяется на уникальность'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` после POST '
                f'запроса с существующими данными: `{field[1]}`'
            )

    @pytest.mark.django_db(transaction=True)
    def test_users_create__valid_request_data(self, client):
        users_count = User.objects.count()
        code_expected = 201
        valid_data = {
            'email': 'Valid@email.ru',
            'username': 'ValidUsername',
            'first_name': 'Validname',
            'last_name': 'Validlastname',
            'password': 'Password654321'
        }
        response = client.post(self.url, data=valid_data)
        response_data = response.json()
        data_expected = {
            'email': 'Valid@email.ru',
            'id': response_data['id'],
            'username': 'ValidUsername',
            'first_name': 'Validname',
            'last_name': 'Validlastname'
        }
        valid_data = {
            'email': 'Valid@email.ru',
            'password': 'Password654321'
        }
        response_auth = client.post('/api/auth/token/login/', data=valid_data)

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{self.url}` с валидными '
            f'данными, возвращается статус {code_expected}'
        )
        assert response_auth.status_code == 200, (
            f'Убедитесь, что после создания пользователя можно '
            f'авторизоваться, и возвращается статус 200'
        )
        assert User.objects.count() == users_count + 1, (
            f'Проверьте, что при POST запросе на `{self.url}` с валидными '
            f'данными создается новый пользователь'
        )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Убедитесь, что поле `{field[0]}` присутствует в выдаче '
                f'после успешного создания пользователя'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` содержит '
                f'корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_users_detail__not_auth(self, client, user):
        url = f'{self.url}{str(user.id)}/'
        code_expected = 401
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}
        response = client.get(url)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'от неавторизованного пользователя, возвращается статус '
            f'{code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'от неавторизованного пользователя, возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_users_detail__not_found(self, user_client, user):
        code_expected = 404
        url = f'{self.url}{code_expected}/'
        data_expected = {'detail': 'Страница не найдена.'}
        response = user_client.get(url)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'на несуществующего пользователя, возвращается статус '
            f'{code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'на несуществующего пользователя, возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_users_detail_me__auth_user(self, user_client, user):
        urls = [
            f'{self.url}{str(user.id)}/',
            f'{self.url}me/'
        ]
        code_expected = 200
        data_expected = {
            'email': user.email,
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_subscribed': user.is_subscribed
        }
        for url in urls:
            response = user_client.get(url)
            response_data = response.json()

            assert response.status_code == code_expected, (
                f'Проверьте, что при GET запросе на `{url}` '
                f'от авторизованного пользователя, возвращается статус '
                f'{code_expected}'
            )
            for field in data_expected.items():
                assert field[0] in response_data.keys(), (
                    f'Убедитесь, что добавили поле `{field[0]}` в список '
                    f'полей `fields` сериализатора модели User'
                )
                assert field[1] == response_data[field[0]], (
                    f'Убедитесь, что значение поля `{field[0]}` содержит '
                    f'корректные данные'
                )

    @pytest.mark.django_db(transaction=True)
    def test_users_me__not_auth(self, client, user):
        url = f'{self.url}me/'
        code_expected = 401
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}
        response = client.get(url)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'от неавторизованного пользователя, возвращается статус '
            f'{code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'от неавторизованного пользователя возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_users_set_password__not_auth(self, client):
        url = f'{self.url}set_password/'
        code_expected = 401
        data_expected = {'detail': 'Учетные данные не были предоставлены.'}
        response = client.get(url)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'от неавторизованного пользователя, возвращается статус '
            f'{code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'от неавторизованного пользователя возвращается сообщение: '
            f'{data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_users_set_password__invalid_data(self, user_client):
        url = f'{self.url}set_password/'
        code_expected = 400
        invalid_data = {
            'new_password': 'password',
            'current_password': 'InvalidPassword'
        }
        data_expected = {'current_password': ['Неправильный пароль.']}
        response = user_client.post(url, data=invalid_data)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'с невалидными паролями, возвращается статус '
            f'{code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'с невалидными паролями возвращается сообщение: '
            f'{data_expected["current_password"]}'
        )

        invalid_data = {
            'new_password': 'password',
            'current_password': 'Password654321'
        }
        data_expected = {
            'new_password': ['Введённый пароль слишком широко распространён.']
        }
        response = user_client.post(url, data=invalid_data)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'с невалидным новым и верным старым паролем, '
            f'возвращается статус {code_expected}'
        )
        assert response_data == data_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'с невалидным новым и верным старым паролем, '
            f'возвращается сообщение: {data_expected["new_password"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_users_set_password__valid_data(self, client, user_client, user):
        url = f'{self.url}set_password/'
        code_expected = 204
        valid_data = {
            'new_password': 'NewPassword654321',
            'current_password': 'Password654321'
        }
        response = user_client.post(url, data=valid_data)

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` '
            f'с валидными данными, возвращается статус '
            f'{code_expected}'
        )

        url_login = '/api/auth/token/login/'
        code_expected = 200
        data = {
            'email': user.email,
            'password': valid_data['new_password']
        }
        field_expected = 'auth_token'
        response = client.post(url_login, data=data)
        response_data = response.json()

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url_login}` с новым паролем, '
            f'возвращается код {code_expected}'
        )
        assert field_expected in response_data.keys(), (
            f'Убедитесь, что при запросе `{url_login}` с новым паролем, '
            f' в ответе возвращается ключ {field_expected}, '
            f'где содержится токен'
        )


class TestSubscriptions:

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_users_list__not_auth(self, client):
        url = f'/api/users/subscriptions/'
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
            f'пользователя, возвращается сообщение: {data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_users_list__auth_user(self, user_client, user, user_2,
                                             another_user, recipe):
        url = f'/api/users/subscriptions/'
        code_expected = 200
        user_client.post(
            f'/api/users/{str(user_2.id)}/subscribe/',
            content_type='application/json'
        )
        user_client.post(
            f'/api/users/{str(another_user.id)}/subscribe/',
            content_type='application/json'
        )
        response = user_client.get(
            url,
            content_type='application/json'
        )
        data = response.json()
        response_data = data['results']
        test_user = response_data[0]
        subscribe_users_count = User.objects.filter(
            subscribing__user=user
        ).count()
        recipes_count = another_user.recipes.count()
        image_expected = '/media/' + r'\w'
        data_expected = {
            'email': another_user.email,
            'id': another_user.id,
            'username': another_user.username,
            'first_name': another_user.first_name,
            'last_name': another_user.last_name,
            'is_subscribed': True,
            'recipes_count': recipes_count
        }
        recipes_expected = {
            'id': recipe.id,
            'name': recipe.name,
            'cooking_time': recipe.cooking_time
        }

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе на `{url}` возвращается код '
            f'{code_expected}'
        )
        assert len(response_data) == data['count'] == subscribe_users_count, (
            f'Проверьте, что при GET запросе на `{url}` '
            f'возвращается весь список пользователей'
        )
        assert 'image' in test_user['recipes'][0], (
            f'Убедитесь, что поле `image` в поле `recipes` присутствует '
            f'в выдаче'
        )
        assert re.match(image_expected, test_user['recipes'][0]['image']), (
            f'Убедитесь, что поле `image` в поле `recipes` содержит '
            f'корректные данные'
        )
        for field in recipes_expected.items():
            assert field[0] in test_user['recipes'][0], (
                f'Убедитесь, что при GET запросе на `{url}`, поле '
                f'`{field[0]}` присутствует в поле `recipes`'
            )
            assert field[1] == test_user['recipes'][0][field[0]], (
                f'Убедитесь, что при GET запросе на `{url}`, значение поля '
                f'`{field[0]}` в поле `recipes` содержит корректные данные'
            )
        for field in data_expected.items():
            assert field[0] in test_user.keys(), (
                f'Убедитесь, что при GET запросе на `{url}`, поле '
                f'`{field[0]}` присутствует в выдаче'
            )
            assert field[1] == test_user[field[0]], (
                f'Убедитесь, что при GET запросе на `{url}`, значение поля '
                f'`{field[0]}` содержит корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_create__not_auth(self, client, another_user):
        url = f'/api/users/{str(another_user.id)}/subscribe/'
        code_expected = 401
        subscriptions_count = Subscription.objects.count()
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
        assert Subscription.objects.count() == subscriptions_count, (
            f'Проверьте, что при POST запросе на `{url}` от анонимного '
            f'пользователя, не создается объект модели `Subscription` '
            f'в базе данных'
        )
        assert response_data == data_expected, (
            f'Убедитесь, что при POST запросе на `{url}` от анонимного '
            f'пользователя, возвращается сообщение: {data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_create_delete__not_found(self, user_client):
        code_expected = 404
        url = f'/api/users/{code_expected}/subscribe/'
        subscriptions_count = Subscription.objects.count()
        response_create = user_client.post(
            url,
            content_type='application/json'
        )
        response_delete = user_client.delete(
            url,
            content_type='application/json'
        )
        response_data_create = response_create.json()
        response_data_delete = response_delete.json()
        data_expected = {'detail': 'Страница не найдена.'}

        assert response_create.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` на несуществующего '
            f'пользователя, возвращается статус {code_expected}'
        )
        assert response_delete.status_code == code_expected, (
            f'Проверьте, что при DELETE запросе на `{url}` на несуществующего '
            f'пользователя, возвращается статус {code_expected}'
        )
        assert Subscription.objects.count() == subscriptions_count, (
            f'Проверьте, что при POST запросе на `{url}` на несуществующего '
            f'пользователя, не создается объект модели `Subscription` '
            f'в базе данных'
        )
        assert response_data_create == data_expected, (
            f'Убедитесь, что при POST запросе на `{url}` на несуществующего '
            f'пользователя, возвращается сообщение: {data_expected["detail"]}'
        )
        assert response_data_delete == data_expected, (
            f'Убедитесь, что при DELETE запросе на `{url}` на несуществующего '
            f'пользователя, возвращается сообщение: {data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_create__auth_user(self, user_client, user, another_user,
                                         recipe, image):
        url = f'/api/users/{str(another_user.id)}/subscribe/'
        subscriptions_count = Subscription.objects.count()
        code_expected = 201
        response = user_client.post(
            url,
            content_type='application/json'
        )
        response_check = user_client.get(
            f'/api/users/{str(another_user.id)}/',
            content_type='application/json'
        )
        response_double = user_client.post(
            url,
            content_type='application/json'
        )
        response_subscribe_yourself = user_client.post(
            f'/api/users/{str(user.id)}/subscribe/',
            content_type='application/json'
        )
        response_data = response.json()
        response_data_check = response_check.json()
        response_data_double = response_double.json()
        response_data_subscribe_yourself = response_subscribe_yourself.json()
        recipes_count_expected = Recipe.objects.filter(
            author=another_user
        ).count()
        image_expected = '/media/' + r'\w'
        data_expected = {
            'email': another_user.email,
            'id': another_user.id,
            'username': another_user.username,
            'first_name': another_user.first_name,
            'last_name': another_user.last_name,
            'is_subscribed': True,
            'recipes_count': recipes_count_expected
        }
        recipes_expected = {
            'id': recipe.id,
            'name': recipe.name,
            'cooking_time': recipe.cooking_time
        }
        double_expected = {'errors': 'Вы уже подписаны на этого пользователя'}
        subscribe_yourself_expected = {
            'errors': 'Невозможно подписаться на самого себя'
        }

        assert response.status_code == code_expected, (
            f'Проверьте, что при POST запросе на `{url}` от авторизованного '
            f'пользователя, возвращается статус {code_expected}'
        )
        assert Subscription.objects.count() == subscriptions_count + 1, (
            f'Проверьте, что при POST запросе на `{url}` от авторизованного '
            f'пользователя, создается объект модели `Subscription` в базе '
            f'данных'
        )
        assert response_data_double == double_expected, (
            f'Убедитесь, что нельзя подписаться на одного пользователя дважды'
        )
        assert (subscribe_yourself_expected
                == response_data_subscribe_yourself), (
            f'Убедитесь, что нельзя подписаться на самого себя'
        )
        assert response_data_check['is_subscribed'] is True, (
            f'Убедитесь, что после подписки на пользователя, поле '
            f'`is_subscribed` этого пользователя имеет значение `True`'
        )
        assert 'image' in response_data['recipes'][0], (
            f'Убедитесь, что поле `image` в поле `recipes` присутствует '
            f'в выдаче'
        )
        assert re.match(image_expected,
                        response_data['recipes'][0]['image']), (
            f'Убедитесь, что поле `image` в поле `recipes` содержит '
            f'корректные данные'
        )
        for field in recipes_expected.items():
            assert field[0] in response_data['recipes'][0], (
                f'Убедитесь, что поле `{field[0]}` присутствует в поле '
                f'`recipes`, после успешной подписки на пользователя'
            )
            assert field[1] == response_data['recipes'][0][field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` в поле `recipes` '
                f'после успешной подписки на пользователя, содержит '
                f'корректные данные'
            )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Убедитесь, что поле `{field[0]}` присутствует в выдаче '
                f'после успешной подписки на пользователя'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` после успешной '
                f'подписки на пользователя, содержит корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_delete__not_auth(self, client, user_client, user_2):
        url = f'/api/users/{str(user_2.id)}/subscribe/'
        code_expected = 401
        user_client.post(
            url,
            content_type='application/json'
        )
        subscriptions_count = Subscription.objects.count()
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
        assert Subscription.objects.count() == subscriptions_count, (
            f'Проверьте, что при DELETE запросе на `{url}` от анонимного '
            f'пользователя, не создается объект модели `Favorite` в базе '
            f'данных'
        )
        assert response_data == data_expected, (
            f'Убедитесь, что при DELETE запросе на `{url}` от анонимного '
            f'пользователя, возвращается сообщение: {data_expected["detail"]}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_subscribe_delete__auth_user(self, user_client, user_2):
        url = f'/api/users/{str(user_2.id)}/subscribe/'
        code_expected = 204
        user_client.post(
            url,
            content_type='application/json'
        )
        favorites_count = Subscription.objects.count()
        response_before = user_client.get(
            f'/api/users/{str(user_2.id)}/',
            content_type='application/json'
        )
        response = user_client.delete(
            url,
            content_type='application/json'
        )
        response_after = user_client.get(
            f'/api/users/{str(user_2.id)}/',
            content_type='application/json'
        )
        response_double = user_client.delete(
            url,
            content_type='application/json'
        )
        response_data_before = response_before.json()
        response_data_after = response_after.json()
        response_data_double = response_double.json()
        double_expected = {'errors': 'Вы не подписаны на этого пользователя'}

        assert (response_data_before['is_subscribed']
                != response_data_after['is_subscribed']), (
            f'Убедитесь, что значение поля `is_subscribed` до DELETE запроса '
            f'отличается от значения этого поля после отписки'
        )
        assert response.status_code == code_expected, (
            f'Проверьте, что при DELETE запросе на `{url}` от авторизованного '
            f'пользователя, возвращается статус {code_expected}'
        )
        assert response_double.status_code == 400, (
            f'Проверьте, что при попытке отписаться от пользователя, '
            f'на которого нет подписки, возвращается статус 400'
        )
        assert Subscription.objects.count() == favorites_count - 1, (
            f'Проверьте, что при DELETE запросе на `{url}` от авторизованного '
            f'пользователя, удаляется объект модели `Subscription` в базе '
            f'данных'
        )
        assert response_data_double == double_expected, (
            f'Проверьте, что нельзя отписаться от пользователя, на которого '
            f'нет подписки'
        )
