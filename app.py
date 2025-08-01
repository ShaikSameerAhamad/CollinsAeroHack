from flask import Flask, render_template, request, jsonify, Response
import cv2
import numpy as np
from cube_model import RubiksCube
from cube_solver import RubiksCubeSolver
from vision_detector import CubeVisionDetector
import json
import base64
import time

app = Flask(__name__)

# Global variables for camera and vision detector
camera = None
vision_detector = CubeVisionDetector()
current_cube_state = None

def find_working_camera():
    """Find a working camera by trying different camera indices"""
    for i in range(4):  # Try camera indices 0-3
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            if cap.isOpened():
                # Test if we can actually read a frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    cap.release()
                    return i
                cap.release()
        except Exception:
            continue
    
    # Fallback to default camera
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            cap.release()
            return 0
    except Exception:
        pass
    
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual_input')
def manual_input():
    return render_template('manual_input.html')

@app.route('/vision_input')
def vision_input():
    return render_template('vision_input.html')

@app.route('/solve_manual', methods=['POST'])
def solve_manual():
    try:
        # Get cube state from form
        cube_data = request.json
        
        # Create cube from input
        cube = RubiksCube()
        
        # Parse the 54 stickers (9 per face, 6 faces)
        # Kociemba expects faces in order: up, right, front, down, left, back
        faces = ['up', 'right', 'front', 'down', 'left', 'back']
        for face_name in faces:
            face_colors = cube_data[face_name]
            cube.set_face(face_name, face_colors)
        
        # Validate cube
        if not cube.is_valid():
            return jsonify({'error': 'Invalid cube configuration'}), 400
        
        # Solve cube
        solver = RubiksCubeSolver(cube)
        solution = solver.solve()
        
        return jsonify({
            'success': True,
            'solution': solution,
            'move_count': len(solution)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_camera')
def start_camera():
    global camera
    try:
        # Find a working camera
        camera_index = find_working_camera()
        if camera_index is None:
            return jsonify({'error': 'No working camera found. Please check your camera connection and permissions.'}), 500
        
        # Initialize camera with better settings for Windows
        camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        # Set camera properties for better performance
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 30)
        camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        
        if not camera.isOpened():
            return jsonify({'error': 'Cannot access camera. Please check camera permissions.'}), 500
        
        # Test camera by reading a frame
        ret, frame = camera.read()
        if not ret or frame is None:
            camera.release()
            camera = None
            return jsonify({'error': 'Camera opened but cannot capture frames. Please check camera settings.'}), 500
        
        return jsonify({'success': True, 'message': f'Camera {camera_index} initialized successfully'})
        
    except Exception as e:
        if camera is not None:
            camera.release()
            camera = None
        return jsonify({'error': f'Camera initialization failed: {str(e)}'}), 500

@app.route('/capture_face', methods=['POST'])
def capture_face():
    global camera, vision_detector, current_cube_state
    
    try:
        face_name = request.json.get('face')
        
        if camera is None or not camera.isOpened():
            return jsonify({'error': 'Camera not initialized. Please start the camera first.'}), 500
        
        # Try to capture frame with retry logic
        frame = None
        for attempt in range(3):  # Try up to 3 times
            ret, frame = camera.read()
            if ret and frame is not None:
                break
            time.sleep(0.1)  # Small delay between attempts
        
        if frame is None:
            return jsonify({'error': 'Failed to capture frame. Please check camera connection and try again.'}), 500
        
        # Detect colors on the face
        face_colors = vision_detector.detect_face_colors(frame)
        
        if face_colors is None:
            return jsonify({'error': 'Could not detect cube face. Please ensure the cube face is clearly visible and well-lit.'}), 500
        
        # Initialize cube state if first face
        if current_cube_state is None:
            current_cube_state = {}
        
        current_cube_state[face_name] = face_colors
        
        # Encode frame as base64 for display
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'colors': face_colors,
            'frame': frame_base64
        })
        
    except Exception as e:
        return jsonify({'error': f'Capture failed: {str(e)}'}), 500

@app.route('/solve_vision', methods=['POST'])
def solve_vision():
    global current_cube_state
    
    try:
        if current_cube_state is None or len(current_cube_state) != 6:
            return jsonify({'error': 'Not all faces captured. Please capture all 6 faces before solving.'}), 400
        
        # Create cube from vision data
        cube = RubiksCube()
        
        # Ensure faces are set in kociemba order
        faces = ['up', 'right', 'front', 'down', 'left', 'back']
        for face_name in faces:
            colors = current_cube_state[face_name]
            cube.set_face(face_name, colors)
        
        # Validate cube
        if not cube.is_valid():
            return jsonify({'error': 'Invalid cube configuration detected. Please re-scan the faces.'}), 400
        
        # Solve cube (uses kociemba library internally)
        solver = RubiksCubeSolver(cube)
        solution = solver.solve()
        
        # Reset state
        current_cube_state = None
        
        return jsonify({
            'success': True,
            'solution': solution,
            'move_count': len(solution)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test_camera')
def test_camera():
    """Test endpoint to check camera status"""
    global camera
    
    try:
        if camera is None:
            return jsonify({
                'status': 'not_initialized',
                'message': 'Camera not initialized'
            })
        
        if not camera.isOpened():
            return jsonify({
                'status': 'not_opened',
                'message': 'Camera not opened'
            })
        
        # Try to read a frame
        ret, frame = camera.read()
        if not ret:
            return jsonify({
                'status': 'capture_failed',
                'message': 'Cannot capture frames'
            })
        
        if frame is None:
            return jsonify({
                'status': 'null_frame',
                'message': 'Camera returns null frames'
            })
        
        # Get camera properties
        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = camera.get(cv2.CAP_PROP_FPS)
        
        return jsonify({
            'status': 'working',
            'message': 'Camera is working properly',
            'frame_size': f'{width}x{height}',
            'fps': fps
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Camera test failed: {str(e)}'
        })

@app.route('/stop_camera')
def stop_camera():
    global camera, current_cube_state
    try:
        if camera is not None:
            camera.release()
            camera = None
        current_cube_state = None
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)