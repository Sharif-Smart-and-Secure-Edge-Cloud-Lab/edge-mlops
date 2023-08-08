import json

data = {
    "Model": "BoW"
}

with open("data.json", "w") as file:
    json.dump(data, file)