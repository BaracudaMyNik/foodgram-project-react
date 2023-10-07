import pytest

from recipes.models import Tag


class TestTags:
    url = '/api/tags/'

    @pytest.mark.django_db(transaction=True)
    def test_tags_list(self, client, user_client, tag, tag_2):
        code_expected = 200
        response = client.get(self.url)
        response_auth = user_client.get(self.url)
        response_data = response.json()
        response_data_auth = response_auth.json()
        test_tag = response_data[0]
        data_expected = {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color,
            'slug': tag.slug
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
        assert len(response_data) == Tag.objects.count(), (
            f'Проверьте, что при GET запросе на `{self.url}` '
            f'возвращается весь список тегов'
        )
        for field in data_expected.items():
            assert field[0] in test_tag.keys(), (
                f'Проверьте, что добавили поле `{field[0]}` в список полей '
                f'`fields` сериализатора модели Tag'
            )
            assert field[1] == test_tag[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` содержит '
                f'корректные данные'
            )

    @pytest.mark.django_db(transaction=True)
    def test_tags_detail(self, client, user_client, tag):
        url = self.url + str(tag.id) + '/'
        code_expected = 200
        response = client.get(url)
        response_auth = user_client.get(url)
        response_data = response.json()
        response_data_auth = response_auth.json()
        data_expected = {
            'id': tag.id,
            'name': tag.name,
            'color': tag.color,
            'slug': tag.slug
        }

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` '
            f'возвращается код {code_expected}'
        )
        assert response_data == response_data_auth, (
            f'Проверьте, что результат GET запроса на `{url}` '
            f'от анонима не отличается от результата запроса от '
            f'авторизованного пользователя'
        )
        for field in data_expected.items():
            assert field[0] in response_data.keys(), (
                f'Проверьте, что добавили поле `{field[0]}` в список полей '
                f'`fields` сериализатора модели Tag'
            )
            assert field[1] == response_data[field[0]], (
                f'Убедитесь, что значение поля `{field[0]}` содержит '
                f'корректные данные'
            )
