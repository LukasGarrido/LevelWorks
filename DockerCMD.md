# Levantar todo el proyecto
docker-compose up -d

# Detener todo el proyecto
docker-compose down

# Levantar todo el proyecto sin cache
docker-compose up -d --build

# Entrar a la terminal de postgres
docker exec -it xperience-db-1 psql -U <Usuario> -d <NombreBD>

# Entrar a la terminal de fastapi
docker exec -it xperience-web-1 bash

# Recargar el servidor
docker-compose restart web

# Reiniciar servidor y reconstruir imagen
docker-compose restart web