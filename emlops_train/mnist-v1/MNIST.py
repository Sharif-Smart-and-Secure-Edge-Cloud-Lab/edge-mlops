import onnxruntime.training.onnxblock as onnxblock
from onnxruntime.training.api import CheckpointState, Module, Optimizer
from onnxruntime import InferenceSession
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
import torch
import onnx
import io
import evaluate


# Offline Step

class MNISTNet(torch.nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super(MNISTNet, self).__init__()

        self.fc1 = torch.nn.Linear(input_size, hidden_size)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(hidden_size, num_classes)

    def forward(self, model_input):
        out = self.fc1(model_input)
        out = self.relu(out)
        out = self.fc2(out)
        return out

# MNISTNet instance    
device = "cpu"
batch_size, input_size, hidden_size, output_size = 64, 784, 500, 10
pt_model = MNISTNet(input_size, hidden_size, output_size).to(device)

# Random input
model_inputs = (torch.randn(batch_size, input_size, device=device),)
model_outputs = pt_model(*model_inputs)
if isinstance(model_outputs, torch.Tensor):
    model_outputs = [model_outputs]

input_names = ["input"]
output_names = ["output"]
dynamic_axes = {"input": {0: "batch_size"}, "output": {0: "batch_size"}}

f = io.BytesIO()
torch.onnx.export(
    pt_model,
    model_inputs,
    f,
    input_names=input_names,
    output_names=output_names,
    opset_version=14,
    do_constant_folding=False,
    training=torch.onnx.TrainingMode.TRAINING,
    dynamic_axes=dynamic_axes,
    export_params=True,
    keep_initializers_as_inputs=False,
)

onnx_model = onnx.load_model_from_string(f.getvalue())

# Creating a class with a Loss function.
class MNISTTrainingBlock(onnxblock.TrainingBlock):
    def __init__(self):
        super(MNISTTrainingBlock, self).__init__()
        self.loss = onnxblock.loss.CrossEntropyLoss()

    def build(self, output_name):
        return self.loss(output_name), output_name
    
# Build the onnx model with loss
training_block = MNISTTrainingBlock()
for param in onnx_model.graph.initializer:
    print(param.name)
    training_block.requires_grad(param.name, True)

# Building training graph and eval graph.
model_params = None
with onnxblock.base(onnx_model):
    _ = training_block(*[output.name for output in onnx_model.graph.output])
    training_model, eval_model = training_block.to_model_proto()
    model_params = training_block.parameters()

# Building the optimizer graph
optimizer_block = onnxblock.optim.AdamW()
with onnxblock.empty_base() as accessor:
    _ = optimizer_block(model_params)
    optimizer_model = optimizer_block.to_model_proto()

# Saving all the files to use them later for the training.
onnxblock.save_checkpoint(training_block.parameters(), "data/checkpoint")
onnx.save(training_model, "data/training_model.onnx")
onnx.save(optimizer_model, "data/optimizer_model.onnx")
onnx.save(eval_model, "data/eval_model.onnx")


# Data Preparation

batch_size = 64
train_kwargs = {'batch_size': batch_size}
test_batch_size = 1000
test_kwargs = {'batch_size': test_batch_size}

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

dataset1 = datasets.MNIST('../data', train=True, download=True,
                          transform=transform)
dataset2 = datasets.MNIST('../data', train=False,
                          transform=transform)
train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)


# Initialize Module and Optimizer

state = CheckpointState.load_checkpoint("data/checkpoint")
model = Module("data/training_model.onnx", state, "data/eval_model.onnx")
optimizer = Optimizer("data/optimizer_model.onnx", model)


# Run Training and Testing Loops

def get_pred(logits):
    return np.argmax(logits, axis=1)

def train(epoch):
    model.train()
    losses = []

    for _, (data, target) in enumerate(train_loader):
        forward_inputs = [data.reshape(len(data), 784).numpy(), target.numpy().astype(np.int64)]
        train_loss, _ = model(*forward_inputs)
        optimizer.step()
        model.lazy_reset_grad()
        losses.append(train_loss)

    print(f'Epoch: {epoch+1}, Train Loss: {sum(losses)/len(losses):.4f}')

def test(epoch):
    model.eval()
    losses = []
    metric = evaluate.load('accuracy')

    for _, (data, target) in enumerate(train_loader):
        forward_inputs = [data.reshape(len(data), 784).numpy(), target.numpy().astype(np.int64)]
        test_loss, logits = model(*forward_inputs)
        metric.add_batch(references=target, predictions=get_pred(logits))
        losses.append(test_loss)

    metrics = metric.compute()
    print(f'Epoch: {epoch+1}, Train Loss: {sum(losses)/len(losses):.4f}, Accuracy: {metrics["accuracy"]:.2f}')

for epoch in range(5):
    train(epoch)
    test(epoch)


# Run inferencing

model.export_model_for_inferencing("data/inference_model.onnx", ["output"])
session = InferenceSession('data/inference_model.onnx', providers=['CPUExecutionProvider'])

# # getting one example from test list to try inference.
# data = next(iter(test_loader))[0][0]

# input_name = session.get_inputs()[0].name
# output_name = session.get_outputs()[0].name 
# output = session.run([output_name], {input_name: data.reshape(1,784).numpy()})

# # plotting the picture
# plt.imshow(data[0], cmap='gray')
# plt.show()

# print("Predicted Label : ",get_pred(output[0]))