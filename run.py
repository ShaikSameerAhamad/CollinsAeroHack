#!/usr/bin/env python3
"""
Enhanced Rubik's Cube Solver Application Runner
Includes error handling, logging, and development features
"""

import os
import sys
import logging
from datetime import datetime
import webbrowser
import threading
import time

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # NOTE: The solver now uses the kociemba library for optimal solutions.
    # Ensure that cube colors and face order match kociemba's expectations:
    # Faces: up, right, front, down, left, back. Colors: W, R, B, O, G, Y.
    from app import app
    import cv2
    import numpy as np
    from cube_model import RubiksCube
    from cube_solver import RubiksCubeSolver
    from vision_detector import CubeVisionDetector
except ImportError as e:
    print(f"ERROR: Import Error: {e}")
    print("\nPlease install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging configuration with Unicode support"""
    # Configure logging to handle Unicode properly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cube_solver.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Ensure the StreamHandler can handle Unicode
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setStream(sys.stdout)
    
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are available"""
    logger = logging.getLogger(__name__)
    
    try:
        # Test OpenCV
        cv2.__version__
        logger.info(f"[OK] OpenCV version: {cv2.__version__}")
        
        # Test camera access
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            logger.info("[OK] Camera access: Available")
            cap.release()
        else:
            logger.warning("[WARNING] Camera access: Not available (vision input will not work)")
        
        # Test cube solver
        test_cube = RubiksCube()
        solver = RubiksCubeSolver(test_cube)
        logger.info("[OK] Cube solver: Initialized successfully")
        
        # Test vision detector
        detector = CubeVisionDetector()
        logger.info("[OK] Vision detector: Initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"[ERROR] Dependency check failed: {e}")
        return False

def open_browser(url, delay=1.5):
    """Open browser after a delay"""
    time.sleep(delay)
    try:
        webbrowser.open(url)
    except Exception:
        pass  # Ignore browser opening errors

def print_banner():
    """Print application banner"""
    banner = """
    +==============================================================+
    |                 RUBIK'S CUBE SOLVER                          |
    |                                                              |  
    |              Advanced 3x3 Solver with Custom Algorithm      |
    |                                                              |
    |  Features:                                                   |
    |    • Custom Layer-by-Layer Algorithm                        |
    |    • Manual Color Input Interface                           |
    |    • Computer Vision Cube Scanning                          |
    |    • Solutions in 25 moves or less                          |
    |    • Real-time validation                                   |
    |                                                              |
    +==============================================================+
    """
    print(banner)

def print_startup_info():
    """Print startup information"""
    print("\nStarting Rubik's Cube Solver...")
    print(f"Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Working Directory: {os.getcwd()}")

def print_usage_info():
    """Print usage information"""
    usage_info = """
    
    USAGE INSTRUCTIONS:
    ===================
    
    1. Open your web browser and go to: http://localhost:5000
    
    2. Choose your input method:
       • Manual Input: Click and select colors for each square
       • Vision Input: Use your webcam to scan a real cube
    
    3. Controls:
       • Click colors from the palette
       • Click cube squares to apply colors
       • Use keyboard shortcuts (1-6 for colors)
       • Drag to paint multiple squares
    
    4. Solve your cube:
       • Click "Solve Cube" to get the solution
       • Follow the move notation (U, R', F2, etc.)
       • Solutions guaranteed in 25 moves or less!
    
    KEYBOARD SHORTCUTS:
    ===================
    • 1-6: Select colors (Red, Green, Blue, Yellow, Orange, White)
    • Ctrl+R: Reset cube
    • Ctrl+S: Solve cube
    
    TROUBLESHOOTING:
    ================
    • Camera not working? Check browser permissions
    • Colors not detecting? Ensure good lighting
    • Invalid cube? Check color counts (9 of each)
    """
    print(usage_info)

def main():
    """Main application entry point"""
    # Setup logging
    logger = setup_logging()
    
    # Print banner
    print_banner()
    
    # Print startup info
    print_startup_info()
    
    # Check dependencies
    if not check_dependencies():
        print("\nERROR: Failed to initialize dependencies. Please check the logs.")
        return 1
    
    # Configuration
    host = '0.0.0.0'
    port = 5000
    debug = True
    
    print(f"\nConfiguration:")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Debug: {debug}")
    
    # Open browser in background thread
    url = f"http://localhost:{port}"
    browser_thread = threading.Thread(target=open_browser, args=(url,))
    browser_thread.daemon = True
    browser_thread.start()
    
    print(f"\nOpening browser at: {url}")
    
    # Print usage instructions
    print_usage_info()
    
    print("\nStarting Flask server...")
    print(f"Server running at: {url}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start Flask app
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=False  # Disable reloader to avoid duplicate processes
        )
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        return 0
    except Exception as e:
        logger.error(f"Server error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())