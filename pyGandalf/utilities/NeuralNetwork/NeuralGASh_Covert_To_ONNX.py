import torch
import torch.nn as nn

from pyGandalf.utilities.definitions import NN_PATH

class SHModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(SHModel, self).__init__()

        self.bn_input = nn.BatchNorm1d(input_size)

        self.fc1 = nn.Linear(input_size, 1024)
        self.bn1 = nn.BatchNorm1d(1024)
        self.dropout1 = nn.Dropout(0.5)

        self.fc2 = nn.Linear(1024, 512)
        self.bn2 = nn.BatchNorm1d(512)
        self.dropout2 = nn.Dropout(0.3)

        self.fc3 = nn.Linear(512, 256)
        self.bn3 = nn.BatchNorm1d(256)
        self.dropout3 = nn.Dropout(0.2)

        self.fc4 = nn.Linear(256, 128)
        self.fc5 = nn.Linear(128, output_size)

        self.activation = nn.SiLU()

    def forward(self, x):
        if x.ndim == 4:
            x = x.permute(0, 1, 3, 2)
            x = x.squeeze(1)

        if x.ndim == 2:
            x = x.unsqueeze(1)

        batch_size, num_vertices, num_features = x.shape
        x = x.view(batch_size * num_vertices, num_features)

        x = self.bn_input(x)
        x = self.fc1(x)
        x = self.activation(x)
        x = self.bn1(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.activation(x)
        x = self.bn2(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        x = self.activation(x)
        x = self.bn3(x)
        x = self.dropout3(x)

        x = self.fc4(x)
        x = self.activation(x)
        x = self.fc5(x)

        x = x.view(batch_size, num_vertices, -1)
        return x

# Load trained model
input_size = 32
output_size = 27
model_path = NN_PATH / 'NeuralGASh_Model.pth'

model = torch.load(model_path, map_location=torch.device('cpu'))
model.eval()

dummy_input = torch.randn(1, 1, input_size, 1000)

onnx_path = 'NeuralGASh_Model.onnx'
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size", 3: "num_vertices"},
        "output": {0: "batch_size", 1: "num_vertices"}
    },
    opset_version=17,
    do_constant_folding=True
)

print(f"Model exported to ONNX: {onnx_path}")
