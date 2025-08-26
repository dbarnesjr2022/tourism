from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from typing import Any, Dict, cast

# allow importing the project package by inserting the repository root (one level above `backend`)
# into sys.path so `import backend` resolves correctly when running alembic from `backend/`.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.app.db import DATABASE_URL, Base  # noqa: E402

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name:
    fileConfig(config.config_file_name)

# set sqlalchemy.url if not present
if not config.get_main_option('sqlalchemy.url'):
    config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL', DATABASE_URL))

target_metadata = Base.metadata
# Ensure model modules are imported so SQLAlchemy metadata is populated for autogenerate
import backend.app.models  # noqa: F401
# Reference the imported models module so static checkers (Pylance/pyright) mark it as used
_ = backend.app.models


def run_migrations_offline():
    url = config.get_main_option('sqlalchemy.url')
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # config.get_section(...) can return None; cast to Dict[str, Any] with a safe empty fallback
    configuration: Dict[str, Any] = cast(Dict[str, Any], config.get_section(config.config_ini_section) or {})
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
