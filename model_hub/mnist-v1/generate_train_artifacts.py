import onnx
from onnxruntime.training import artifacts

onnx_model = onnx.load("../../emlops_train/mnist-v1/trained_model.onnx")

requires_grad = ["fc1.weight", "fc1.bias", "fc2.weight", "fc2.bias"]
frozen_params = [
    param.name
    for param in onnx_model.graph.initializer
    if param.name not in requires_grad
]

artifacts.generate_artifacts(
    onnx_model,
    requires_grad=requires_grad,
    frozen_params=frozen_params,
    loss=artifacts.LossType.CrossEntropyLoss,
    optimizer=artifacts.OptimType.AdamW,
    artifact_directory="model"
)
