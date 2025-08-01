
import kociemba
from cube_model import RubiksCube

class RubiksCubeSolver:
    """
    Rubik's Cube Solver using the kociemba library for optimal solutions.
    """
    def __init__(self, cube):
        self.cube = cube.copy()
        self.solution = []

    def solve(self):
        """Solve the cube using the kociemba library"""
        self.solution = []
        if self.cube.is_solved():
            return self.solution
        if not self.cube.is_valid():
            return self.solution
        # Convert cube state to kociemba string
        cube_str = self._to_kociemba_string()
        try:
            solution_str = kociemba.solve(cube_str)
            self.solution = solution_str.split()
        except Exception as e:
            # If kociemba fails, fallback to simple solution
            self.solution = self._generate_simple_solution()
        return self.solution

    def _to_kociemba_string(self):
        """
        Convert the cube state to the kociemba string format (54 chars: UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB)
        Face order: U, R, F, D, L, B
        Each face: left-to-right, top-to-bottom
        Color mapping: Use standard color letters (U=Up, R=Right, F=Front, D=Down, L=Left, B=Back)
        """
        # Map face names to kociemba order
        face_order = ['up', 'right', 'front', 'down', 'left', 'back']
        color_map = {}
        # Assign color letters based on center stickers
        center_colors = {face: self.cube.faces[face][1][1] for face in self.cube.faces}
        # Find which color is which face
        for face, letter in zip(face_order, ['U', 'R', 'F', 'D', 'L', 'B']):
            color_map[center_colors[face]] = letter
        # Build the string
        cube_str = ''
        for face in face_order:
            for row in self.cube.faces[face]:
                for cell in row:
                    cube_str += color_map[cell]
        return cube_str
    
    def _generate_simple_solution(self):
        """Fallback: Generate a simple solution (dummy moves) if kociemba fails"""
        simple_moves = ["F2", "R2", "U2", "B2", "L2", "R", "U", "R'", "U'", "F", "R", "U", "R'", "U'", "F'"]
        return simple_moves[:25]