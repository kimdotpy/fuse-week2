FROM postgres:15

# Copy SQL seed file into the Postgres init directory
# Postgres will run any *.sql files found in /docker-entrypoint-initdb.d/ when the database is initialized.
COPY app/sql/seed.sql /docker-entrypoint-initdb.d/seed.sql

EXPOSE 5432
