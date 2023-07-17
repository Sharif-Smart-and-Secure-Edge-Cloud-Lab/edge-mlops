from flask import Flask

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
    return "Building Docker image..."

# Build provided model name
@app.route("/build/<model_name>")
def build_model(model_name):
    return f"Building {model_name}..."

# Deploy provided model name if built
@app.route("/deploy/<model_name>")
def deploy_model(model_name):
    return f"Deploying {model_name}"
