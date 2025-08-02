import RubiksCube3D from './RubiksCube3D.js';

let previewCube = null;
let solutionCube = null;

function initPreview() {
    console.log("Initializing preview cube...");
    if (previewCube) {
        previewCube.destroy();
    }
    previewCube = new RubiksCube3D('preview-cube-container');
}

function initSolution() {
    console.log("Initializing solution cube...");
    if (solutionCube) {
        solutionCube.destroy();
    }
    solutionCube = new RubiksCube3D('solution-cube-container');
}

function updatePreview(cubeState) {
    console.log("Updating preview cube...");
    if (previewCube) {
        previewCube.updateState(cubeState);
    }
}

function updateSolution(cubeState) {
    console.log("Updating solution cube...");
    if (solutionCube) {
        solutionCube.updateState(cubeState);
    }
}

function animateSolutionMove(move) {
    console.log(`Animating move: ${move}`);
    if (solutionCube) {
        solutionCube.animateMove(move);
    }
}

// Export functions for use in other files
window.cube3D = {
    initPreview,
    initSolution,
    updatePreview,
    updateSolution,
    animateSolutionMove
};