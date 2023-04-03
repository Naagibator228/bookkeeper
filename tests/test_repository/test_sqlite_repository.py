from bookkeeper.repository.sqlite_repository import SQLiteRepository
from sqlite3 import IntegrityError


import pytest
import typing
import sqlite3


class Custom():
    name: str
    pk: int = 0
    def __init__(self, pk: int = 0, name:str = None):
        self.pk = pk
        self.name = name

class Category():
    customer_id: int
    purchase: str
    pk: int = 0
    def __init__(self, pk: int = 0, customer_id:int = None, purchase: str = None):
        self.pk = pk
        self.customer_id = customer_id
        self.purchase = purchase

@pytest.fixture
def custom_class()-> Custom:
    return Custom

custom_variable = Custom
custom_variable_ = Category
x = iter(list(range(0,1000)))

@pytest.fixture
def repo():
    with sqlite3.connect("custom") as con:
        # con.execute(("DROP TABLE custom"))
        con.execute("CREATE TABLE IF NOT EXISTS custom (pk INTEGER PRIMARY KEY, name TEXT)")
        con.execute(f"INSERT INTO custom (pk, name) VALUES ({next(x)}, 'John')")
        con.execute(f"INSERT INTO custom (pk, name) VALUES ({next(x)}, 'Jane')")
    yield SQLiteRepository("custom", custom_variable)

    # Удаляем таблицу и закрываем соединение с базой данных
    # con.execute("DROP TABLE custom")
    con.close()

@pytest.fixture
def repo_():
    with sqlite3.connect("custom") as con:
        con.execute('PRAGMA foreign_keys = ON')
        con.execute("CREATE TABLE IF NOT EXISTS category (pk INTEGER PRIMARY KEY, customer_id INTEGER, purchase TEXT, FOREIGN KEY (customer_id) REFERENCES custom(pk))")
        con.execute(f"INSERT INTO category (pk, customer_id, purchase) VALUES ({next(x)},  1, 'p')")
        con.execute(f"INSERT INTO category (pk, customer_id, purchase) VALUES ({next(x)}, 2, 'f')")
    yield SQLiteRepository("custom", custom_variable_)
    con.execute("DROP TABLE category")
    con.execute("DROP TABLE custom")
    con.close()

def test_crud(repo, custom_class):
    obj = custom_class()
    obj.name = "test"
    print(obj.name)
    pk = repo.add(obj)
    assert obj.pk == pk
    assert repo.get(pk).name == "test"
    obj2 = custom_class()
    obj2.pk = pk
    obj2.name = "test2"
    repo.update(obj2)
    assert repo.get(pk).name == "test2"
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo, custom_class):
    obj = custom_class()
    obj.pk = 1
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo):
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_delete_unexistent(repo):
    with pytest.raises(KeyError):
        repo.delete(100444)


def test_cannot_update_without_pk(repo, custom_class):
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_all(repo, custom_class):
    con = sqlite3.connect('custom')
    cur = con.cursor()
    cur.execute('DELETE FROM custom')
    con.commit()
    con.close()
    objects = [custom_class() for i in range(5)]
    for o in objects:
        repo.add(o)
    assert len(repo.get_all()) == len(objects)


def test_get_all_with_condition(repo):
    obj1 = Custom(name="Johny")
    obj2 = Custom(name="Johny")
    obj3 = Custom(name="Lewis")
    obj4 = Custom(name='Lora')
    repo.add(obj1)
    repo.add(obj2)
    repo.add(obj3)

    # Get all objects where age is greater than 30
    results = repo.get_all({'name':'Johny'})
    assert len(results) == 2
    assert results[0].name == "Johny"


def test_foreign_keys(repo_):

    con_ = sqlite3.connect('custom')
    cur = con_.cursor()
    obj = Category(customer_id=999, purchase='p')
    with pytest.raises(IntegrityError):
        repo_.add(obj)
    obj = Category(customer_id=2, purchase='f')
    repo_.add(obj)
    results = repo_.get_all()
    assert len(results) == 3
    con_.commit()
    con_.close()
