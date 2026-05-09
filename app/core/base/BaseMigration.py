from __future__ import annotations

from typing import ClassVar

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, text
from sqlalchemy.orm import Session


class BaseMigration:
    table_name: ClassVar[str | None] = None

    @classmethod
    def get_table_name(cls) -> str:
        if cls.table_name:
            return cls.table_name
        raise ValueError(f"{cls.__name__} precisa definir table_name.")

    @classmethod
    def base_columns(cls) -> list[Column]:
        return [
            Column("id", Integer, primary_key=True),
            Column("uuid", String(36), unique=True, index=True, nullable=False),
            Column("created_at", DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP")),
            Column("deleted_at", DateTime(timezone=True), nullable=True),
        ]

    @classmethod
    def build_table(cls, *columns: Column) -> Table:
        return Table(cls.get_table_name(), MetaData(), *cls.base_columns(), *columns)

    @classmethod
    def create_table(cls, db: Session, *columns: Column) -> None:
        cls.build_table(*columns).create(bind=db.get_bind(), checkfirst=True)

    @classmethod
    def drop_table(cls, db: Session) -> None:
        Table(cls.get_table_name(), MetaData()).drop(bind=db.get_bind(), checkfirst=True)
