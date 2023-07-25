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
        status['exists'] = True
        status['building'] = False
    else:
        # Build docker image
        for i in range(MAX_NUM_BUILD_THREADS):
            if docker_build_threads[i] is None:
                # empty id
                build_thread = threading.Thread(target=dapi.build_emlops, args=(i,))
                docker_build_threads[i] = build_thread
                build_thread.start()
                status['exists'] = False
                status['building'] = True
                break
            elif not docker_build_threads[i].is_alive():
                # Thread is dead, reuse the ID
                build_thread = threading.Thread(target=dapi.build_emlops, args=(i,))
                docker_build_threads[i] = build_thread
                build_thread.start()
                status['exists'] = False
                status['building'] = True
                break
        else:
            # We couldn't found an ID, so try again later...
            status['exists'] = False
            status['building'] = False

    return jsonify(status)

# Build provided model name
@app.route("/build/<model_name>")
def build_model(model_name):
    # First check if deploy module Docker is built
    if not dapi.is_image_exist(DEPLOY_MODULE_DOCKER_TAG):
        return "Deploy module Docker image is not built yet. Try again!"
    

# Deploy provided model name if built
@app.route("/deploy/<model_name>")
def deploy_model(model_name):
    return f"Deploying {model_name}"

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
