import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torchvision import transforms
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision.datasets import ImageFolder

data_root = '../data/10000/10000'

class CustomDataset(Dataset):
    def __init__(self, root, transform=None):
        self.data = ImageFolder(root=root, transform=transform)
    
    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

transform = transforms.Compose([
    transforms.Resize((28, 28)),
    transforms.Grayscale(num_output_channels=1),
    transforms.RandomRotation(10),
    transforms.RandomHorizontalFlip(),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.ToTensor()
])

custom_dataset = CustomDataset(root=data_root, transform=transform)

test_split = 0.1
dataset_size = len(custom_dataset)
test_size = int(test_split * dataset_size)
train_size = dataset_size - test_size

train_dataset, test_dataset = random_split(custom_dataset, [train_size, test_size])

batch_size = 64
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

print("Loaded Dataset")

class DIDANet(nn.Module):
    def __init__(self):
        super(DIDANet, self).__init__()

        self.conv1 = nn.Conv2d(1, 32, 3)
        self.conv2 = nn.Conv2d(32, 64, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(64 * 5 * 5, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 64 * 5 * 5)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

net = DIDANet()

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(net.parameters(), lr=0.01, momentum=0.9)

num_epochs = 15

for epoch in range(num_epochs):
    net.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for i, data in enumerate(train_loader, 0):
        inputs, labels = data
        optimizer.zero_grad()
        outputs = net(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / len(train_loader)
    epoch_accuracy = 100 * correct / total

    print(f"Epoch {epoch + 1}/{num_epochs}:")
    print(f"  Loss: {epoch_loss:.4f}")
    print(f"  Accuracy: {epoch_accuracy:.2f}%")

print("Finished Training")

net.eval()
correct = 0
total = 0

with torch.no_grad():
    for data in test_loader:
        inputs, labels = data
        outputs = net(inputs)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f"Test Accuracy: {100 * correct / total:.2f}%")

input_names = ["input"]
output_names = ["output"]
dynamic_axes = {"input": {0: "batch_size"}, "output": {0: "batch_size"}}

model_inputs = torch.randn(1, 1, 28, 28)

torch.onnx.export(
    net,
    model_inputs,
    "dida_trained.onnx",
    input_names=input_names,
    output_names=output_names,
    opset_version=14,
    do_constant_folding=False,
    training=torch.onnx.TrainingMode.TRAINING,
    dynamic_axes=dynamic_axes,
    export_params=True,
    keep_initializers_as_inputs=False
)

print("Exported Model")