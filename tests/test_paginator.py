import pytest

from recipes.models import Recipe
from users.models import User


class TestPaginator:
    urls = {
        'Recipe': '/api/recipes/',
        'User': '/api/users/'
    }

    @pytest.mark.django_db(transaction=True)
    def test_paginator(self, client, many_recipes, many_users):
        for model, url in self.urls.items():
            second_page = f'{url}?page=2'
            code_expected = 200
            response = client.get(url, content_type='application/json')
            response_second_page = client.get(
                second_page,
                content_type='application/json'
            )
            response_data = response.json()
            response_data_second_page = response_second_page.json()
            fields_expected = ['count', 'next', 'previous', 'results']
            next_expected = f'http://testserver{second_page}'
            previous_expected = f'http://testserver{url}'
            if model == 'Recipe':
                objects_count = Recipe.objects.count()
            else:
                objects_count = User.objects.count()

            assert response.status_code == code_expected, (
                f'Убедитесь, что при GET запросе на `{url}` с пагинацией '
                f'возвращается код {code_expected}'
            )
            assert len(response_data['results']) == 6, (
                f'Убедитесь, что при GET запросе на `{url}` с пагинацией, '
                f'на первой странице отображается 6 объектов класса `{model}`'
            )
            assert len(response_data_second_page['results']) == 4, (
                f'Убедитесь, что при GET запросе на `{second_page}` '
                f'с пагинацией, на второй странице отображаются оставшиеся '
                f'объекты класса `{model}`'
            )
            assert objects_count == response_data['count'], (
                f'Убедитесь, что при GET запросе на `{url}` с пагинацией, '
                f'в поле `count` отображается количество всех объектов '
                f'класса `{model}`'
            )
            assert next_expected == response_data['next'], (
                f'Убедитесь, что при GET запросе на `{url}` с пагинацией, '
                f'в поле `next` отображается ссылка на следующую страницу'
            )
            assert previous_expected == response_data_second_page['previous'], (
                f'Убедитесь, что при GET запросе на `{second_page}` '
                f'с пагинацией, в поле `previous` отображается ссылка '
                f'на предыдущую страницу'
            )
            for field in fields_expected:
                assert field in response_data, (
                    f'Убедитесь, что поле `{field}` присутствует в выдаче '
                    f'после успешного GET запроса списка объектов `{model}`'
                )
