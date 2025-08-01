#!/usr/bin/env python3
"""
Test script to reproduce the move engine issue where a solved cube
(all colors the same) still suggests moves.
"""


# NOTE: The solver now uses the kociemba library for optimal solutions.
# Ensure that cube colors and face order match kociemba's expectations:
# Faces: up, right, front, down, left, back. Colors: W, R, B, O, G, Y.
from cube_model import RubiksCube
from cube_solver import RubiksCubeSolver

def test_solved_cube_issue():
    """Test the issue where a solved cube suggests unnecessary moves"""
    print("Testing move engine with already solved cube...")
    
    # Create a solved cube (all faces same color as center)
    cube = RubiksCube()
    
    # Verify it's solved
    print(f"Is cube solved? {cube.is_solved()}")
    print(f"Is cube valid? {cube.is_valid()}")
    
    # Print cube state
    print("\nCube state:")
    print(cube.get_state_string())
    
    # Try to solve it
    solver = RubiksCubeSolver(cube)
    solution = solver.solve()
    
    print(f"\nSolution suggested: {solution}")
    print(f"Number of moves: {len(solution)}")
    
    # This should be 0 moves for a solved cube!
    if len(solution) == 0:
        print("✅ PASS: Correctly identified solved cube")
    else:
        print("❌ FAIL: Suggested moves for already solved cube")
        
    return len(solution)

def test_mixed_color_cube():
    """Test with a cube that has all same colors (invalid but should be handled)"""
    print("\n" + "="*50)
    print("Testing cube with all same colors...")
    
    cube = RubiksCube()
    
    # Set all faces to the same color (this creates an invalid cube)
    for face_name in cube.faces.keys():
        cube.set_face(face_name, ['R'] * 9)  # All red
    
    print(f"Is cube solved? {cube.is_solved()}")
    print(f"Is cube valid? {cube.is_valid()}")
    
    # Try to solve it
    solver = RubiksCubeSolver(cube)
    solution = solver.solve()
    
    print(f"\nSolution suggested: {solution}")
    print(f"Number of moves: {len(solution)}")
    
    return len(solution)

if __name__ == "__main__":
    print("Rubik's Cube Solver Issue Test")
    print("="*50)
    
    # Test 1: Already solved cube
    moves1 = test_solved_cube_issue()
    
    # Test 2: All same colors
    moves2 = test_mixed_color_cube()
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Solved cube suggested moves: {moves1}")
    print(f"Same-color cube suggested moves: {moves2}")
    
    if moves1 > 0:
        print("\n🚨 BUG CONFIRMED: Solver suggests moves for already solved cube!")
    else:
        print("\n✅ No issue found with solved cube")
