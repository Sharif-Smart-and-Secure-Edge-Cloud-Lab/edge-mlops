import os
from pathlib import Path
import logging
from logging.config import dictConfig

EMLOPS_DEPLOY_DIR = os.path.dirname(os.path.realpath(__file__))

PROJECT_ROOT_DIR = str(Path(EMLOPS_DEPLOY_DIR).parent.absolute())

LATEST_EMLOPS_VERSION = "0.2.0"
DEPLOY_MODULE_DOCKER_IMAGE_NAME = "edgemlops"
DEPLOY_MODULE_DOCKER_TAG = f"{DEPLOY_MODULE_DOCKER_IMAGE_NAME}:{LATEST_EMLOPS_VERSION}"


# At most 4 threads will be used
MAX_NUM_BUILD_THREADS = 4
docker_build_status = [False]*MAX_NUM_BUILD_THREADS
docker_build_threads = [None]*MAX_NUM_BUILD_THREADS

# List of all previously run pipeling
all_pipelines = []

# Logger configuration
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
