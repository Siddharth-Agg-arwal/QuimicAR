import cv2
import numpy as np
import os

output_dir = "sample_markers"
os.makedirs(output_dir, exist_ok=True)

# Use the same dictionary as the app
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Mapping based on Level 0 in levels.yaml
# Marker 0: Oxygen (count 1)
# Marker 1: Hydrogen (count 2)
# Marker 2: Carbon (count 4)
markers = {
    0: "Oxygen",
    1: "Hydrogen",
    2: "Carbon",
    3: "Nitrogen", 
    4: "Sulfur"
}

print(f"Generating markers in '{output_dir}'...")

for marker_id, name in markers.items():
    try:
        # Generate marker
        img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, 200)
        
        # Add border and text for better usability
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img_padded = cv2.copyMakeBorder(img_color, 50, 20, 20, 20, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        
        cv2.putText(img_padded, f"ID {marker_id}: {name}", (20, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
        
        filename = os.path.join(output_dir, f"marker_{marker_id}_{name}.png")
        cv2.imwrite(filename, img_padded)
        print(f"Saved {filename}")
    except Exception as e:
        print(f"Error generating marker {marker_id}: {e}")

# Create a composite image for Level 0 (Water: H2O)
# We need Marker 0 (Oxygen) and Marker 1 (Hydrogen - provides 2 H atoms in Level 0)
try:
    canvas = np.ones((400, 600, 3), dtype=np.uint8) * 255
    
    marker0 = cv2.aruco.generateImageMarker(aruco_dict, 0, 200)
    marker1 = cv2.aruco.generateImageMarker(aruco_dict, 1, 200)
    
    marker0_color = cv2.cvtColor(marker0, cv2.COLOR_GRAY2BGR)
    marker1_color = cv2.cvtColor(marker1, cv2.COLOR_GRAY2BGR)
    
    # Place markers
    canvas[100:300, 50:250] = marker0_color
    canvas[100:300, 350:550] = marker1_color
    
    # Add labels
    cv2.putText(canvas, "Level 0 Solution: Water (H2O)", (120, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,0), 2)
    cv2.putText(canvas, "ID 0: Oxygen", (80, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
    cv2.putText(canvas, "ID 1: Hydrogen (x2)", (360, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0), 2)
    
    filename = os.path.join(output_dir, "test_level0_water_solution.png")
    cv2.imwrite(filename, canvas)
    print(f"Saved {filename}")
except Exception as e:
    print(f"Error generating composite image: {e}")
