import docker
import os
from emlops_deploy import *
import emlops_deploy.docker_api as dapi

dapi.is_image_exist(DEPLOY_MODULE_DOCKER_TAG)

