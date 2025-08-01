import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

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
      <mesh>
        <boxGeometry args={[0.98, 0.98, 0.98]} />
        <meshStandardMaterial color="#222" />
      </mesh>
      {faces.map(([face, offset, rot]) => {
        const color = getStickerColor(face as string, x, y, z);
        return color ? (
          <mesh key={face as string} position={offset as [number, number, number]} rotation={rot as [number, number, number]}>
            <planeGeometry args={[0.9, 0.9]} />
            <meshBasicMaterial color={color} />
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
    <Canvas camera={{ position: [5, 5, 5], fov: 60 }}>
      <ambientLight intensity={0.7} />
      <directionalLight position={[5, 10, 7]} intensity={1} />
      {positions.map((pos, i) => (
        <Cubie key={i} position={pos as [number, number, number]} />
      ))}
      <OrbitControls />
    </Canvas>
  );
}
