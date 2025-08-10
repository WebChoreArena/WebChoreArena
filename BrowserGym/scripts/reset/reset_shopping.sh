#!/bin/bash
### Performs a full reset of the shopping environment.
### Note: This takes a while (~2 minutes), so it's not recommended to run this too frequently.

# Define variables
CONTAINER_NAME="shopping"
BASE_URL="<your_base_url>" # Change this to your server's IP address

docker stop $CONTAINER_NAME
sleep 20
echo "Removing container $CONTAINER_NAME"
docker rm $(docker ps -a | grep $CONTAINER_NAME | awk '{print $1}')
docker run --name $CONTAINER_NAME -p 7770:80 -d shopping_final_0712
echo "Waiting for all services to start"
# wait ~1 min for all services to start
sleep 60

echo $CONTAINER_NAME
docker exec $CONTAINER_NAME /var/www/magento2/bin/magento setup:store-config:set --base-url="http://$BASE_URL:7770" # no trailing slash
docker exec $CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e  'UPDATE core_config_data SET value="http://$BASE_URL:7770" WHERE path = "web/secure/base_url";'
docker exec $CONTAINER_NAME /var/www/magento2/bin/magento cache:flush