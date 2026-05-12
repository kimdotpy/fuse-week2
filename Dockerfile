FROM postgres:16

# -----------------------------------------------------------------------------
# Labels
# -----------------------------------------------------------------------------
LABEL maintainer="fuse-wk2"
LABEL description="PostgreSQL 16 image pre-seeded with app/sql/seed.sql"

# -----------------------------------------------------------------------------
# Seed data
# Postgres automatically executes *.sql files placed in this directory
# the very first time the container starts (i.e., when the data volume is empty).
# Files are run in alphabetical order, so prefix with numbers if ordering matters.
# -----------------------------------------------------------------------------
COPY app/sql/seed.sql /docker-entrypoint-initdb.d/01_seed.sql

EXPOSE 5432
