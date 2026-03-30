import type { ProjectPreset } from "@/features/capabilities/presets/lib/preset-types";

export function sortProjectPresets(items: ProjectPreset[]): ProjectPreset[] {
  return [...items].sort((a, b) => {
    if (a.sort_order !== b.sort_order) {
      return a.sort_order - b.sort_order;
    }
    return a.project_preset_id - b.project_preset_id;
  });
}

export function getDefaultProjectPresetId(
  items: ProjectPreset[],
): number | null {
  return items.find((item) => item.is_default)?.preset_id ?? null;
}
