import * as THREE from "three";

// Loaded only after the visitor requests the 3D experience.
export function mountScene(canvas: HTMLCanvasElement): () => void {
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  let frame = 0;
  let disposed = false;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
  camera.position.set(0, 0, 8);
  const group = new THREE.Group();
  const geometry = new THREE.TorusKnotGeometry(1.55, 0.43, 160, 18, 2, 3);
  const material = new THREE.MeshStandardMaterial({ color: 0xb9a48e, metalness: 0.52, roughness: 0.32 });
  const mesh = new THREE.Mesh(geometry, material);
  group.add(mesh);
  scene.add(group);
  const light = new THREE.DirectionalLight(0xffe2bb, 3);
  light.position.set(3, 5, 7);
  scene.add(light, new THREE.AmbientLight(0xffffff, 1.4));
  const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const resize = () => {
    const parent = canvas.parentElement;
    if (!parent || disposed) return;
    const width = Math.max(1, parent.clientWidth);
    const height = Math.max(1, parent.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  const observer = new ResizeObserver(resize);
  observer.observe(canvas.parentElement || canvas);
  resize();
  const draw = () => {
    if (disposed) return;
    if (!motion.matches) group.rotation.y += 0.003;
    group.rotation.x = 0.14;
    renderer.render(scene, camera);
    frame = window.requestAnimationFrame(draw);
  };
  draw();
  return () => {
    disposed = true;
    window.cancelAnimationFrame(frame);
    observer.disconnect();
    geometry.dispose();
    material.dispose();
    renderer.dispose();
  };
}
