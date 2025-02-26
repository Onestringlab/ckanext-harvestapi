#!/bin/bash

# Pesan commit untuk git
COMMIT_MESSAGE="Initial Commit"

# Perintah git di host
git add .
git commit -m "$COMMIT_MESSAGE"
git push -u origin master

# URL repository
REPO_URL="https://repo.tech-dev.id/sdi/ckan/ckanext-harvestapi.git"

# Nama container Docker
CONTAINER_NAME="ckan"

# Path ke direktori ekstensi di dalam container
EXT_PATH="/srv/app/ckanext-harvestapi"

# Perintah untuk menjalankan pembaruan
docker exec "$CONTAINER_NAME" bash -c "
    [ ! -d $EXT_PATH ] && git clone $REPO_URL $EXT_PATH
    cd $EXT_PATH && git pull && pip install -e .
"

# Restart container (opsional, hapus jika tidak diperlukan)
docker restart "$CONTAINER_NAME"
