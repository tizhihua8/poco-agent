export function resolveInitialPresetSelection(args: {
  initialPresetId: number | null;
  hasTouchedPreset: boolean;
  currentSelectedPresetId: number | null;
}): number | null {
  const { initialPresetId, hasTouchedPreset, currentSelectedPresetId } = args;

  if (initialPresetId === null || hasTouchedPreset) {
    return currentSelectedPresetId;
  }

  return initialPresetId;
}
