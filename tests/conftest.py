import pytest
import pandas as pd
import os


@pytest.fixture(scope="session")
def test_data_dir():
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture(autouse=True)
def setup_test_env(test_data_dir):
    # Criar diretório de teste se não existir
    os.makedirs(test_data_dir, exist_ok=True)
    yield
    # Cleanup após os testes (opcional)
    # os.rmdir(test_data_dir)
