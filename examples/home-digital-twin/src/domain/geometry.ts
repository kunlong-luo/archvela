/**
 * Only site and H1 footprint values listed here are confirmed project inputs.
 * Building placement in the site plan and wall/floor heights are NOT approved.
 * Never represent the demonstration as as-built or construction geometry.
 */
export const dimensions = Object.freeze({
  plotWidthM: 15,
  plotDepthM: 14,
  houseWidthM: 11.2,
  houseDepthM: 8.4,
  demonstrationFloorHeightM: 2.8
});

export function areaM2(width: number, depth: number): number {
  if (!(width > 0 && depth > 0)) throw new Error("Dimensions must be positive");
  return Math.round(width * depth * 100) / 100;
}

export const houseAreaM2 = areaM2(dimensions.houseWidthM, dimensions.houseDepthM);
export const plotAreaM2 = areaM2(dimensions.plotWidthM, dimensions.plotDepthM);

export function fitsWithinRect(outerX: number, outerZ: number, innerX: number, innerZ: number): boolean {
  return outerX > 0 && outerZ > 0 && innerX > 0 && innerZ > 0 && innerX <= outerX && innerZ <= outerZ;
}

export const disclosure = "仅演示尺寸比例与交互。主屋位置、门窗、层高和附属厨房未通过施工图核定，切勿用于施工放样。";
