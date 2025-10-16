import torch.nn as nn

class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size=100, num_layers=2, output_size=1, dropout_prob=0.2):
        super(LSTMModel, self).__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_prob if num_layers > 1 else 0
        )
        self.dropout = nn.Dropout(dropout_prob)
        self.linear = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        out_dropout = self.dropout(lstm_out[:, -1, :])
        prediction = self.linear(out_dropout)
        return prediction


class BidirectionalLSTM(nn.Module):
    def __init__(self, input_size, hidden_size=64, num_layers=2, output_size=1, dropout_prob=0.3):
        super(BidirectionalLSTM, self).__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_prob if num_layers > 1 else 0,
            bidirectional=True)
        
        self.dropout = nn.Dropout(dropout_prob)
        self.linear = nn.Linear(hidden_size * 2, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_time_step_out = lstm_out[:, -1, :]
        out_dropout = self.dropout(last_time_step_out)
        prediction = self.linear(out_dropout)
        return prediction