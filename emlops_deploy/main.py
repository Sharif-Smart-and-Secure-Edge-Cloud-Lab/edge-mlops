# import logging
import threading
from flask import Flask, jsonify
from emlops_deploy import *
import emlops_deploy.docker_api as dapi


app = Flask(__name__)

@app.route("/")
def main_page():
    return """<h1> Deploy Module Main Page </h1>
              <p> Part of the EMlops framework, specialized in
              deploying apps </p>
           """

# Build Dockerfile
@app.route("/build")
def build_docker_image():
    status = dict()
    # Check whether image exists:
    img_exists = dapi.is_image_exist(DEPLOY_MODULE_DOCKER_TAG)
    if img_exists:
        logging.info("Deploy image already exists, not building again.")
        status['exists'] = True
        status['building'] = False
    else:
        # Build docker image
        for i in range(MAX_NUM_BUILD_THREADS):
            if docker_build_threads[i] is None:
                # empty id
                logging.info("Building deployer Docker image")
                build_thread = threading.Thread(target=dapi.build_emlops, args=(i,))
                docker_build_threads[i] = build_thread
                build_thread.start()
                status['exists'] = False
                status['building'] = True
                break
            elif not docker_build_threads[i].is_alive():
                # Thread is dead, reuse the ID
                logging.info("Building deployer Docker image")
                build_thread = threading.Thread(target=dapi.build_emlops, args=(i,))
                docker_build_threads[i] = build_thread
                build_thread.start()
                status['exists'] = False
                status['building'] = True
                break
        else:
            # We couldn't found an ID, so try again later...
            logging.warning("No free thread found for building process, try again later!")
            status['exists'] = False
            status['building'] = False

    return jsonify(status)

# Build provided model name
@app.route("/build/<model_name>")
def build_model(model_name: str):
    status = dict()
    # First check if deploy module image has been built
    if not dapi.is_image_exist(DEPLOY_MODULE_DOCKER_TAG):
        logging.error("Deploy module image has not been built. Build it with 'build' API")
        status['deploy_exists'] = False
        status[model_name] = False
    else:
        logging.info(f"Building {model_name} pipeline...")
        dapi.build_model(model_name)
        status['deploy_exists'] = True
        status[model_name] = True

    return jsonify(status)

# Deploy provided model name if built
@app.route("/deploy/<model_name>")
def deploy_model(model_name):
    status = dict()
    if model_name in all_pipelines:
        dapi.deploy_model(model_name)
        status[model_name] = True
    else:
        logging.error("Pipeline has not been built, first build the pipeline")
        status[model_name] = False
    return jsonify(status)

# Statistics of the server:
@app.route("/stat")
def get_stat():
    msg = "<strong>Thread lifetime:</strong><br>"
    for id, t in enumerate(docker_build_threads):
        if t is None:
            msg += f"Thread {id} -> Not used | "
        elif t.is_alive():
            msg += f"Thread {id} -> Alive | "
        else:
            msg += f"Thread {id} -> Dead | "
    msg += "<br><strong> Status: </strong><br>"
    for id, status in enumerate(docker_build_status):
            msg += f"Thread {id} -> {status} | "
    msg += "<br>"

    return msg

@app.route("/pipelines")
def get_pipelines_list():
    msg = "Pipeline name:<br>"
    for pipeline in all_pipelines:
        msg += f"{pipeline}<br>"

    return msg

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8080)
    finally:
        logging.info("Stopping deploy container...")
        dapi.stop_deploy_cont()
