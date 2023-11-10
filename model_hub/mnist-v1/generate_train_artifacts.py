#!/usr/bin/env python

import os
import shutil
import argparse
import onnx
from onnxruntime.training import artifacts

def main(model_path: str):
    onnx_model = onnx.load(model_path)
    #FIXME: must be modified if model structure changes
    requires_grad = ["conv1.weight", "conv1.bias",
                    "conv2.weight", "conv2.bias",
                    "fc1.weight", "fc1.bias",
                    "fc2.weight", "fc2.bias"]
    frozen_params = [
        param.name
        for param in onnx_model.graph.initializer
        if param.name not in requires_grad
    ]

    if not os.path.isdir("model"):
        os.makedirs("model")

    print("Generating artifacts...")
    artifacts.generate_artifacts(
        onnx_model,
        requires_grad=requires_grad,
        frozen_params=frozen_params,
        loss=artifacts.LossType.CrossEntropyLoss,
        optimizer=artifacts.OptimType.AdamW,
        artifact_directory="model"
    )
    # copy inference model, too
    shutil.copyfile(model_path, "model/inference.onnx")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="TrainArtifactGen",
        description="Generate ORT training artifacts"
    )
    parser.add_argument("-m", "--model", help="Path to a valid ONNX model", required=True)
    args = vars(parser.parse_args())
    main(args['model'])
