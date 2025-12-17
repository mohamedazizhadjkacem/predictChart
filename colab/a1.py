# extract_all_samples.py
import os
import cv2
import numpy as np
import pickle

DATASET_DIR = "dataset"  # folder with sample_X/input.png and label.png
OUTPUT_DIR = "numeric_dataset"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_candles(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return []

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, w, _ = img.shape

    # Thresholds for green/red candles
    green_mask = cv2.inRange(hsv, (40, 50, 50), (90, 255, 255))
    red_mask1 = cv2.inRange(hsv, (0, 50, 50), (10, 255, 255))
    red_mask2 = cv2.inRange(hsv, (170, 50, 50), (180, 255, 255))
    red_mask = cv2.bitwise_or(red_mask1, red_mask2)

    mask = cv2.bitwise_or(green_mask, red_mask)
    cols_with_candle = np.where(np.any(mask > 0, axis=0))[0]

    if len(cols_with_candle) == 0:
        return []

    candles = []
    start = cols_with_candle[0]
    for i in range(1, len(cols_with_candle)):
        if cols_with_candle[i] > cols_with_candle[i-1] + 1:
            end = cols_with_candle[i-1]
            candle_slice = mask[:, start:end+1]

            rows = np.where(np.any(candle_slice > 0, axis=1))[0]
            if len(rows) == 0:
                start = cols_with_candle[i]
                continue

            low = rows.max() / h
            high = rows.min() / h
            mid = (end-start)//2
            left = candle_slice[:, :mid]
            right = candle_slice[:, mid:]
            o = np.mean(np.where(np.any(left>0, axis=1))[0])/h if np.any(left>0) else high
            c = np.mean(np.where(np.any(right>0, axis=1))[0])/h if np.any(right>0) else high

            candles.append([o, high, low, c])
            start = cols_with_candle[i]

    return candles

# --- Process all samples ---
all_data = []

for sample_folder in sorted(os.listdir(DATASET_DIR)):
    folder_path = os.path.join(DATASET_DIR, sample_folder)
    if not os.path.isdir(folder_path):
        continue

    input_path = os.path.join(folder_path, "input.png")
    label_path = os.path.join(folder_path, "label.png")

    past_candles = extract_candles(input_path)
    future_candles = extract_candles(label_path)

    if len(past_candles) == 0 or len(future_candles) == 0:
        continue

    sample_data = {
        "past": past_candles,
        "future": future_candles,
        "input_size": (input_path and cv2.imread(input_path).shape[1], cv2.imread(input_path).shape[0]),
        "output_size": (label_path and cv2.imread(label_path).shape[1], cv2.imread(label_path).shape[0])
    }
    all_data.append(sample_data)

# --- Save dataset ---
output_file = os.path.join(OUTPUT_DIR, "all_samples_numeric.pkl")
with open(output_file, "wb") as f:
    pickle.dump(all_data, f)

print(f"Extracted {len(all_data)} samples into {output_file}")
