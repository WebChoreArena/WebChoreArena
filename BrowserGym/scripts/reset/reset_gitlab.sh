
#!/bin/bash
### Performs a full reset of the shopping environment.
### Note: This takes a while (~2 minutes), so it's not recommended to run this too frequently.

# Define variables
CONTAINER_NAME="gitlab"

docker stop $CONTAINER_NAME
sleep 20
docker remove $CONTAINER_NAME


docker run --name gitlab -d -p 8023:8023 gitlab-populated-final-port8023 /opt/gitlab/embedded/bin/runsvdir-start

seep 100
# wait at least 5 mins for services to boot
docker exec gitlab sed -i "s|^external_url.*|external_url 'http://localhost:8023'|" /etc/gitlab/gitlab.rb
docker exec gitlab gitlab-ctl reconfigure