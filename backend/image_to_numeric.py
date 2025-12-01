import cv2
import numpy as np
from typing import List

def image_to_numeric(img) -> List[List[float]]:
    """
    Convert a candlestick chart image (1025×817) into 50 OHLC numeric rows
    
    Args:
        img: OpenCV image array (BGR format)
        
    Returns:
        List of [open, high, low, close] values normalized to 0-1 range
    """
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    
    candles = []
    num_candles = 50
    candle_width = w // num_candles
    
    for i in range(num_candles):
        # Calculate column boundaries
        x1 = i * candle_width
        x2 = x1 + candle_width
        
        # Crop the column for this candle
        crop = gray[:, x1:x2]
        
        # Extract OHLC values from different sections of the candle
        # Open: top quarter average
        o = np.mean(crop[:h//4])
        
        # High: maximum value in the column
        h_ = np.max(crop)
        
        # Low: minimum value in the column
        l = np.min(crop)
        
        # Close: bottom quarter average
        c = np.mean(crop[3*h//4:])
        
        # Normalize to 0-1 range (assuming 0-255 grayscale)
        normalized_candle = [o/255, h_/255, l/255, c/255]
        candles.append(normalized_candle)
    
    return candles

def validate_numeric_data(data: List[List[float]]) -> bool:
    """
    Validate that numeric data is in correct OHLC format
    
    Args:
        data: List of [open, high, low, close] values
        
    Returns:
        True if valid, False otherwise
    """
    if not data or len(data) == 0:
        return False
    
    for candle in data:
        if len(candle) != 4:  # Must have OHLC
            return False
        
        o, h, l, c = candle
        
        # Basic validation: high should be >= low
        if h < l:
            return False
        
        # Values should be in reasonable range (0-1 for normalized data)
        if not all(0 <= val <= 1 for val in candle):
            return False
    
    return True