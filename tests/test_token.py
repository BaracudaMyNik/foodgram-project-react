import pytest


class TestToken:
    url_login = '/api/auth/token/login/'
    url_logout = '/api/auth/token/logout/'

    @pytest.mark.django_db(transaction=True)
    def test_login__invalid_request_data(self, client, user):
        code_expected = 400
        field = 'non_field_errors'
        value = 'Невозможно войти с предоставленными учетными данными.'

        url = self.url_login
        response = client.post(url)

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        assert {field: [value]} == response.json(), (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected} с сообщением {value}'
        )

        email_invalid = 'invalid_email_not_exists'
        password_invalid = 'invalid pwd'
        data_invalid = {
            'email': email_invalid,
            'password': password_invalid
        }
        response = client.post(url, data=data_invalid)

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` с некорректными данными, '
            f'возвращается код {code_expected}'
        )
        assert {field: [value]} == response.json(), (
            f'Убедитесь, что при запросе `{url}` с некорректными данными, '
            f'возвращается код {code_expected} с сообщением {value}'
        )

        email_valid = user.email
        data_invalid = {
            'email': email_valid,
            'password': password_invalid
        }
        response = client.post(url, data=data_invalid)

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` с некорректным паролем, '
            f'возвращается код {code_expected}'
        )
        assert {field: [value]} == response.json(), (
            f'Убедитесь, что при запросе `{url}` с некорректным паролем, '
            f'возвращается код {code_expected} с сообщением {value}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_login__valid_request_data(self, client, user):
        code_expected = 200
        field_in_response = 'auth_token'

        url = self.url_login
        valid_data = {
            'email': user.email,
            'password': 'Password654321'
        }
        response = client.post(url, data=valid_data)

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` с валидными данными, '
            f'возвращается код {code_expected}'
        )
        assert field_in_response in response.json().keys(), (
            f'Убедитесь, что при запросе `{url}` с валидными данными, '
            f' в ответе возвращается код {code_expected} с ключом '
            f'{field_in_response}, где содержится токен'
        )

    @pytest.mark.django_db(transaction=True)
    def test_logout(self, client, user_client):
        url = self.url_logout
        response = user_client.post(url)

        code_expected = 204
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` от авторизованного '
            f'пользователя, возвращается код {code_expected}'
        )

        response = client.post(url)
        field = 'detail'
        value = 'Учетные данные не были предоставлены.'
        code_expected = 401
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` от неавторизованного '
            f'пользователя, возвращается код {code_expected}'
        )
        assert {field: value} == response.json(), (
            f'Убедитесь, что при запросе `{url}` от неавторизованного '
            f'пользователя, возвращается код {code_expected} '
            f'с сообщением {value}'
        )
