import os
import docker
from emlops_deploy import *
import subprocess
import shlex

# Docker API handler
docker_client = docker.from_env()
# Deploy container object
deploy_container = None


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
        img, logs = docker_client.images.build(path=PROJECT_ROOT_DIR,
                                               tag=DEPLOY_MODULE_DOCKER_TAG,
                                               quiet=False,
                                               dockerfile="Dockerfile")
        #TODO: Try to output the log concurrently (not provided by Docker API)
        for log in logs:
            if 'stream' in log:
                for line in log['stream'].splitlines():
                    logging.info(line)
        # Change directory back to avoid confusion in other modules
        os.chdir(cwd)
        docker_build_status[id] = True
    except Exception:
        logging.error("Unable to build image! Exception occured")
        os.chdir(cwd)
        docker_build_status[id] = False


def run_deploy_cont():
    global deploy_container
    if deploy_container is None:
        logging.info("Running deploy container...")
        deploy_container = docker_client.containers.run(DEPLOY_MODULE_DOCKER_TAG,
                                                        command="tail -f /dev/null",
                                                        detach=True,
                                                        remove=True)
    elif deploy_container.status != "running":
        # rerun again
        logging.warning("Deploy container in stopped! restarting...")
        deploy_container.restart()


def stop_deploy_cont():
    if deploy_container is not None:
        deploy_container.stop()


def build_model(model_name):
    """
    Builds model in emlops container

    :param model_name: model name
    :type model_name: str
    :return: None
    """
    #FIXME: Currently only builds imdb-v1 pipeline
    run_deploy_cont()

    cont_id = deploy_container.id
    subprocess.run(shlex.split(f"docker cp {PROJECT_ROOT_DIR}/model_hub/{model_name} {cont_id}:/{model_name}"))

    status, output = deploy_container.exec_run(f"chmod +x /{model_name}/build.sh")
    logging.info(f"{status} -> \n{output.decode('utf-8')}")

    status, output = deploy_container.exec_run(f"/{model_name}/build.sh")
    logging.info(f"{status} -> \n{output.decode('utf-8')}")

    all_pipelines.append(model_name)
    logging.info("Image created successfully!")


def deploy_model(model_name):
    #FIXME: Currently only builds imdb-v1 pipeline
    logging.info(deploy_container.status)
    if deploy_container.status != "stopped":
        logging.info("Deploying model to local...")
        cont_id = deploy_container.id
        #FIXME: Check the output of subprocess
        subprocess.run(shlex.split(f"docker cp {cont_id}:/{model_name}/install/. {PROJECT_ROOT_DIR}/emlops_deploy/exec_hub/{model_name}"))
        return True
    else:
        logging.error("Deploy container is not running!")
        return False
