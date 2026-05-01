import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 1. Biar bisa import dari folder root project
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# 2. Load .env
from dotenv import load_dotenv
load_dotenv()

# 3. Import Base + semua model lu
from app.database import Base
from app.models.user import User, UserRole
from app.models.course import Course
from app.models.chapter import Chapter
from app.models.enrollment import Enrollment

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 4. Kasih tau Alembic metadata lu ada dimana
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # 5. Override sqlalchemy.url dari alembic.ini pake .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()