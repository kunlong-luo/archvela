import { Canvas } from "@react-three/fiber";
import { dimensions } from "../domain/geometry";

type Props = { floor: 1 | 2; angle: number; onSelect: (value: string) => void; };
const width = dimensions.houseWidthM;
const depth = dimensions.houseDepthM;
const floorH = dimensions.demonstrationFloorHeightM;

function Wall({position, size, onClick}: {position:[number,number,number];size:[number,number,number];onClick:()=>void}) {
  return <mesh position={position} onClick={event => {event.stopPropagation();onClick();}} castShadow>
    <boxGeometry args={size}/>
    <meshStandardMaterial color="#e8e9dd" roughness={0.91}/>
  </mesh>;
}

function House({floor,angle,onSelect}:Props) {
  const y = floor === 1 ? 0.18 : floorH + 0.18;
  return <group rotation={[0,angle,0]}>
    <mesh position={[0,-0.13,0]} receiveShadow><boxGeometry args={[dimensions.plotWidthM,0.14,dimensions.plotDepthM]}/><meshStandardMaterial color="#84a49a"/></mesh>
    <mesh position={[0,y,0]} onClick={event=>{event.stopPropagation();onSelect(floor===1?"一层楼板（示意）":"二层楼板（示意）")}}>
      <boxGeometry args={[width,0.28,depth]}/><meshStandardMaterial color={floor===1?"#c2cbbd":"#d3c19c"}/>
    </mesh>
    <Wall position={[0,y+1.27,-depth/2]} size={[width,2.5,0.18]} onClick={()=>onSelect("北侧外墙（示意）")}/>
    <Wall position={[-width/2,y+1.27,0]} size={[0.18,2.5,depth]} onClick={()=>onSelect("西侧外墙（示意）")}/>
    <Wall position={[width/2,y+1.27,0]} size={[0.18,2.5,depth]} onClick={()=>onSelect("东侧外墙（示意）")}/>
    <Wall position={[0,y+1.27,depth/2]} size={[width,2.5,0.18]} onClick={()=>onSelect("南侧外墙（示意）")}/>
    <mesh position={[0,y+2.53,0]} onClick={event=>{event.stopPropagation();onSelect("屋顶轮廓（示意，不代表实际坡度）")}}>
      <boxGeometry args={[width+0.5,0.12,depth+0.5]}/>
      <meshStandardMaterial color="#526f66" transparent opacity={0.48}/>
    </mesh>
  </group>;
}
export default function HouseScene({floor,angle,onSelect}:Props){
  return <Canvas shadows dpr={[1,1.5]} frameloop="demand"
    camera={{position:[17,16,19],fov:42,near:0.1,far:150}}
    onPointerMissed={()=>onSelect("请选择主屋构件")}
    fallback={<p role="status">无法初始化 WebGL。可切回平面模式查看尺寸。</p>}>
    <color attach="background" args={["#edf1e9"]}/>
    <ambientLight intensity={1.7}/>
    <directionalLight position={[10,18,7]} intensity={2.7} castShadow shadow-mapSize={[1024,1024]}/>
    <House floor={floor} angle={angle} onSelect={onSelect}/>
  </Canvas>;
}
