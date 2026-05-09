from __future__ import annotations

from typing import ClassVar

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, MetaData, String, Table, Text, text
from sqlalchemy.orm import Session


class BaseMigration:
    table_name: ClassVar[str | None] = None

    def __init__(self, db: Session) -> None:
        self.db = db

    @classmethod
    def get_table_name(cls) -> str:
        if cls.table_name:
            return cls.table_name
        raise ValueError(f"{cls.__name__} precisa definir table_name.")

    @classmethod
    def raw_default(cls, expression: str):
        return text(expression)

    @classmethod
    def current_timestamp_default(cls):
        return text("CURRENT_TIMESTAMP")

    @classmethod
    def column(cls, name: str, type_: object, **kwargs) -> Column:
        return Column(name, type_, **kwargs)

    @classmethod
    def id_column(cls) -> Column:
        return Column("id", Integer, primary_key=True)

    @classmethod
    def uuid_column(cls) -> Column:
        return Column("uuid", String(36), unique=True, index=True, nullable=False)

    @classmethod
    def created_at_column(cls) -> Column:
        return Column("created_at", DateTime(timezone=True), nullable=False, server_default=cls.current_timestamp_default())

    @classmethod
    def updated_at_column(cls) -> Column:
        return Column("updated_at", DateTime(timezone=True), nullable=False, server_default=cls.current_timestamp_default())

    @classmethod
    def deleted_at_column(cls) -> Column:
        return Column("deleted_at", DateTime(timezone=True), nullable=True)

    @classmethod
    def base_columns(cls) -> list[Column]:
        return [
            cls.id_column(),
            cls.uuid_column(),
            cls.created_at_column(),
            cls.updated_at_column(),
            cls.deleted_at_column(),
        ]

    def build_table(self, *columns: Column) -> Table:
        return Table(self.get_table_name(), MetaData(), *self.base_columns(), *columns)

    def create_table(self, *columns: Column) -> None:
        self.build_table(*columns).create(bind=self.db.get_bind(), checkfirst=True)

    def drop_table(self) -> None:
        Table(self.get_table_name(), MetaData()).drop(bind=self.db.get_bind(), checkfirst=True)

    @classmethod
    def string(cls, name: str, length: int = 255, **kwargs) -> Column:
        return Column(name, String(length), **kwargs)

    @classmethod
    def text_column(cls, name: str, **kwargs) -> Column:
        return Column(name, Text, **kwargs)

    @classmethod
    def integer(cls, name: str, **kwargs) -> Column:
        return Column(name, Integer, **kwargs)

    @classmethod
    def float(cls, name: str, **kwargs) -> Column:
        return Column(name, Float, **kwargs)

    @classmethod
    def indexed(cls, name: str, type_: object, **kwargs) -> Column:
        return Column(name, type_, index=True, **kwargs)

    @classmethod
    def unique(cls, name: str, type_: object, **kwargs) -> Column:
        return Column(name, type_, unique=True, index=True, **kwargs)

    @classmethod
    def foreign_id(cls, name: str, table_name: str, column_name: str = "id", **kwargs) -> Column:
        return Column(name, Integer, ForeignKey(f"{table_name}.{column_name}"), index=True, **kwargs)

    @classmethod
    def foreign_uuid(cls, name: str, table_name: str, column_name: str = "uuid", **kwargs) -> Column:
        return Column(name, String(36), ForeignKey(f"{table_name}.{column_name}"), index=True, **kwargs)

    @classmethod
    def boolean(cls, name: str, **kwargs) -> Column:
        return Column(name, Boolean, **kwargs)

    @classmethod
    def json(cls, name: str, **kwargs) -> Column:
        return Column(name, JSON, **kwargs)

    @classmethod
    def datetime(cls, name: str, **kwargs) -> Column:
        return Column(name, DateTime(timezone=True), **kwargs)
