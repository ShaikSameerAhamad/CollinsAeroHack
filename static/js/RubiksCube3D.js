// RubiksCube3D.js
import * as THREE from 'https://unpkg.com/three@0.154.0/build/three.module.js';

class RubiksCube3D {
    constructor(containerId) {
        this.mountElement = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.cubeGroup = null;
        this.isMouseDown = false;
        this.mousePos = { x: 0, y: 0 };
        this.rotation = { x: 0.3, y: 0.3 };
        this.zoom = 8;
        this.animationId = null;

        // Cube colors
        this.colors = {
            front: 0xff0000,   // Bright Red
            back: 0xff6600,    // Bright Orange
            right: 0x00ff00,   // Bright Green
            left: 0x0066ff,    // Bright Blue
            top: 0xffff00,     // Bright Yellow
            bottom: 0xffffff   // Pure White
        };

        this.init();
        this.setupEventListeners();
    }

    updateState(cubeState) {
        // Update colors based on cube state
        this.colors = {
            front: this.colorMap[cubeState.front[4]],  // Center piece color
            back: this.colorMap[cubeState.back[4]],
            right: this.colorMap[cubeState.right[4]],
            left: this.colorMap[cubeState.left[4]],
            top: this.colorMap[cubeState.up[4]],
            bottom: this.colorMap[cubeState.down[4]]
        };
        
        // Recreate the cube with new colors
        if (this.cubeGroup) {
            this.scene.remove(this.cubeGroup);
        }
        this.createCube();
    }

    createCubelet(x, y, z) {
        const geometry = new THREE.BoxGeometry(0.98, 0.98, 0.98);
        
        const materials = [
            new THREE.MeshLambertMaterial({ color: x === 1 ? this.colors.right : 0x101010 }), // Right
            new THREE.MeshLambertMaterial({ color: x === -1 ? this.colors.left : 0x101010 }), // Left
            new THREE.MeshLambertMaterial({ color: y === 1 ? this.colors.top : 0x101010 }), // Top
            new THREE.MeshLambertMaterial({ color: y === -1 ? this.colors.bottom : 0x101010 }), // Bottom
            new THREE.MeshLambertMaterial({ color: z === 1 ? this.colors.front : 0x101010 }), // Front
            new THREE.MeshLambertMaterial({ color: z === -1 ? this.colors.back : 0x101010 }) // Back
        ];

        const cube = new THREE.Mesh(geometry, materials);
        cube.position.set(x, y, z);
        
        const edges = new THREE.EdgesGeometry(geometry);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x000000, linewidth: 2 }));
        line.position.set(x, y, z);
        
        return { cube, line };
    }

    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);

        // Camera
        this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 1000);
        this.updateCameraPosition();

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(600, 600);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 1024;
        directionalLight.shadow.mapSize.height = 1024;
        this.scene.add(directionalLight);

        // Create cube
        this.cubeGroup = new THREE.Group();
        
        for (let x = -1; x <= 1; x++) {
            for (let y = -1; y <= 1; y++) {
                for (let z = -1; z <= 1; z++) {
                    const { cube, line } = this.createCubelet(x, y, z);
                    cube.castShadow = true;
                    cube.receiveShadow = true;
                    this.cubeGroup.add(cube);
                    this.cubeGroup.add(line);
                }
            }
        }
        
        this.cubeGroup.rotation.x = this.rotation.x;
        this.cubeGroup.rotation.y = this.rotation.y;
        
        this.scene.add(this.cubeGroup);

        // Mount
        if (this.mountElement) {
            this.mountElement.appendChild(this.renderer.domElement);
            this.startAnimation();
        }
    }

    updateCameraPosition() {
        const distance = this.zoom;
        this.camera.position.set(distance, distance, distance);
        this.camera.lookAt(0, 0, 0);
    }

    startAnimation() {
        const animate = () => {
            this.animationId = requestAnimationFrame(animate);
            this.renderer.render(this.scene, this.camera);
        };
        animate();
    }

    setupEventListeners() {
        if (!this.mountElement) return;

        this.mountElement.addEventListener('mousedown', this.handleMouseDown.bind(this));
        document.addEventListener('mouseup', this.handleMouseUp.bind(this));
        document.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.mountElement.addEventListener('wheel', this.handleWheel.bind(this));
        
        // Touch events
        this.mountElement.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.mountElement.addEventListener('touchend', this.handleTouchEnd.bind(this));
        this.mountElement.addEventListener('touchmove', this.handleTouchMove.bind(this));
    }

    handleMouseDown(e) {
        this.isMouseDown = true;
        this.mousePos = { x: e.clientX, y: e.clientY };
        this.mountElement.style.cursor = 'grabbing';
    }

    handleMouseUp() {
        this.isMouseDown = false;
        if (this.mountElement) {
            this.mountElement.style.cursor = 'grab';
        }
    }

    handleMouseMove(e) {
        if (!this.isMouseDown || !this.cubeGroup) return;

        const deltaX = e.clientX - this.mousePos.x;
        const deltaY = e.clientY - this.mousePos.y;

        this.rotation.y += deltaX * 0.01;
        this.rotation.x += deltaY * 0.01;

        this.cubeGroup.rotation.y = this.rotation.y;
        this.cubeGroup.rotation.x = this.rotation.x;

        this.mousePos = { x: e.clientX, y: e.clientY };
    }

    handleWheel(e) {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 1 : -1;
        this.zoom = Math.max(4, Math.min(15, this.zoom + delta * 0.5));
        this.updateCameraPosition();
    }

    handleTouchStart(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.isMouseDown = true;
            this.mousePos = { x: touch.clientX, y: touch.clientY };
        }
    }

    handleTouchEnd(e) {
        e.preventDefault();
        this.isMouseDown = false;
    }

    handleTouchMove(e) {
        e.preventDefault();
        if (!this.isMouseDown || !this.cubeGroup || e.touches.length !== 1) return;

        const touch = e.touches[0];
        const deltaX = touch.clientX - this.mousePos.x;
        const deltaY = touch.clientY - this.mousePos.y;

        this.rotation.y += deltaX * 0.01;
        this.rotation.x += deltaY * 0.01;

        this.cubeGroup.rotation.y = this.rotation.y;
        this.cubeGroup.rotation.x = this.rotation.x;

        this.mousePos = { x: touch.clientX, y: touch.clientY };
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.mountElement && this.renderer) {
            this.mountElement.removeChild(this.renderer.domElement);
        }

        // Remove event listeners
        document.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        document.removeEventListener('mouseup', this.handleMouseUp.bind(this));
    }
}

export default RubiksCube3D;
