import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import * as THREE from 'three';

const FACE_COLORS = {
  U: '#ffffff', // White
  D: '#ffff00', // Yellow
  F: '#ff0000', // Red
  B: '#ff8800', // Orange
  L: '#0000ff', // Blue
  R: '#00ff00', // Green
};

function getStickerColor(face: string, x: number, y: number, z: number) {
  if (face === 'U' && y === 1) return FACE_COLORS.U;
  if (face === 'D' && y === -1) return FACE_COLORS.D;
  if (face === 'F' && z === 1) return FACE_COLORS.F;
  if (face === 'B' && z === -1) return FACE_COLORS.B;
  if (face === 'L' && x === -1) return FACE_COLORS.L;
  if (face === 'R' && x === 1) return FACE_COLORS.R;
  return null;
}

function Cubie({ position }: { position: [number, number, number] }) {
  const meshRef = useRef();
  const [x, y, z] = position;
  const faces = [
    ['U', [0, 0.51, 0], [Math.PI / 2, 0, 0]],
    ['D', [0, -0.51, 0], [-Math.PI / 2, 0, 0]],
    ['F', [0, 0, 0.51], [0, 0, 0]],
    ['B', [0, 0, -0.51], [0, Math.PI, 0]],
    ['L', [-0.51, 0, 0], [0, Math.PI / 2, 0]],
    ['R', [0.51, 0, 0], [0, -Math.PI / 2, 0]],
  ];
  return (
    <group position={position}>
      <mesh ref={meshRef} castShadow>
        <boxGeometry args={[0.98, 0.98, 0.98]} />
        <meshStandardMaterial color="#222" roughness={0.3} metalness={0.1} />
      </mesh>
      {faces.map(([face, offset, rot]) => {
        const color = getStickerColor(face as string, x, y, z);
        return color ? (
          <mesh 
            key={face as string} 
            position={offset as [number, number, number]} 
            rotation={rot as [number, number, number]}
            castShadow
          >
            <planeGeometry args={[0.9, 0.9]} />
            <meshStandardMaterial 
              color={color} 
              roughness={0.3} 
              metalness={0.1}
            />
          </mesh>
        ) : null;
      })}
    </group>
  );
}

export default function RubiksCube3D() {
  const positions: Array<[number, number, number]> = [];
  for (let x = -1; x <= 1; x++)
    for (let y = -1; y <= 1; y++)
      for (let z = -1; z <= 1; z++)
        positions.push([x, y, z]);

  return (
    <div style={{ width: '100%', height: '100%', background: '#1a1a1a' }}>
      <Canvas
        camera={{ position: [5, 5, 5], fov: 50 }}
        shadows
        gl={{ antialias: true }}
      >
        {/* Lighting */}
        <ambientLight intensity={0.3} />
        <directionalLight 
          position={[10, 10, 5]} 
          intensity={1} 
          castShadow 
          shadow-mapSize-width={2048} 
          shadow-mapSize-height={2048}
        />
        <pointLight position={[-10, -10, -10]} intensity={0.5} />
        
        {/* Environment for reflections */}
        <Environment preset="city" />
        
        {/* Rubik's Cube */}
        <group>
          {positions.map((pos, i) => (
            <Cubie key={i} position={pos as [number, number, number]} />
          ))}
        </group>
        
        {/* Controls */}
        <OrbitControls 
          enablePan={false} 
          enableZoom={true} 
          enableRotate={true}
          minDistance={3}
          maxDistance={15}
          rotateSpeed={0.5}
          zoomSpeed={0.5}
        />
        
        {/* Ground plane for shadows */}
        <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]}>
          <planeGeometry args={[20, 20]} />
          <shadowMaterial transparent opacity={0.2} />
        </mesh>
      </Canvas>
    </div>
  );
}
