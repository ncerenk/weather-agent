import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import URL

from alembic import context
from dotenv import load_dotenv


# .env dosyasını yükle
load_dotenv()


# Alembic Config
config = context.config


# Logging ayarları
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Şimdilik SQLAlchemy model metadata kullanmıyoruz
target_metadata = None


# PostgreSQL bağlantı URL'sini .env üzerinden oluştur
database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

# alembic.ini içindeki dummy URL'yi override et
config.set_main_option(
    "sqlalchemy.url",
    database_url.render_as_string(hide_password=False),
)


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
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()