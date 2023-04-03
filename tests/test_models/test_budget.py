from datetime import datetime

import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Budget

@pytest.fixture
def repo():
    return MemoryRepository()

def test_create_with_full_args_list():
    e = Budget(term=datetime.now(), amount=1, category = 1, pk=1)
    assert e.amount == 1
    assert e.category == 1

def test_can_add_to_repo(repo):
    e = Budget(datetime.now(), 100, 1)
    pk = repo.add(e)
    assert e.pk == pk