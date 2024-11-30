#!/bin/bash

# Load environment variables from the .env file
set -o allexport
source taskmanager/taskmanager/.env
set +o allexport

# Define container name or ID
CONTAINER_NAME="task-manager-api_postgresql_1"

# Execute commands in the PostgreSQL container
docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
DO
\$\$
BEGIN
   -- Grant privileges to the specific user on the specified database
   EXECUTE 'GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER';
END
\$\$;
"

# Echo a message when the script is finished
echo "Privileges have been successfully granted to $POSTGRES_USER on the database $POSTGRES_DB."
