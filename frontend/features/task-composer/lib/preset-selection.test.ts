import test from "node:test";
import assert from "node:assert/strict";

import { resolveInitialPresetSelection } from "./preset-selection.ts";

test("resolveInitialPresetSelection applies initial preset before user interaction", () => {
  const selected = resolveInitialPresetSelection({
    initialPresetId: 7,
    hasTouchedPreset: false,
    currentSelectedPresetId: null,
  });

  assert.equal(selected, 7);
});

test("resolveInitialPresetSelection keeps current selection after user interaction", () => {
  const selected = resolveInitialPresetSelection({
    initialPresetId: 7,
    hasTouchedPreset: true,
    currentSelectedPresetId: 9,
  });

  assert.equal(selected, 9);
});

test("resolveInitialPresetSelection clears selection when default preset is removed", () => {
  const selected = resolveInitialPresetSelection({
    initialPresetId: null,
    hasTouchedPreset: false,
    currentSelectedPresetId: 5,
  });

  assert.equal(selected, null);
});
