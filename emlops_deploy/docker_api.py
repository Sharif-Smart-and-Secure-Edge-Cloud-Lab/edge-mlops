import os 
import docker
from emlops_deploy import *
import subprocess
import shlex

docker_client = docker.from_env()

def is_image_exist(in_tag):
    """
    Checks whether input tag exists in local registry.

    :param in_tag: input tag to check if exists
    :type in_tag: str
    :return: Flag specifing whether image exists or not
    """
    found_img = docker_client.images.list(name=in_tag, filters={"dangling": False})
    if len(found_img):
        return True
    else:
        return False

def build_emlops(id):
    """
    Builds deploy module Docker image.

    :return: None - Status is written in common status list
    """
    docker_build_status[id] = False
    cwd = os.getcwd()
    # Dockerfile must be run from the project ROOT path
    os.chdir(PROJECT_ROOT_DIR)
    try:
        img = docker_client.images.build(path=PROJECT_ROOT_DIR,
                                        tag=DEPLOY_MODULE_DOCKER_TAG,
                                        quiet=False,
                                        dockerfile="Dockerfile")
        # Change directory back to avoid confusion in other modules
        os.chdir(cwd)
        docker_build_status[id] = True
    except Exception:
        os.chdir(cwd)
        docker_build_status[id] = False
    
def build_model(model_name):
    """
    Builds model in emlops container

    :param model_name: model name
    :type model_name: str
    :return: None
    """
    #FIXME: Currently only runs for our imdb-v1 pipeline
    deploy_module_cont = docker_client.containers.run(DEPLOY_MODULE_DOCKER_TAG,
                                                    command="tail -f /dev/null",
                                                    detach=True,
                                                    remove=True)
    cont_id = deploy_module_cont.id
    subprocess.run(shlex.split(f"docker cp {PROJECT_ROOT_DIR}/model_hub/{model_name} {cont_id}:/{model_name}"))
    status, output = deploy_module_cont.exec_run(f"chmod +x /{model_name}/build.sh")
    status, output = deploy_module_cont.exec_run(f"/{model_name}/build.sh")
    deploy_module_cont.stop()
