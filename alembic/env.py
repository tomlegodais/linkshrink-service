import importlib
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from core import Config, Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


def set_postgres_url() -> None:
    config.set_main_option('sqlalchemy.url', Config.POSTGRES_URL)


def import_models_for_migrations() -> None:
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), '../app/models')):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            importlib.import_module(f'models.{module_name}')


set_postgres_url()
import_models_for_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()