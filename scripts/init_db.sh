#!/bin/bash

# Load environment variables
source ../.env

# Check if psql is installed
if ! command -v psql &> /dev/null; then
    echo "Error: psql is not installed. Please install PostgreSQL client tools."
    exit 1
fi

# Initialize the database
echo "Initializing database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f init_db.sql

if [ $? -eq 0 ]; then
    echo "Database initialized successfully!"
else
    echo "Error initializing database."
    exit 1
fi 