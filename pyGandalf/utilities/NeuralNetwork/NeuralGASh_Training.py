import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from pyGandalf.utilities.GA.CGA_Multivector_Processing import build_motor_from_vertex_normal

import numpy as np

def load_large_txt(file_path):
    """ Efficiently load large .txt files line by line """
    with open(file_path, "r") as f:
        for line in f:
            yield np.array([float(x) for x in line.split()], dtype=np.float32)

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
        """
        This forward can handle:
         - Training shape: [B, V, 6]
         - Unity Barracuda shape: [1,1,6,V]
         
        We'll unify them to [B, V, 6] before flattening.
        """
        # If Barracuda feeds us a 4D tensor [1,1,6,numVerts], permute -> [1,1,numVerts,6] -> squeeze -> [1,numVerts,6]
        if x.ndim == 4:
            x = x.permute(0, 1, 3, 2)  # => [1,1,numVerts,6]
            x = x.squeeze(1)          # => [1,numVerts,6]

        # If it’s [B,6] 2D, we make it [B,1,6]
        if x.ndim == 2:
            x = x.unsqueeze(1)

        # Now we expect [batch_size, num_vertices, num_features=6]
        batch_size, num_vertices, num_features = x.shape

        # Flatten so linear layers see [B*V, 6]
        x = x.view(batch_size * num_vertices, num_features)

        # Normal feed-forward:
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

        # Reshape back to [B, V, 27]
        x = x.view(batch_size, num_vertices, -1)
        return x


class MeshDataset(Dataset):
    def __init__(self, mesh_directory):
        self.mesh_directory = mesh_directory
        self.data_info = []
        self.loaded_data = {}

        all_files = os.listdir(mesh_directory)
        model_names = {
            file.replace("_vertices.txt", "")
            for file in all_files
            if file.endswith("_vertices.txt")
        }

        input_data_list = []

        for model_name in model_names:
            vertices_file = os.path.join(mesh_directory, f"{model_name}_vertices.txt")
            normals_file = os.path.join(mesh_directory, f"{model_name}_normals.txt")
            coeff_file_path = os.path.join(mesh_directory, f"{model_name}.obj.txt")

            print(f"Loading {coeff_file_path} ")

            vertices = np.loadtxt(vertices_file, dtype=np.float32)
            normals = np.loadtxt(normals_file, dtype=np.float32)
            vertex_coeffs = np.vstack(list(load_large_txt(coeff_file_path)))

            num_vertices = vertices.shape[0]
            assert num_vertices == normals.shape[0] == vertex_coeffs.shape[0], f"ERROR: Shape mismatch in {model_name}"

            input_features = []

            for i, (v, n) in enumerate(zip(vertices, normals)):
                if np.isnan(n).any():
                    n = np.array([0.0, 0.0, 0.0], dtype=np.float32) 
                M = build_motor_from_vertex_normal(v, n)
                # Fetch the geometric descriptors
                input_features.append(M)


            input_features = np.nan_to_num(input_features)
            vertex_coeffs = np.nan_to_num(vertex_coeffs)

            target_coeffs = vertex_coeffs.reshape(vertices.shape[0], -1)

            input_data_list.append(input_features)

            self.loaded_data[model_name] = {
                "input_features": torch.tensor(input_features, dtype=torch.float32),
                "target_coeffs": torch.tensor(target_coeffs, dtype=torch.float32),
            }

            self.data_info.append(model_name)

        all_input_data = np.vstack(input_data_list)
        train_mean = np.mean(all_input_data, axis=0)
        train_std = np.std(all_input_data, axis=0) + 1e-6
        print(f"Training Mean: {train_mean}, Std: {train_std}")

    def __len__(self):
        return len(self.data_info)

    def __getitem__(self, idx):
        model_name = self.data_info[idx]
        return (self.loaded_data[model_name]["input_features"],
                self.loaded_data[model_name]["target_coeffs"])


def custom_collate_fn(batch):
    """
    We pad each mesh in a batch to the max number of vertices among them.
    However, here you're using batch_size=1 in your main, so the padding
    is kind of redundant. But we'll keep it anyway.
    """
    inputs, targets = zip(*batch)

    max_vertices = max(inp.shape[0] for inp in inputs)

    padded_inputs = torch.zeros(len(inputs), max_vertices, inputs[0].shape[1])
    padded_targets = torch.zeros(len(targets), max_vertices, targets[0].shape[1])

    for i, (inp, tgt) in enumerate(zip(inputs, targets)):
        padded_inputs[i, :inp.shape[0], :] = inp
        padded_targets[i, :tgt.shape[0], :] = tgt

    return padded_inputs, padded_targets


def main():
    # Directories setup
    mesh_directory = '..'

    input_size = 32
    output_size = 27

    model = SHModel(input_size=input_size, output_size=output_size)
    mesh_dataset = MeshDataset(mesh_directory)

    train_indices, val_indices = train_test_split(
        range(len(mesh_dataset)), test_size=0.2, random_state=42
    )
    train_dataset = torch.utils.data.Subset(mesh_dataset, train_indices)
    val_dataset = torch.utils.data.Subset(mesh_dataset, val_indices)

    train_loader = DataLoader(
        train_dataset, batch_size=1, shuffle=True,
        collate_fn=custom_collate_fn, num_workers=0
    )
    validation_loader = DataLoader(
        val_dataset, batch_size=1, shuffle=False,
        collate_fn=custom_collate_fn, num_workers=0
    )

    criterion = nn.MSELoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.0001, weight_decay=5e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', patience=3, factor=0.3
    )

    num_epochs = 30

    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0

        for inputs, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)

            loss = criterion(outputs, targets)


            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        avg_train_loss = running_loss / len(train_loader)
        print(f"Epoch [{epoch+1}/{num_epochs}], Training Loss: {avg_train_loss:.4f}")

        model.eval()
        validation_loss = 0.0
        with torch.no_grad():
            for inputs, targets in validation_loader:
                outputs = model(inputs)
                loss = criterion(outputs, targets)
                validation_loss += loss.item()

        avg_val_loss = validation_loss / len(validation_loader)
        print(f"Validation Loss: {avg_val_loss:.4f}")

        # You can step the scheduler if desired
        scheduler.step(avg_val_loss)

    # Save final model
    torch.save(model, 'NeuralGASh_Model.pth')
    print("Model saved: NeuralGASh_Model.pth")


if __name__ == "__main__":
    main()