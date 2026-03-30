import test from "node:test";
import assert from "node:assert/strict";

import {
  getDefaultProjectPresetId,
  sortProjectPresets,
} from "./project-presets.ts";

const buildProjectPreset = (overrides: {
  project_preset_id: number;
  preset_id: number;
  sort_order: number;
  is_default?: boolean;
}) => ({
  project_preset_id: overrides.project_preset_id,
  project_id: "project-1",
  preset_id: overrides.preset_id,
  is_default: overrides.is_default ?? false,
  sort_order: overrides.sort_order,
  preset: {
    preset_id: overrides.preset_id,
    user_id: "user-1",
    name: `Preset ${overrides.preset_id}`,
    icon: "default" as const,
    browser_enabled: false,
    memory_enabled: false,
    skill_ids: [],
    mcp_server_ids: [],
    plugin_ids: [],
    subagent_configs: [],
    created_at: "",
    updated_at: "",
  },
  created_at: "",
  updated_at: "",
});

test("sortProjectPresets orders by sort_order then project_preset_id", () => {
  const sorted = sortProjectPresets([
    buildProjectPreset({ project_preset_id: 3, preset_id: 30, sort_order: 1 }),
    buildProjectPreset({ project_preset_id: 1, preset_id: 10, sort_order: 0 }),
    buildProjectPreset({ project_preset_id: 2, preset_id: 20, sort_order: 1 }),
  ]);

  assert.deepEqual(
    sorted.map((item) => item.project_preset_id),
    [1, 2, 3],
  );
});

test("getDefaultProjectPresetId returns default preset when present", () => {
  const presetId = getDefaultProjectPresetId([
    buildProjectPreset({ project_preset_id: 1, preset_id: 10, sort_order: 0 }),
    buildProjectPreset({
      project_preset_id: 2,
      preset_id: 20,
      sort_order: 1,
      is_default: true,
    }),
  ]);

  assert.equal(presetId, 20);
});

test("getDefaultProjectPresetId returns null when no default exists", () => {
  const presetId = getDefaultProjectPresetId([
    buildProjectPreset({ project_preset_id: 1, preset_id: 10, sort_order: 0 }),
  ]);

  assert.equal(presetId, null);
});
