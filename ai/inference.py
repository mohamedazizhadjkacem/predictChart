import torch
import numpy as np
import logging
from typing import List, Union
import os

from model import CandlestickLSTM, create_model

logger = logging.getLogger(__name__)

class ModelInference:
    """
    Handles model loading and inference for candlestick prediction
    """
    
    def __init__(self, model_path: str, device: str = None):
        self.model_path = model_path
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_config = {
            'input_size': 4,
            'hidden_size': 128,
            'num_layers': 2,
            'output_size': 4,
            'sequence_length': 50,
            'prediction_length': 25
        }
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                logger.warning(f"Model file not found: {self.model_path}")
                self._create_dummy_model()
                return
            
            # Load model state
            checkpoint = torch.load(self.model_path, map_location=self.device)
            
            # Extract config if saved with checkpoint
            if isinstance(checkpoint, dict) and 'config' in checkpoint:
                self.model_config.update(checkpoint['config'])
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
            
            # Create model
            self.model = CandlestickLSTM(**self.model_config)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully from {self.model_path}")
            logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._create_dummy_model()
    
    def _create_dummy_model(self):
        """Create a dummy model for testing when real model is not available"""
        logger.info("Creating dummy model for demonstration")
        self.model = CandlestickLSTM(**self.model_config)
        self.model.to(self.device)
        self.model.eval()
        
        # Save dummy model
        torch.save(self.model.state_dict(), self.model_path)
        logger.info(f"Dummy model saved to {self.model_path}")
    
    def predict(self, sequence: List[List[float]], prediction_length: int = None) -> List[List[float]]:
        """
        Generate prediction from input sequence
        
        Args:
            sequence: List of [open, high, low, close] values
            prediction_length: Number of future candles to predict
            
        Returns:
            Predicted future candlestick sequence
        """
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        if prediction_length is None:
            prediction_length = self.model_config['prediction_length']
        
        try:
            # Validate input
            if not sequence or len(sequence) == 0:
                raise ValueError("Empty sequence provided")
            
            if len(sequence[0]) != 4:
                raise ValueError("Each candlestick must have 4 values (OHLC)")
            
            # Convert to tensor
            input_tensor = torch.FloatTensor(sequence).to(self.device)
            
            # Ensure we have enough input data
            required_length = self.model_config['sequence_length']
            if len(sequence) < required_length:
                # Pad sequence if too short
                padding_length = required_length - len(sequence)
                padding = sequence[:1] * padding_length  # Repeat first candle
                sequence = padding + sequence
                input_tensor = torch.FloatTensor(sequence).to(self.device)
            elif len(sequence) > required_length:
                # Truncate if too long (use most recent data)
                sequence = sequence[-required_length:]
                input_tensor = torch.FloatTensor(sequence).to(self.device)
            
            # Generate prediction
            with torch.no_grad():
                prediction = self.model.predict_single(input_tensor, prediction_length)
                prediction_np = prediction.cpu().numpy()
            
            # Convert back to list format
            prediction_list = prediction_np.tolist()
            
            # Validate output
            prediction_list = self._validate_prediction(prediction_list)
            
            logger.info(f"Generated prediction: {len(prediction_list)} candles")
            
            return prediction_list
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            # Return fallback prediction
            return self._generate_fallback_prediction(sequence, prediction_length)
    
    def _validate_prediction(self, prediction: List[List[float]]) -> List[List[float]]:
        """
        Validate and fix prediction output
        
        Args:
            prediction: Raw prediction from model
            
        Returns:
            Validated and corrected prediction
        """
        validated = []
        
        for candle in prediction:
            if len(candle) != 4:
                continue
            
            o, h, l, c = candle
            
            # Ensure values are in valid range [0, 1]
            o = max(0.0, min(1.0, float(o)))
            h = max(0.0, min(1.0, float(h)))
            l = max(0.0, min(1.0, float(l)))
            c = max(0.0, min(1.0, float(c)))
            
            # Ensure high >= max(open, close) and low <= min(open, close)
            h = max(h, o, c)
            l = min(l, o, c)
            
            validated.append([o, h, l, c])
        
        return validated
    
    def _generate_fallback_prediction(self, sequence: List[List[float]], prediction_length: int) -> List[List[float]]:
        """
        Generate a simple fallback prediction when model fails
        
        Args:
            sequence: Input sequence
            prediction_length: Number of predictions to generate
            
        Returns:
            Fallback prediction based on recent trends
        """
        logger.warning("Using fallback prediction method")
        
        if not sequence:
            # Return default candles if no input
            return [[0.5, 0.6, 0.4, 0.5]] * prediction_length
        
        # Use last few candles to estimate trend
        recent_candles = sequence[-min(5, len(sequence)):]
        
        # Calculate price change trend
        if len(recent_candles) >= 2:
            changes = []
            for i in range(1, len(recent_candles)):
                prev_close = recent_candles[i-1][3]
                curr_close = recent_candles[i][3]
                if prev_close > 0:
                    change = (curr_close - prev_close) / prev_close
                    changes.append(change)
            
            avg_change = np.mean(changes) if changes else 0
            volatility = np.std(changes) if changes else 0.02
        else:
            avg_change = 0
            volatility = 0.02
        
        # Generate predictions
        prediction = []
        last_close = sequence[-1][3]
        
        for _ in range(prediction_length):
            # Add trend and random noise
            noise = np.random.normal(0, volatility)
            price_change = avg_change + noise
            
            new_close = last_close * (1 + price_change)
            new_open = last_close * (1 + np.random.normal(0, 0.005))
            
            # Generate high and low
            price_range = abs(new_close - new_open) * (1 + volatility)
            new_high = max(new_open, new_close) + abs(np.random.normal(0, price_range))
            new_low = min(new_open, new_close) - abs(np.random.normal(0, price_range))
            
            # Normalize to 0-1 range
            candle = [
                max(0, min(1, new_open)),
                max(0, min(1, new_high)),
                max(0, min(1, new_low)),
                max(0, min(1, new_close))
            ]
            
            # Validate OHLC relationships
            candle[1] = max(candle[1], candle[0], candle[3])  # High
            candle[2] = min(candle[2], candle[0], candle[3])  # Low
            
            prediction.append(candle)
            last_close = new_close
        
        return prediction
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        if self.model is None:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded",
            "device": str(self.device),
            "config": self.model_config,
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }

def preprocess_sequence(sequence: List[List[float]], target_length: int = 50) -> List[List[float]]:
    """
    Preprocess input sequence to required length
    
    Args:
        sequence: Input OHLC sequence
        target_length: Required sequence length
        
    Returns:
        Processed sequence of target length
    """
    if len(sequence) == target_length:
        return sequence
    elif len(sequence) > target_length:
        # Use most recent data
        return sequence[-target_length:]
    else:
        # Pad with repeated first values
        padding_length = target_length - len(sequence)
        if sequence:
            padding = [sequence[0]] * padding_length
            return padding + sequence
        else:
            # Default padding
            return [[0.5, 0.6, 0.4, 0.5]] * target_length