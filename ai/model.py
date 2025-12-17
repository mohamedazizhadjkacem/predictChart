import torch
import torch.nn as nn
import numpy as np

class CandlestickLSTM(nn.Module):
    
    """
    LSTM Sequence-to-Sequence model for candlestick prediction
    
    Architecture:
    - LSTM encoder to process input sequence
    - LSTM decoder to generate output sequence
    - Fully connected layers for final prediction
    """
    
    def __init__(self, input_size=4, hidden_size=128, num_layers=2, output_size=4, sequence_length=50, prediction_length=25):
        super(CandlestickLSTM, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length
        
        # Encoder LSTM
        self.encoder_lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Decoder LSTM
        self.decoder_lstm = nn.LSTM(
            input_size=output_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0
        )
        
        # Output layer
        self.output_projection = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, output_size),
            nn.Sigmoid()  # Ensure output is in 0-1 range
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize model weights using Xavier initialization"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                if len(param.shape) >= 2:
                    nn.init.xavier_uniform_(param)
                else:
                    nn.init.uniform_(param, -0.1, 0.1)
            elif 'bias' in name:
                nn.init.zeros_(param)
    
    def forward(self, x, target_length=None):
        """
        Forward pass through the model
        
        Args:
            x: Input sequence [batch_size, sequence_length, input_size]
            target_length: Length of prediction sequence (defaults to self.prediction_length)
        
        Returns:
            predictions: [batch_size, target_length, output_size]
        """
        batch_size = x.size(0)
        if target_length is None:
            target_length = self.prediction_length
        
        # Encode input sequence
        encoder_outputs, (hidden, cell) = self.encoder_lstm(x)
        
        # Initialize decoder
        predictions = []
        
        # Use last input as initial decoder input
        decoder_input = x[:, -1, :].unsqueeze(1)  # [batch_size, 1, input_size]
        
        # Generate predictions step by step
        for _ in range(target_length):
            # Decoder step
            decoder_output, (hidden, cell) = self.decoder_lstm(decoder_input, (hidden, cell))
            
            # Project to output size
            prediction = self.output_projection(decoder_output)  # [batch_size, 1, output_size]
            predictions.append(prediction)
            
            # Use prediction as next input
            decoder_input = prediction
        
        # Concatenate all predictions
        predictions = torch.cat(predictions, dim=1)  # [batch_size, target_length, output_size]
        
        return predictions
    
    def predict_single(self, x, target_length=None):
        """
        Predict for a single sequence (inference mode)
        
        Args:
            x: Input sequence [sequence_length, input_size]
            target_length: Length of prediction
            
        Returns:
            predictions: [target_length, output_size]
        """
        self.eval()
        with torch.no_grad():
            # Add batch dimension
            x = x.unsqueeze(0)  # [1, sequence_length, input_size]
            
            # Get prediction
            pred = self.forward(x, target_length)
            
            # Remove batch dimension
            pred = pred.squeeze(0)  # [target_length, output_size]
            
            return pred

class CandlestickTransformer(nn.Module):
    """
    Alternative Transformer model for candlestick prediction
    """
    
    def __init__(self, input_size=4, d_model=128, nhead=8, num_layers=6, output_size=4, sequence_length=50, prediction_length=25):
        super(CandlestickTransformer, self).__init__()
        
        self.input_size = input_size
        self.d_model = d_model
        self.output_size = output_size
        self.sequence_length = sequence_length
        self.prediction_length = prediction_length
        
        # Input projection
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, sequence_length + prediction_length)
        
        # Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=0.1,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output projection
        self.output_projection = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(d_model // 2, output_size),
            nn.Sigmoid()
        )
    
    def forward(self, x, target_length=None):
        if target_length is None:
            target_length = self.prediction_length
        
        batch_size, seq_len, _ = x.shape
        
        # Project input to model dimension
        x = self.input_projection(x)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Create prediction tokens
        pred_tokens = torch.zeros(batch_size, target_length, self.d_model, device=x.device)
        
        # Concatenate input and prediction tokens
        full_sequence = torch.cat([x, pred_tokens], dim=1)
        
        # Create attention mask to prevent looking at future predictions
        mask = self._generate_square_subsequent_mask(seq_len + target_length, x.device)
        
        # Apply transformer
        output = self.transformer(full_sequence, mask=mask)
        
        # Extract prediction part and project to output size
        predictions = output[:, seq_len:, :]
        predictions = self.output_projection(predictions)
        
        return predictions
    
    def _generate_square_subsequent_mask(self, sz, device):
        """Generate mask for transformer"""
        mask = torch.triu(torch.ones(sz, sz, device=device) * float('-inf'), diagonal=1)
        return mask

class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        return x + self.pe[:x.size(1), :].transpose(0, 1)

def create_model(model_type="lstm", **kwargs):
    """
    Factory function to create models
    
    Args:
        model_type: "lstm" or "transformer"
        **kwargs: Model parameters
        
    Returns:
        Initialized model
    """
    if model_type.lower() == "lstm":
        return CandlestickLSTM(**kwargs)
    elif model_type.lower() == "transformer":
        return CandlestickTransformer(**kwargs)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

def count_parameters(model):
    """Count total trainable parameters"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
