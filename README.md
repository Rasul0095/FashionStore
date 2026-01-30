
docker network create Mynetwork

docker run --name store_db \
    -p 6432:5432 \
    -e POSTGRES_USER=rasul \
    -e POSTGRES_PASSWORD=root \
    -e POSTGRES_DB=fashion_store \
    --network=Mynetwork \
    --volume pg-store-data:/var/lib/postgresql/data \
    -d postgres:17


docker run --name store_cache \
    -p 7379:6379 \
    --network=Mynetwork \
    -d redis:7.4


docker run --name store_back \
    -p 8888:8000 \
    --network=Mynetwork \
    store_image


docker run --name store_celery_worker \
    --network=Mynetwork \
    store_image \
    celery --app=src.tasks.celery_app:celery_instance worker -l INFO

docker build -t store_image .
docker stop store_back
docker compose build
docker compose up
docker compose down

