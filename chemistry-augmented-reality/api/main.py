from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import io
import sys
import os
import yaml

# Add parent directory to path to import chemistry_ar modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

app = FastAPI(
    title="Chemistry AR API",
    description="Augmented Reality Chemistry Game API",
    version="1.0.0"
)

# Add CORS middleware to allow requests from web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files directory - handle both local and Heroku paths
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Load levels data from YAML
levels_file = os.path.join(os.path.dirname(__file__), "..", "chemistry_ar", "data", "levels.yaml")
levels_data = []
current_level = 0

if os.path.exists(levels_file):
    with open(levels_file, 'r') as f:
        data = yaml.safe_load(f)
        if data and 'levels' in data:
            levels_data = data['levels']

WIDTH, HEIGHT = 1280, 720


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse(content="<h1>Chemistry AR API</h1><p>Visit <a href='/docs'>/docs</a> for API documentation.</p>")


@app.get("/health")
async def health_check():
    """API health check endpoint"""
    return {
        "status": "ok",
        "message": "Chemistry AR API is running",
        "version": "1.0.0"
    }


@app.get("/levels")
async def get_levels():
    """Get information about available levels"""
    global current_level
    objective = "Unknown"
    if levels_data and current_level < len(levels_data):
        objective = levels_data[current_level].get("objective", {}).get("name", "Unknown")
    
    return {
        "total_levels": len(levels_data),
        "current_level": current_level,
        "current_objective": objective
    }


@app.post("/process_frame")
async def process_frame(file: UploadFile = File(...)):
    """
    Process an image frame and detect ArUco markers.
    
    Args:
        file: Image file (JPEG, PNG, etc.)
        
    Returns:
        Processed image with detected ArUco markers highlighted
    """
    try:
        # Read uploaded file
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Resize frame to expected dimensions
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        
        # Detect ArUco markers
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        aruco_params = cv2.aruco.DetectorParameters()
        corners, ids, rejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=aruco_params)
        
        # Draw detected markers
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # Get current level markers info
            current_level_data = levels_data[current_level] if levels_data and current_level < len(levels_data) else None
            level_markers = current_level_data.get("markers", []) if current_level_data else []
            
            detected_required_count = 0
            total_required_count = sum(1 for m in level_markers if m.get("required", False))
            
            # Add text labels for detected markers
            for i, corner in enumerate(corners):
                marker_id = ids[i][0]
                center = corner[0].mean(axis=0).astype(int)
                
                # Determine label based on level data
                label = f"ID: {marker_id}"
                color = (0, 255, 0) # Green
                
                if marker_id < len(level_markers):
                    marker_info = level_markers[marker_id]
                    atoms = marker_info.get("atoms", [])
                    atom_names = [f"{a['count']}{a['element']}" for a in atoms]
                    label = "+".join(atom_names)
                    
                    if marker_info.get("required", False):
                        detected_required_count += 1
                        color = (0, 255, 255) # Yellow for required
                    else:
                        color = (200, 200, 200) # Gray for optional
                
                cv2.putText(frame, label, (center[0], center[1] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
            
            # Check if objective is met (simple check: are all required markers visible?)
            # This is a simplification. Real engine checks distance/reaction.
            if detected_required_count >= total_required_count and total_required_count > 0:
                cv2.putText(frame, "OBJECTIVE MET!", (50, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 0), 5)
                
        # Encode as JPEG
        success, encoded_img = cv2.imencode('.jpg', frame)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to encode image")
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(encoded_img.tobytes()),
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing frame: {str(e)}")


@app.post("/set_level/{level_number}")
async def set_level(level_number: int):
    """Set the current game level"""
    global current_level
    try:
        if level_number < 0 or level_number >= len(levels_data):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid level number. Must be between 0 and {len(levels_data) - 1}"
            )
        
        current_level = level_number
        objective = levels_data[level_number].get("objective", {}).get("name", "Unknown")
        
        return {
            "status": "success",
            "current_level": level_number,
            "objective": objective
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting level: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
