import os
from pathlib import Path

EMLOPS_DEPLOY_DIR = os.path.dirname(os.path.realpath(__file__))

PROJECT_ROOT_DIR = str(Path(EMLOPS_DEPLOY_DIR).parent.absolute())

LATEST_EMLOPS_VERSION = "0.2.0"
DEPLOY_MODULE_DOCKER_IMAGE_NAME = "edgemlops"
DEPLOY_MODULE_DOCKER_TAG = f"{DEPLOY_MODULE_DOCKER_IMAGE_NAME}:{LATEST_EMLOPS_VERSION}"


# At most 4 threads will be used
MAX_NUM_BUILD_THREADS = 4
docker_build_status = [False]*MAX_NUM_BUILD_THREADS
docker_build_threads = [None]*MAX_NUM_BUILD_THREADS