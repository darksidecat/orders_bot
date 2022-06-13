# script to copy redis.conf to VOLUMES_DIR from environment variable
#
# Usage: prepare_volumes.sh
#

# check if enviroment variable is set
if [ -z "$VOLUMES_DIR" ]; then
  echo "VOLUMES_DIR is not set"
  exit 1
fi

# create VOLUMES_DIR if it doesn't exist
if [ ! -d "${HOME}/${VOLUMES_DIR}" ]; then
  mkdir -p "${HOME}/${VOLUMES_DIR}"
fi


# create in VOLUMES_DIR pg-data directory if it doesn't exist
if [ ! -d "${HOME}/${VOLUMES_DIR}/pg-data" ]; then
  mkdir -p "${HOME}/${VOLUMES_DIR}/pg-data"
fi

# create in VOLUMES_DIR redis-data directory if it doesn't exist
if [ ! -d "${HOME}/${VOLUMES_DIR}/redis-data" ]; then
  mkdir -p "${HOME}/${VOLUMES_DIR}/redis-data"
fi

# create in VOLUMES_DIR redis-config directory if it doesn't exist
if [ ! -d "${HOME}/${VOLUMES_DIR}/redis-config" ]; then
  mkdir -p "${HOME}/${VOLUMES_DIR}/redis-config"
fi

# copy redis.conf to VOLUMES_DIR
cp ./redis.conf "${HOME}/${VOLUMES_DIR}/redis-config/redis.conf"


# check if redis.conf was copied
if [ -f "${HOME}/${VOLUMES_DIR}/redis-config/redis.conf" ]; then
  echo "redis.conf was copied to VOLUMES_DIR"
else
  echo "redis.conf was not copied to VOLUMES_DIR"
  exit 1
fi