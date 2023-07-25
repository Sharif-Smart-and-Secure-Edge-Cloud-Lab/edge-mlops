import os 
import docker
from emlops_deploy import *

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
    