from PIL import Image, ImageDraw
from typing import List

def numeric_to_image(numeric: List[List[float]], width: int = 342, height: int = 817) -> Image.Image:
    """
    Reconstruct a candlestick chart image from numeric OHLC data
    
    Args:
        numeric: List of [open, high, low, close] values (0-1 normalized)
        width: Target image width (default: 342)
        height: Target image height (default: 817)
        
    Returns:
        PIL Image object of the reconstructed candlestick chart
    """
    # Create white background image
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    
    num_candles = len(numeric)
    candle_width = width // num_candles
    
    for i, (o, h_, l, c) in enumerate(numeric):
        # Calculate x coordinates for this candle
        x_left = i * candle_width
        x_right = x_left + candle_width - 2  # Leave small gap between candles
        x_center = (x_left + x_right) // 2
        
        # Convert normalized values to y coordinates (flip because image coordinates start from top)
        o_y = height - int(o * height)
        h_y = height - int(h_ * height)
        l_y = height - int(l * height)
        c_y = height - int(c * height)
        
        # Determine candle color (green if close > open, red otherwise)
        color = "green" if c > o else "red"
        body_color = color
        
        # Draw high-low line (wick)
        draw.line([x_center, h_y, x_center, l_y], fill="black", width=1)
        
        # Draw candle body
        body_top = min(o_y, c_y)
        body_bottom = max(o_y, c_y)
        
        # If open == close, draw a thin line
        if abs(body_top - body_bottom) < 2:
            draw.line([x_left, body_top, x_right, body_top], fill="black", width=2)
        else:
            # Draw filled rectangle for candle body
            draw.rectangle([x_left, body_top, x_right, body_bottom], 
                         fill=body_color, outline="black", width=1)
        
        # Draw open and close ticks
        tick_size = candle_width // 4
        
        # Open tick (left side)
        draw.line([x_left - tick_size, o_y, x_center, o_y], fill="black", width=1)
        
        # Close tick (right side)  
        draw.line([x_center, c_y, x_right + tick_size, c_y], fill="black", width=1)
    
    return img

def create_candlestick_chart_advanced(numeric: List[List[float]], width: int = 342, height: int = 817) -> Image.Image:
    """
    Advanced candlestick chart generation with better styling
    
    Args:
        numeric: List of [open, high, low, close] values (0-1 normalized)
        width: Target image width
        height: Target image height
        
    Returns:
        PIL Image with styled candlestick chart
    """
    # Create image with light background
    img = Image.new("RGB", (width, height), "#f8f9fa")
    draw = ImageDraw.Draw(img)
    
    # Add margins
    margin_top = 20
    margin_bottom = 20
    margin_left = 10
    margin_right = 10
    
    chart_width = width - margin_left - margin_right
    chart_height = height - margin_top - margin_bottom
    
    num_candles = len(numeric)
    candle_width = chart_width // num_candles
    
    # Find min and max values for better scaling
    all_values = [val for candle in numeric for val in candle]
    min_val = min(all_values)
    max_val = max(all_values)
    value_range = max_val - min_val if max_val > min_val else 1
    
    for i, (o, h_, l, c) in enumerate(numeric):
        # Calculate x coordinates
        x_left = margin_left + i * candle_width
        x_right = x_left + candle_width - 1
        x_center = (x_left + x_right) // 2
        
        # Scale and position y coordinates
        o_y = margin_top + chart_height - int(((o - min_val) / value_range) * chart_height)
        h_y = margin_top + chart_height - int(((h_ - min_val) / value_range) * chart_height)
        l_y = margin_top + chart_height - int(((l - min_val) / value_range) * chart_height)
        c_y = margin_top + chart_height - int(((c - min_val) / value_range) * chart_height)
        
        # Determine colors
        is_bullish = c >= o
        body_color = "#26a69a" if is_bullish else "#ef5350"  # Teal/Red
        wick_color = "#37474f"  # Dark grey
        
        # Draw wick (high-low line)
        draw.line([x_center, h_y, x_center, l_y], fill=wick_color, width=1)
        
        # Draw candle body
        body_top = min(o_y, c_y)
        body_bottom = max(o_y, c_y)
        
        if abs(body_top - body_bottom) < 2:
            # Doji candle (open == close)
            draw.line([x_left, body_top, x_right, body_top], fill=wick_color, width=2)
        else:
            # Regular candle body
            if is_bullish:
                # Hollow/outline for bullish
                draw.rectangle([x_left, body_top, x_right, body_bottom], 
                             outline=body_color, width=2)
            else:
                # Filled for bearish
                draw.rectangle([x_left, body_top, x_right, body_bottom], 
                             fill=body_color, outline=body_color)
    
    return img