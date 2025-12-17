import cv2
import numpy as np
from typing import List

def image_to_numeric(img) -> List[List[float]]:
    """
    Convert a candlestick chart image into OHLC numeric data using HSV color detection
    This matches the exact extraction logic from the Colab training
    
    Args:
        img: OpenCV image array (BGR format)
        
    Returns:
        List of [open, high, low, close] values normalized to 0-1 range
    """
    if img is None:
        return []
    
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w, _ = img.shape
    
    # Thresholds for green/red candles (matching training code)
    green_mask = cv2.inRange(hsv, (40, 50, 50), (90, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)
    
    # Combine masks to find all candlestick pixels
    mask = cv2.bitwise_or(green_mask, red_mask)
    
    # Find columns that contain candle pixels
    cols_with_candle = np.where(np.any(mask > 0, axis=0))[0]
    
    if len(cols_with_candle) == 0:
        print(f"No candlestick pixels detected in image of shape {img.shape}")
        return []
    
    candles = []
    start = cols_with_candle[0]
    
    # Process each group of consecutive columns as a single candle
    for i in range(1, len(cols_with_candle)):
        if cols_with_candle[i] > cols_with_candle[i-1] + 1:  # Gap found, end current candle
            end = cols_with_candle[i-1]
            candle_slice = mask[:, start:end+1]
            
            # Find rows with candle pixels in this slice
            rows = np.where(np.any(candle_slice > 0, axis=1))[0]
            if len(rows) == 0:
                start = cols_with_candle[i]
                continue
            
            # Calculate OHLC values (normalized by height)
            # Note: In image coordinates, Y=0 is TOP, Y=max is BOTTOM
            # So min_row = top of candle = HIGH price, max_row = bottom of candle = LOW price
            low_y = rows.max()   # Bottom of candle (highest row index) = LOW price
            high_y = rows.min()  # Top of candle (lowest row index) = HIGH price
            
            # Convert to 0-1 range, flipping coordinate system
            high = 1.0 - (high_y / h)  # Top of candle = high price
            low = 1.0 - (low_y / h)    # Bottom of candle = low price
            
            # Split candle slice in half to get open/close
            mid = (end - start) // 2
            left_half = candle_slice[:, :mid] if mid > 0 else candle_slice
            right_half = candle_slice[:, mid:] if mid < candle_slice.shape[1] else candle_slice
            
            # Open: average row position in left half
            if np.any(left_half > 0):
                open_y = np.mean(np.where(np.any(left_half > 0, axis=1))[0])
                open_val = 1.0 - (open_y / h)  # Convert to price space
            else:
                open_val = high
            
            # Close: average row position in right half  
            if np.any(right_half > 0):
                close_y = np.mean(np.where(np.any(right_half > 0, axis=1))[0])
                close_val = 1.0 - (close_y / h)  # Convert to price space
            else:
                close_val = high
            
            candles.append([float(open_val), float(high), float(low), float(close_val)])
            start = cols_with_candle[i]
    
    # Handle the last candle
    if len(cols_with_candle) > 0:
        end = cols_with_candle[-1]
        candle_slice = mask[:, start:end+1]
        
        rows = np.where(np.any(candle_slice > 0, axis=1))[0]
        if len(rows) > 0:
            low_y = rows.max()
            high_y = rows.min()
            
            # Convert to price space (flip Y coordinates)
            high = 1.0 - (high_y / h)
            low = 1.0 - (low_y / h)
            
            mid = (end - start) // 2
            left_half = candle_slice[:, :mid] if mid > 0 else candle_slice
            right_half = candle_slice[:, mid:] if mid < candle_slice.shape[1] else candle_slice
            
            if np.any(left_half > 0):
                open_y = np.mean(np.where(np.any(left_half > 0, axis=1))[0])
                open_val = 1.0 - (open_y / h)
            else:
                open_val = high
                
            if np.any(right_half > 0):
                close_y = np.mean(np.where(np.any(right_half > 0, axis=1))[0])
                close_val = 1.0 - (close_y / h)
            else:
                close_val = high
            
            candles.append([float(open_val), float(high), float(low), float(close_val)])
    
    print(f"Extracted {len(candles)} candles from image of shape {img.shape}")
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