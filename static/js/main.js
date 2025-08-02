import RubiksCube3D from './RubiksCube3D.js';

// Initialize the cube when the solve button is clicked
document.addEventListener('DOMContentLoaded', function() {
    let cube3D = null;

    // Function to handle solve button click
    function handleSolveClick() {
        // Create cube container if it doesn't exist
        let cubeContainer = document.getElementById('cube-3d-container');
        if (!cubeContainer) {
            cubeContainer = document.createElement('div');
            cubeContainer.id = 'cube-3d-container';
            cubeContainer.className = 'cube-3d-container';
            
            // Add zoom indicator
            const zoomIndicator = document.createElement('div');
            zoomIndicator.className = 'zoom-indicator';
            zoomIndicator.style.cssText = `
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 0.5rem;
                font-family: monospace;
            `;
            cubeContainer.appendChild(zoomIndicator);
            
            // Insert the container before the solution container
            const solutionContainer = document.querySelector('.solution-container');
            if (solutionContainer) {
                solutionContainer.parentNode.insertBefore(cubeContainer, solutionContainer);
            }
        }

        // Initialize or reinitialize the 3D cube
        if (cube3D) {
            cube3D.destroy();
        }
        cube3D = new RubiksCube3D('cube-3d-container');
    }

    // Add click event listener to solve buttons
    const solveButtons = document.querySelectorAll('.solve-button');
    solveButtons.forEach(button => {
        button.addEventListener('click', handleSolveClick);
    });
});
