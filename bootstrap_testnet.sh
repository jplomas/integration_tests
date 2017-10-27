#!/bin/sh

export DOCKER_UID=$( id -u ${USER} )
export DOCKER_GID=$( id -g ${USER} )
export NUM_NODES=4

echo "****************************************************************"
echo "****************************************************************"
echo "                     FLUSHING EVERYTHING"
echo "****************************************************************"
echo "****************************************************************"
#rm -r volumes/*

echo "****************************************************************"
echo "****************************************************************"
echo "                     BUILDING CONTAINERS"
echo "****************************************************************"
echo "****************************************************************"
export BOOT_PHASE=build
docker-compose build

echo "****************************************************************"
echo "****************************************************************"
echo "                       BOOTSTRAPPING"
echo "****************************************************************"
echo "****************************************************************"
export BOOT_PHASE=bootstrap
export LOCALNET_ONLY=yes
docker-compose up --scale node=${NUM_NODES}
python3 ./scripts/collect_wallets.py # Get Addresses and prepare genesis block

echo "****************************************************************"
echo "****************************************************************"
echo "                       STARTING LOCALNET"
echo "****************************************************************"
echo "****************************************************************"
export BOOT_PHASE=start
docker-compose up --scale node=${NUM_NODES}
