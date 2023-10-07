import os
import pytest
import time

pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]


@pytest.fixture(scope="session", autouse=True)
def auto_session_resource(request):
    start = time.time()

    def auto_session_resource_teardown():
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = f'{root_dir}/backend/media/recipes/'
        finish = time.time()
        try:
            files = os.listdir(os.path.join(path))
            for file in files:
                if os.path.isfile(path + file):
                    stat = os.stat(path + file)
                    created_time = stat.st_ctime
                    if start <= created_time <= finish:
                        os.remove(path + file)
            print('\nТестовые файлы удалены\n')
        except FileNotFoundError:
            print('\nТестовые файлы не найдены\n')

    request.addfinalizer(auto_session_resource_teardown)
