import torch
import torch.nn as nn


class CandlestickPredictor(nn.Module):
    """
    Exact model architecture from Colab notebook
    Encoder-Decoder LSTM for sequence-to-sequence candlestick prediction
    """
    def __init__(self, input_size=4, output_size=4, hidden_size=128, num_layers=2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        # Encoder LSTM
        self.encoder_lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)

        # Decoder LSTM - takes previous prediction (output_size) as input
        self.decoder_lstm = nn.LSTM(output_size, hidden_size, num_layers, batch_first=True)
        # Linear layer to map decoder's hidden state to output_size features
        self.decoder_linear = nn.Linear(hidden_size, output_size)

    def forward(self, x, past_lengths, future_lengths):
        batch_size = x.size(0)

        # Encoder
        # Pack padded sequence
        packed_input = nn.utils.rnn.pack_padded_sequence(x, past_lengths.cpu(), batch_first=True, enforce_sorted=False)

        # Pass through encoder LSTM. We only need the final hidden and cell states.
        _, (hidden_state, cell_state) = self.encoder_lstm(packed_input)

        # Decoder
        # Determine the maximum future_len in the current batch
        max_future_len_in_batch = torch.max(future_lengths).item()

        # Create an initial 'start token' input for the decoder (e.g., a tensor of zeros)
        # This should have shape (batch_size, 1, self.output_size)
        decoder_input = torch.zeros(batch_size, 1, self.output_size, device=x.device)

        decoder_outputs = []

        # Autoregressive decoding loop
        for _ in range(max_future_len_in_batch):
            # Pass through decoder LSTM
            output, (hidden_state, cell_state) = self.decoder_lstm(decoder_input, (hidden_state, cell_state))

            # Apply linear layer to get prediction for current timestep
            prediction = self.decoder_linear(output)

            # Store the prediction
            decoder_outputs.append(prediction)

            # Use the prediction as the input for the next timestep (detach to prevent backprop through past unrolling)
            decoder_input = prediction.detach()

        # Concatenate the predictions along the sequence dimension
        predictions = torch.cat(decoder_outputs, dim=1)

        return predictions
