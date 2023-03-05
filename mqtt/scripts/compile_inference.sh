#!/bin/bash
# Running a docker container and save the ID
echo "Runnig container..."
DOCKID=$(sudo docker run -d -ti edgemlops:1.0.0 /bin/bash)
echo "The container is now alive with ID: $DOCKID"

sudo docker cp ./inference $DOCKID:/inference
sudo docker cp ./convert_model $DOCKID:/convert_model
sudo docker cp ./scripts/build_inference.sh $DOCKID:/build_inference.sh
sudo docker exec $DOCKID sh -c "chmod +x /build_inference.sh && /build_inference.sh"

sudo docker cp $DOCKID:/test ./test
sudo docker stop $DOCKID
# sudo docker exec $DOCKID /test.sh
