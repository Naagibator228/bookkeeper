

from inspect import get_annotations
import sqlite3

from typing import Any
from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    def __init__(self, db_file: str, cls: type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

    def add(self, obj: T) -> int:
        if not isinstance(obj, self.cls):
            raise ValueError(f'trying to add object {obj} of wrong type')
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        names = ', '.join(self.fields.keys())
        p = ', '.join("?" * len(self.fields))
        values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            print(f"INSERT INTO {self.table_name} ({names}) VALUES ({p})", values)
            cur.execute(f"INSERT INTO {self.table_name} ({names}) VALUES ({p})", values)
            obj.pk = cur.lastrowid
        con.close()
        return obj.pk


    def get(self, pk: int) -> T:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            print(self.get_all())
            cur.execute(f"SELECT * FROM {self.table_name} WHERE pk=?", (pk,))
            result = cur.fetchone()
            if result is None:
                return None
            obj_dict = dict(zip(self.fields.keys(), result[1:]))
            obj_dict['pk'] = pk
        con.close()
        return self.cls(**obj_dict)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        query = f'SELECT * FROM {self.table_name}'
        values = ()
        if where:
            query += ' WHERE '
            conditions = []
            for key, value in where.items():
                conditions.append(f'{key}=?')
                values += (value,)
            query += ' AND '.join(conditions)
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(query, values)
            results = cur.fetchall()
            objects = []
            for result in results:
                print(result)
                obj_dict = dict(zip(self.fields.keys(), result[1:]))
                obj_dict['pk'] = result[0]
                objects.append(self.cls(**obj_dict))
            return objects

    def update(self, obj: T) -> None:
        if not hasattr(obj, 'pk') or obj.pk == 0:
            raise ValueError("Object must have a primary key to be updated")
        fields = [f'{key}=?' for key in self.fields.keys()]
        values = [getattr(obj, key) for key in self.fields.keys()]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(
                f'UPDATE {self.table_name} SET {", ".join(fields)} WHERE pk=?', values + [obj.pk])

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute('PRAGMA foreign_keys = ON')
            cur.execute(f'DELETE FROM {self.table_name} WHERE pk=?', (pk,))
            if cur.rowcount == 0:
                raise KeyError(f"trying to delete nonexistent object with pk={pk}")