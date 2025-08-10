#!/bin/bash
### Performs a full reset of the shopping environment.
### Note: This takes a while (~2 minutes), so it's not recommended to run this too frequently.

# Define variables
CONTAINER_NAME="shopping_admin"
BASE_URL="<your_base_url>" # Change this to your server's IP address

docker stop $CONTAINER_NAME
sleep 10
docker rm shopping_admin

docker run --name shopping_admin -p 7780:80 -d shopping_admin_final_0719
# wait ~1 min to wait all services to start
sleep 30

docker exec shopping_admin /var/www/magento2/bin/magento setup:store-config:set --base-url="http://$BASE_URL:7780" # no trailing slash
docker exec shopping_admin mysql -u magentouser -pMyPassword magentodb -e  'UPDATE core_config_data SET value="http://$BASE_URL:7780/" WHERE path = "web/secure/base_url";'
docker exec shopping_admin /var/www/magento2/bin/magento cache:flush
# sleep 30
