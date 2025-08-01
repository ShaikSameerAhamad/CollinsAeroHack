import cv2
import numpy as np
from sklearn.cluster import KMeans
import webcolors

class CubeVisionDetector:
    """
    Computer vision system to detect Rubik's cube colors from camera feed
    """
    
    def __init__(self):
        # HSV color ranges for cube colors
        self.color_ranges = {
            'red': [(0, 50, 50), (10, 255, 255), (170, 50, 50), (180, 255, 255)],
            'orange': [(10, 50, 50), (25, 255, 255)],
            'yellow': [(25, 50, 50), (35, 255, 255)],
            'green': [(35, 50, 50), (85, 255, 255)],
            'blue': [(85, 50, 50), (130, 255, 255)],
            'white': [(0, 0, 180), (180, 30, 255)]
        }
        
        # Color mapping for cube representation
        self.color_map = {
            'red': 'R',
            'orange': 'O', 
            'yellow': 'Y',
            'green': 'G',
            'blue': 'B',
            'white': 'W'
        }
        
        # Grid positions for 3x3 detection
        self.grid_positions = []
        self._calculate_grid_positions()
    
    def _calculate_grid_positions(self):
        """Calculate 3x3 grid positions for tile detection"""
        # These will be calculated based on detected cube region
        self.grid_positions = [
            (0.2, 0.2), (0.5, 0.2), (0.8, 0.2),  # Top row
            (0.2, 0.5), (0.5, 0.5), (0.8, 0.5),  # Middle row
            (0.2, 0.8), (0.5, 0.8), (0.8, 0.8)   # Bottom row
        ]
    
    def detect_face_colors(self, frame):
        """
        Detect colors of a cube face from camera frame
        Returns list of 9 colors in reading order (left-to-right, top-to-bottom)
        """
        try:
            # Preprocess frame
            processed_frame = self._preprocess_frame(frame)
            
            # Detect cube region
            cube_region = self._detect_cube_region(processed_frame)
            
            if cube_region is None:
                return None
            
            # Extract colors from 3x3 grid
            colors = self._extract_grid_colors(cube_region)
            
            return colors
        
        except Exception as e:
            print(f"Error in color detection: {e}")
            return None
    
    def _preprocess_frame(self, frame):
        """Preprocess frame for better color detection"""
        # Resize frame for consistent processing
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # Enhance contrast
        lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _detect_cube_region(self, frame):
        """
        Detect the cube face region in the frame
        Returns the region of interest containing the cube face
        """
        # Convert to HSV for better color segmentation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for cube colors
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for color_name, ranges in self.color_ranges.items():
            if color_name == 'red':  # Red has two ranges
                lower1, upper1, lower2, upper2 = ranges
                mask1 = cv2.inRange(hsv, np.array(lower1), np.array(upper1))
                mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                color_mask = cv2.bitwise_or(mask1, mask2)
            else:
                lower, upper = ranges
                color_mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            mask = cv2.bitwise_or(mask, color_mask)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            # Fallback: use center region of frame
            h, w = frame.shape[:2]
            margin = min(h, w) // 4
            return frame[margin:h-margin, margin:w-margin]
        
        # Find largest rectangular contour (assumed to be cube face)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Extract region with some padding
        padding = 20
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2 * padding)
        h = min(frame.shape[0] - y, h + 2 * padding)
        
        return frame[y:y+h, x:x+w]
    
    def _extract_grid_colors(self, cube_region):
        """
        Extract colors from 3x3 grid positions
        Returns list of 9 color codes
        """
        colors = []
        h, w = cube_region.shape[:2]
        
        # Sample colors from grid positions
        for rel_x, rel_y in self.grid_positions:
            # Convert relative position to absolute
            x = int(rel_x * w)
            y = int(rel_y * h)
            
            # Extract small region around the point
            region_size = min(w, h) // 12  # Adaptive region size
            x1 = max(0, x - region_size)
            y1 = max(0, y - region_size)
            x2 = min(w, x + region_size)
            y2 = min(h, y + region_size)
            
            tile_region = cube_region[y1:y2, x1:x2]
            
            # Get dominant color in this region
            color = self._get_dominant_color(tile_region)
            colors.append(color)
        
        return colors
    
    def _get_dominant_color(self, region):
        """
        Get the dominant color in a region using K-means clustering
        Returns color code (R, G, B, Y, O, W)
        """
        if region.size == 0:
            return 'W'  # Default to white
        
        # Reshape image to be a list of pixels
        pixels = region.reshape(-1, 3)
        
        # Apply K-means clustering to find dominant colors
        try:
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Get the most common cluster center
            labels = kmeans.labels_
            label_counts = np.bincount(labels)
            dominant_cluster = np.argmax(label_counts)
            dominant_color_bgr = kmeans.cluster_centers_[dominant_cluster]
            
            # Convert BGR to RGB
            dominant_color_rgb = dominant_color_bgr[::-1]
            
        except:
            # Fallback: use mean color
            dominant_color_rgb = np.mean(pixels, axis=0)[::-1]
        
        # Convert to color name
        return self._rgb_to_cube_color(dominant_color_rgb)
    
    def _rgb_to_cube_color(self, rgb):
        """
        Convert RGB values to cube color code
        Returns one of: R, G, B, Y, O, W
        """
        r, g, b = rgb
        
        # Convert to HSV for better color classification
        rgb_normalized = np.array([[[r, g, b]]], dtype=np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)[0][0]
        h, s, v = hsv
        
        # Classify color based on HSV values
        if v < 100:  # Very dark - could be any color in shadow
            # Use RGB ratios for dark colors
            if r > g and r > b:
                return 'R'
            elif g > r and g > b:
                return 'G'
            elif b > r and b > g:
                return 'B'
            else:
                return 'W'
        
        if s < 50:  # Low saturation - white or very light color
            return 'W'
        
        if v > 200 and s < 100:  # High value, low saturation
            return 'W'
        
        # Classify by hue
        if h < 10 or h > 170:  # Red range
            return 'R'
        elif 10 <= h < 25:     # Orange range
            return 'O'
        elif 25 <= h < 35:     # Yellow range
            return 'Y'
        elif 35 <= h < 85:     # Green range
            return 'G'
        elif 85 <= h < 130:    # Blue range
            return 'B'
        else:                  # Default case
            # Use RGB values as fallback
            if r > 200 and g > 200 and b > 200:
                return 'W'
            elif r > g + 50 and r > b + 50:
                return 'R'
            elif g > r + 30 and g > b + 30:
                return 'G'
            elif b > r + 30 and b > g + 30:
                return 'B'
            elif r > 150 and g > 100 and b < 100:
                return 'O'
            elif r > 150 and g > 150 and b < 100:
                return 'Y'
            else:
                return 'W'
    
    def draw_detection_overlay(self, frame, colors=None):
        """
        Draw detection overlay on frame for debugging
        """
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Draw grid
        for i, (rel_x, rel_y) in enumerate(self.grid_positions):
            x = int(rel_x * w)
            y = int(rel_y * h)
            
            # Draw circle at detection point
            cv2.circle(overlay, (x, y), 15, (0, 255, 0), 2)
            
            # Draw color if provided
            if colors and i < len(colors):
                color_bgr = self._color_code_to_bgr(colors[i])
                cv2.circle(overlay, (x, y), 10, color_bgr, -1)
                
                # Draw text
                cv2.putText(overlay, colors[i], (x + 20, y + 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return overlay
    
    def _color_code_to_bgr(self, color_code):
        """Convert color code to BGR for OpenCV drawing"""
        color_bgr_map = {
            'R': (0, 0, 255),     # Red
            'G': (0, 255, 0),     # Green
            'B': (255, 0, 0),     # Blue
            'Y': (0, 255, 255),   # Yellow
            'O': (0, 165, 255),   # Orange
            'W': (255, 255, 255)   # White
        }
        return color_bgr_map.get(color_code, (128, 128, 128))  # Gray as default