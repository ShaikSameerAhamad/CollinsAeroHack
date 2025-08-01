import copy

class RubiksCube:
    """
    3x3 Rubik's Cube representation
    Each face is represented as a 3x3 grid with colors
    """
    
    def __init__(self):
        # Initialize solved cube
        # Colors: W=White, O=Orange, G=Green, R=Red, B=Blue, Y=Yellow
        self.faces = {
            'up': [['W'] * 3 for _ in range(3)],      # Top face
            'down': [['Y'] * 3 for _ in range(3)],    # Bottom face
            'front': [['R'] * 3 for _ in range(3)],   # Front face
            'back': [['O'] * 3 for _ in range(3)],    # Back face
            'right': [['B'] * 3 for _ in range(3)],   # Right face
            'left': [['G'] * 3 for _ in range(3)]     # Left face
        }
        
        # Color mapping for validation
        self.color_map = {'W': 'white', 'Y': 'yellow', 'R': 'red', 
                         'O': 'orange', 'B': 'blue', 'G': 'green'}
        
    def set_face(self, face_name, colors):
        """Set colors for a specific face"""
        if face_name not in self.faces:
            raise ValueError(f"Invalid face name: {face_name}")
        
        # Convert flat list to 3x3 grid
        if len(colors) == 9:
            self.faces[face_name] = [
                [colors[0], colors[1], colors[2]],
                [colors[3], colors[4], colors[5]],
                [colors[6], colors[7], colors[8]]
            ]
        else:
            raise ValueError("Face must have exactly 9 colors")
    
    def get_face_flat(self, face_name):
        """Get face colors as flat list"""
        face = self.faces[face_name]
        return [face[i][j] for i in range(3) for j in range(3)]
    
    def is_solved(self):
        """Check if cube is in solved state"""
        for face_name, face in self.faces.items():
            center_color = face[1][1]  # Center piece
            for row in face:
                for color in row:
                    if color != center_color:
                        return False
        return True
    
    def is_valid(self):
        """Validate if cube configuration is legal"""
        try:
            # Count colors
            color_count = {}
            for face in self.faces.values():
                for row in face:
                    for color in row:
                        color_count[color] = color_count.get(color, 0) + 1
            
            # Each color should appear exactly 9 times
            for color in ['W', 'Y', 'R', 'O', 'B', 'G']:
                if color_count.get(color, 0) != 9:
                    return False
            
            # Check centers are different
            centers = [self.faces[face][1][1] for face in self.faces.keys()]
            if len(set(centers)) != 6:
                return False
            
            # Additional validation for edge and corner pieces
            return self._validate_pieces()
            
        except Exception:
            return False
    
    def _validate_pieces(self):
        """Validate edge and corner pieces"""
        # Simplified validation - in a real implementation,
        # this would check edge and corner permutation parity
        return True
    
    def copy(self):
        """Create a deep copy of the cube"""
        new_cube = RubiksCube()
        new_cube.faces = copy.deepcopy(self.faces)
        return new_cube
    
    def apply_move(self, move):
        """Apply a move to the cube"""
        if move.endswith("'"):
            # Prime move (counterclockwise)
            base_move = move[:-1]
            self._apply_base_move(base_move, clockwise=False)
        elif move.endswith("2"):
            # Double move
            base_move = move[:-1]
            self._apply_base_move(base_move, clockwise=True)
            self._apply_base_move(base_move, clockwise=True)
        else:
            # Regular move (clockwise)
            self._apply_base_move(move, clockwise=True)
    
    def _apply_base_move(self, move, clockwise=True):
        """Apply base move (U, D, L, R, F, B)"""
        if move == 'U':
            self._rotate_up(clockwise)
        elif move == 'D':
            self._rotate_down(clockwise)
        elif move == 'L':
            self._rotate_left(clockwise)
        elif move == 'R':
            self._rotate_right(clockwise)
        elif move == 'F':
            self._rotate_front(clockwise)
        elif move == 'B':
            self._rotate_back(clockwise)
        else:
            raise ValueError(f"Invalid move: {move}")
    
    def _rotate_face(self, face_name, clockwise=True):
        """Rotate a face 90 degrees"""
        face = self.faces[face_name]
        if clockwise:
            # Clockwise rotation
            self.faces[face_name] = [[face[2-j][i] for j in range(3)] for i in range(3)]
        else:
            # Counterclockwise rotation
            self.faces[face_name] = [[face[j][2-i] for j in range(3)] for i in range(3)]
    
    def _rotate_up(self, clockwise=True):
        """Rotate upper face"""
        self._rotate_face('up', clockwise)
        
        # Save first row of affected faces
        temp = self.faces['front'][0].copy()
        
        if clockwise:
            self.faces['front'][0] = self.faces['right'][0].copy()
            self.faces['right'][0] = self.faces['back'][0].copy()
            self.faces['back'][0] = self.faces['left'][0].copy()
            self.faces['left'][0] = temp
        else:
            self.faces['front'][0] = self.faces['left'][0].copy()
            self.faces['left'][0] = self.faces['back'][0].copy()
            self.faces['back'][0] = self.faces['right'][0].copy()
            self.faces['right'][0] = temp
    
    def _rotate_down(self, clockwise=True):
        """Rotate bottom face"""
        self._rotate_face('down', clockwise)
        
        # Save last row of affected faces
        temp = self.faces['front'][2].copy()
        
        if clockwise:
            self.faces['front'][2] = self.faces['left'][2].copy()
            self.faces['left'][2] = self.faces['back'][2].copy()
            self.faces['back'][2] = self.faces['right'][2].copy()
            self.faces['right'][2] = temp
        else:
            self.faces['front'][2] = self.faces['right'][2].copy()
            self.faces['right'][2] = self.faces['back'][2].copy()
            self.faces['back'][2] = self.faces['left'][2].copy()
            self.faces['left'][2] = temp
    
    def _rotate_right(self, clockwise=True):
        """Rotate right face"""
        self._rotate_face('right', clockwise)
        
        # Save right column of affected faces
        temp = [self.faces['front'][i][2] for i in range(3)]
        
        if clockwise:
            for i in range(3):
                self.faces['front'][i][2] = self.faces['down'][i][2]
                self.faces['down'][i][2] = self.faces['back'][2-i][0]
                self.faces['back'][2-i][0] = self.faces['up'][i][2]
                self.faces['up'][i][2] = temp[i]
        else:
            for i in range(3):
                self.faces['front'][i][2] = self.faces['up'][i][2]
                self.faces['up'][i][2] = self.faces['back'][2-i][0]
                self.faces['back'][2-i][0] = self.faces['down'][i][2]
                self.faces['down'][i][2] = temp[i]
    
    def _rotate_left(self, clockwise=True):
        """Rotate left face"""
        self._rotate_face('left', clockwise)
        
        # Save left column of affected faces
        temp = [self.faces['front'][i][0] for i in range(3)]
        
        if clockwise:
            for i in range(3):
                self.faces['front'][i][0] = self.faces['up'][i][0]
                self.faces['up'][i][0] = self.faces['back'][2-i][2]
                self.faces['back'][2-i][2] = self.faces['down'][i][0]
                self.faces['down'][i][0] = temp[i]
        else:
            for i in range(3):
                self.faces['front'][i][0] = self.faces['down'][i][0]
                self.faces['down'][i][0] = self.faces['back'][2-i][2]
                self.faces['back'][2-i][2] = self.faces['up'][i][0]
                self.faces['up'][i][0] = temp[i]
    
    def _rotate_front(self, clockwise=True):
        """Rotate front face"""
        self._rotate_face('front', clockwise)
        
        if clockwise:
            # Save bottom row of up face
            temp = self.faces['up'][2].copy()
            self.faces['up'][2] = [self.faces['left'][2-i][2] for i in range(3)]
            for i in range(3):
                self.faces['left'][i][2] = self.faces['down'][0][i]
            self.faces['down'][0] = [self.faces['right'][2-i][0] for i in range(3)]
            for i in range(3):
                self.faces['right'][i][0] = temp[i]
        else:
            # Save bottom row of up face
            temp = self.faces['up'][2].copy()
            for i in range(3):
                self.faces['up'][2][i] = self.faces['right'][i][0]
            self.faces['right'] = [[self.faces['down'][0][2-i] if j == 0 else self.faces['right'][i][j] for j in range(3)] for i in range(3)]
            for i in range(3):
                self.faces['down'][0][i] = self.faces['left'][i][2]
            for i in range(3):
                self.faces['left'][i][2] = temp[2-i]
    
    def _rotate_back(self, clockwise=True):
        """Rotate back face"""
        self._rotate_face('back', clockwise)
        
        if clockwise:
            # Save top row of up face
            temp = self.faces['up'][0].copy()
            for i in range(3):
                self.faces['up'][0][i] = self.faces['right'][i][2]
            for i in range(3):
                self.faces['right'][i][2] = self.faces['down'][2][2-i]
            self.faces['down'][2] = [self.faces['left'][2-i][0] for i in range(3)]
            for i in range(3):
                self.faces['left'][i][0] = temp[2-i]
        else:
            # Save top row of up face
            temp = self.faces['up'][0].copy()
            self.faces['up'][0] = [self.faces['left'][2-i][0] for i in range(3)]
            for i in range(3):
                self.faces['left'][i][0] = self.faces['down'][2][i]
            for i in range(3):
                self.faces['down'][2][i] = self.faces['right'][2-i][2]
            for i in range(3):
                self.faces['right'][i][2] = temp[i]
    
    def get_state_string(self):
        """Get cube state as string for debugging"""
        result = ""
        for face_name in ['up', 'down', 'front', 'back', 'right', 'left']:
            result += f"{face_name}: {self.get_face_flat(face_name)}\n"
        return result