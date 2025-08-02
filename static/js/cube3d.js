// cube3d.js
import RubiksCube3D from './RubiksCube3D.js';

let previewCube = null;
let solutionCube = null;

function initPreview() {
    if (previewCube) {
        previewCube.destroy();
    }
    previewCube = new RubiksCube3D('preview-cube-container');
}

function initSolution() {
    if (solutionCube) {
        solutionCube.destroy();
    }
    solutionCube = new RubiksCube3D('cube-3d-solution');
}

function updatePreview(cubeState) {
    if (previewCube) {
        previewCube.updateCubeState(cubeState);
    }
}

function updateSolution(cubeState) {
    if (solutionCube) {
        solutionCube.updateCubeState(cubeState);
    }
}

// Export functions for use in other files
window.cube3D = {
    initPreview,
    initSolution,
    updatePreview,
    updateSolution
};
