from torchvision import datasets, transforms
from onnxruntime.training import artifacts
import numpy as np
import torch
import onnx
import io

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
    
device = "cpu"
batch_size, input_size, hidden_size, output_size = 64, 784, 500, 10
model_inputs = (torch.randn(batch_size, input_size, device=device),)
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

net = MNISTNet(input_size, hidden_size, output_size).to(device)

criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(net.parameters(), lr=0.01)

num_epochs = 5

for epoch in range(num_epochs):
    running_loss = 0.0
    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        inputs = inputs.view(len(inputs), 784)
        labels = torch.tensor(labels, dtype=torch.int64)

        optimizer.zero_grad()

        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

print("Finished Training")

input_names = ["input"]
output_names = ["output"]
dynamic_axes = {"input": {0: "batch_size"}, "output": {0: "batch_size"}}

torch.onnx.export(
    net,
    model_inputs,
    "mnist_trained.onnx",
    input_names=input_names,
    output_names=output_names,
    opset_version=14,
    dynamic_axes=dynamic_axes,
    export_params=True,
)

print("Exported Model")