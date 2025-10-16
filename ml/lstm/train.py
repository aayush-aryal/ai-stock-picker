# train.py
import torch
import torch.nn as nn
from model import LSTMModel, BidirectionalLSTM
from pathlib import Path
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
import pickle


SCRIPT_DIR = Path(__file__).resolve().parent
TENSOR_DIR = SCRIPT_DIR.parent / "data" / "tensors"
MODEL_SAVE_PATH = SCRIPT_DIR.parent / "models" / "lstm.pt"
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True) # Ensure models directory exists


print("Loading pre-processed tensors from disk...")
X_train = torch.load(TENSOR_DIR / 'X_train.pt')
y_train = torch.load(TENSOR_DIR / 'y_train.pt')
X_test = torch.load(TENSOR_DIR / 'X_test.pt')
y_test = torch.load(TENSOR_DIR / 'y_test.pt')
with open(TENSOR_DIR / 'target_scaler.pkl', 'rb') as f:
    target_scaler = pickle.load(f)
print("Tensors and scaler loaded.")


BATCH_SIZE = 256
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")


hparams = {
    'input_size': X_train.shape[2],
    'hidden_size': 64,
    'num_layers': 2,
    'dropout_prob': 0.3
}

model = BidirectionalLSTM(
    input_size=hparams['input_size'],
    hidden_size=hparams['hidden_size'],
    num_layers=hparams['num_layers'],
    dropout_prob=hparams['dropout_prob']
).to(device)

loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = ReduceLROnPlateau(optimizer, 'min', factor=0.5, patience=3)

train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_dataset = TensorDataset(X_test, y_test)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)


epochs = 30
train_losses = []
test_losses = []
best_test_loss = float('inf')
best_epoch = -1

for epoch in range(epochs):
    model.train()
    total_train_loss = 0
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        y_pred = model(batch_X)
        loss = loss_function(y_pred, batch_y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_train_loss += loss.item()
    

    avg_train_loss = total_train_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    model.eval()
    total_test_loss = 0
    with torch.no_grad():
        for batch_X, batch_y in test_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            test_pred = model(batch_X)
            total_test_loss += loss_function(test_pred, batch_y).item()

    avg_test_loss = total_test_loss / len(test_loader)
    test_losses.append(avg_test_loss)
    
    print(f'Epoch {epoch+1}/{epochs}, Train Loss: {avg_train_loss:.6f}, Test Loss: {avg_test_loss:.6f}')
    scheduler.step(avg_test_loss)

    
    if avg_test_loss < best_test_loss:
        best_test_loss = avg_test_loss
        best_epoch = epoch + 1 
        torch.save({
            'model_state_dict': model.state_dict(),
            'hparams': hparams
        }, MODEL_SAVE_PATH)
        print(f"  -> New best model saved with test loss: {best_test_loss:.6f}")

print(f"\nTraining finished. Best model from epoch {best_epoch} saved with test loss {best_test_loss:.6f}.")


plt.figure(figsize=(10, 5))
plt.plot(train_losses, label='Training Loss')
plt.plot(test_losses, label='Test Loss')
plt.title('Training and Test Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss (MSE)')
plt.legend()
plt.grid(True)
plt.show()