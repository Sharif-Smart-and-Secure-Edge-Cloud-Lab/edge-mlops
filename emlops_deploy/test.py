import docker
import os
from emlops_deploy import *
import subprocess
import shlex
# import emlops_deploy.docker_api as dapi

docker_client = docker.from_env()

deploy_module_cont = docker_client.containers.run(DEPLOY_MODULE_DOCKER_TAG,
                                                  command="tail -f /dev/null",
                                                  detach=True,
                                                  remove=True)

model_name = "imdb-v1"
cont_id = deploy_module_cont.id

# Copy files
subprocess.run(shlex.split(f"docker cp {PROJECT_ROOT_DIR}/model_hub/{model_name} {cont_id}:/{model_name}"))

status, output = deploy_module_cont.exec_run(f"chmod +x /{model_name}/build.sh")
print(f"{status} -> \n{output.decode('utf-8')}")

status, output = deploy_module_cont.exec_run(f"/{model_name}/build.sh")
print(f"{status} -> \n{output.decode('utf-8')}")

deploy_module_cont.stop()
