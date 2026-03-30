"use client";

import * as React from "react";
import {
  Check,
  ChevronDown,
  ChevronUp,
  Loader2,
  Plus,
  Sparkles,
  Trash2,
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { CapabilityDialogContent } from "@/features/capabilities/components/capability-dialog-content";
import { presetsService } from "@/features/capabilities/presets/api/presets-api";
import { PRESET_ICON_MAP } from "@/features/capabilities/presets/lib/preset-visuals";
import type {
  Preset,
  ProjectPreset,
} from "@/features/capabilities/presets/lib/preset-types";
import { projectPresetsService } from "@/features/projects/api/project-presets-api";
import { sortProjectPresets } from "@/features/projects/lib/project-presets";
import { Dialog, DialogFooter } from "@/components/ui/dialog";
import { useT } from "@/lib/i18n/client";

interface ProjectSettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
  projectName: string;
  onProjectPresetsChange?: (items: ProjectPreset[]) => void;
}

export function ProjectSettingsDialog({
  open,
  onOpenChange,
  projectId,
  projectName,
  onProjectPresetsChange,
}: ProjectSettingsDialogProps) {
  const { t } = useT("translation");
  const [allPresets, setAllPresets] = React.useState<Preset[]>([]);
  const [projectPresets, setProjectPresets] = React.useState<ProjectPreset[]>(
    [],
  );
  const [selectedPresetId, setSelectedPresetId] = React.useState<string>("none");
  const [isLoading, setIsLoading] = React.useState(false);
  const [actionKey, setActionKey] = React.useState<string | null>(null);

  const availablePresets = React.useMemo(() => {
    const boundIds = new Set(projectPresets.map((item) => item.preset_id));
    return allPresets.filter((preset) => !boundIds.has(preset.preset_id));
  }, [allPresets, projectPresets]);

  const publishProjectPresets = React.useCallback(
    (items: ProjectPreset[]) => {
      const sorted = sortProjectPresets(items);
      setProjectPresets(sorted);
      onProjectPresetsChange?.(sorted);
    },
    [onProjectPresetsChange],
  );

  const refresh = React.useCallback(async () => {
    setIsLoading(true);
    try {
      const [presets, attached] = await Promise.all([
        presetsService.listPresets({ revalidate: 0 }),
        projectPresetsService.list(projectId, { revalidate: 0 }),
      ]);
      setAllPresets(presets);
      publishProjectPresets(attached);
    } catch (error) {
      console.error("[ProjectSettingsDialog] Failed to fetch presets", error);
      toast.error(t("project.settingsPanel.presets.toasts.loadError"));
    } finally {
      setIsLoading(false);
    }
  }, [projectId, publishProjectPresets, t]);

  React.useEffect(() => {
    if (!open) return;
    void refresh();
  }, [open, refresh]);

  React.useEffect(() => {
    if (!open) return;
    setSelectedPresetId("none");
  }, [open, availablePresets.length]);

  const handleAddPreset = React.useCallback(async () => {
    if (selectedPresetId === "none") return;
    setActionKey(`add:${selectedPresetId}`);
    try {
      const created = await projectPresetsService.add(projectId, {
        preset_id: Number(selectedPresetId),
      });
      publishProjectPresets([...projectPresets, created]);
      setSelectedPresetId("none");
      toast.success(t("project.settingsPanel.presets.toasts.added"));
    } catch (error) {
      console.error("[ProjectSettingsDialog] Failed to add preset", error);
      toast.error(t("project.settingsPanel.presets.toasts.addFailed"));
    } finally {
      setActionKey(null);
    }
  }, [projectId, projectPresets, publishProjectPresets, selectedPresetId, t]);

  const handleSetDefault = React.useCallback(
    async (presetId: number) => {
      setActionKey(`default:${presetId}`);
      try {
        const updated = await projectPresetsService.setDefault(projectId, presetId);
        publishProjectPresets(
          projectPresets.map((item) =>
            item.preset_id === presetId
              ? updated
              : { ...item, is_default: false },
          ),
        );
        toast.success(t("project.settingsPanel.presets.toasts.defaultUpdated"));
      } catch (error) {
        console.error("[ProjectSettingsDialog] Failed to set default", error);
        toast.error(t("project.settingsPanel.presets.toasts.defaultFailed"));
      } finally {
        setActionKey(null);
      }
    },
    [projectId, projectPresets, publishProjectPresets, t],
  );

  const handleRemove = React.useCallback(
    async (presetId: number) => {
      setActionKey(`remove:${presetId}`);
      try {
        await projectPresetsService.remove(projectId, presetId);
        publishProjectPresets(
          projectPresets.filter((item) => item.preset_id !== presetId),
        );
        toast.success(t("project.settingsPanel.presets.toasts.removed"));
      } catch (error) {
        console.error("[ProjectSettingsDialog] Failed to remove preset", error);
        toast.error(t("project.settingsPanel.presets.toasts.removeFailed"));
      } finally {
        setActionKey(null);
      }
    },
    [projectId, projectPresets, publishProjectPresets, t],
  );

  const handleMove = React.useCallback(
    async (presetId: number, direction: -1 | 1) => {
      const currentIndex = projectPresets.findIndex(
        (item) => item.preset_id === presetId,
      );
      const targetIndex = currentIndex + direction;
      if (currentIndex < 0 || targetIndex < 0 || targetIndex >= projectPresets.length) {
        return;
      }

      const current = projectPresets[currentIndex];
      const target = projectPresets[targetIndex];
      setActionKey(`move:${presetId}`);
      try {
        const [updatedCurrent, updatedTarget] = await Promise.all([
          projectPresetsService.updateOrder(projectId, current.preset_id, {
            sort_order: target.sort_order,
          }),
          projectPresetsService.updateOrder(projectId, target.preset_id, {
            sort_order: current.sort_order,
          }),
        ]);

        publishProjectPresets(
          projectPresets.map((item) => {
            if (item.preset_id === updatedCurrent.preset_id) return updatedCurrent;
            if (item.preset_id === updatedTarget.preset_id) return updatedTarget;
            return item;
          }),
        );
      } catch (error) {
        console.error("[ProjectSettingsDialog] Failed to reorder presets", error);
        toast.error(t("project.settingsPanel.presets.toasts.orderFailed"));
      } finally {
        setActionKey(null);
      }
    },
    [projectId, projectPresets, publishProjectPresets, t],
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <CapabilityDialogContent
        title={t("project.settingsPanel.dialogTitle", { name: projectName })}
        description={t("project.settingsPanel.dialogDescription")}
        maxWidth="48rem"
        maxHeight="80dvh"
        desktopMaxHeight="86dvh"
        footer={
          <DialogFooter>
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              {t("common.close")}
            </Button>
          </DialogFooter>
        }
      >
        <div className="space-y-5">
          <section className="space-y-3 rounded-2xl border border-border/60 p-4">
            <div className="space-y-1">
              <h3 className="text-sm font-medium text-foreground">
                {t("project.settingsPanel.presets.title")}
              </h3>
              <p className="text-xs text-muted-foreground">
                {t("project.settingsPanel.presets.description")}
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="flex-1 space-y-2">
                <Label>{t("project.settingsPanel.presets.addLabel")}</Label>
                <Select
                  value={selectedPresetId}
                  onValueChange={setSelectedPresetId}
                  disabled={availablePresets.length === 0 || isLoading}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue
                      placeholder={t(
                        "project.settingsPanel.presets.addPlaceholder",
                      )}
                    />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">
                      {t("project.settingsPanel.presets.addPlaceholder")}
                    </SelectItem>
                    {availablePresets.map((preset) => (
                      <SelectItem
                        key={preset.preset_id}
                        value={String(preset.preset_id)}
                      >
                        {preset.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={() => void handleAddPreset()}
                disabled={
                  selectedPresetId === "none" || actionKey?.startsWith("add:")
                }
              >
                <Plus className="mr-2 size-4" />
                {t("project.settingsPanel.presets.add")}
              </Button>
            </div>
          </section>

          <section className="space-y-3">
            {isLoading ? (
              <div className="flex min-h-32 items-center justify-center rounded-2xl border border-dashed border-border/60 text-sm text-muted-foreground">
                <Loader2 className="mr-2 size-4 animate-spin" />
                {t("project.settingsPanel.presets.loading")}
              </div>
            ) : projectPresets.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-border/60 px-4 py-10 text-center text-sm text-muted-foreground">
                {t("project.settingsPanel.presets.empty")}
              </div>
            ) : (
              projectPresets.map((item, index) => {
                const iconName =
                  item.preset.icon in PRESET_ICON_MAP
                    ? item.preset.icon
                    : "default";

                return (
                  <div
                    key={item.project_preset_id}
                    className="rounded-2xl border border-border/60 bg-card p-4"
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className="flex size-10 shrink-0 items-center justify-center rounded-xl border border-border/60 bg-muted/40"
                        style={{ color: item.preset.color || "var(--primary)" }}
                      >
                        {React.createElement(PRESET_ICON_MAP[iconName], {
                          className: "size-4",
                        })}
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="truncate text-sm font-medium text-foreground">
                            {item.preset.name}
                          </p>
                          {item.is_default ? (
                            <Badge variant="secondary">
                              {t("project.settingsPanel.presets.default")}
                            </Badge>
                          ) : null}
                        </div>
                        <p className="mt-1 text-xs text-muted-foreground">
                          {item.preset.description?.trim() ||
                            t("project.settingsPanel.presets.emptyDescription")}
                        </p>
                      </div>

                      <div className="flex shrink-0 items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8"
                          disabled={index === 0 || actionKey === `move:${item.preset_id}`}
                          onClick={() => void handleMove(item.preset_id, -1)}
                        >
                          <ChevronUp className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8"
                          disabled={
                            index === projectPresets.length - 1 ||
                            actionKey === `move:${item.preset_id}`
                          }
                          onClick={() => void handleMove(item.preset_id, 1)}
                        >
                          <ChevronDown className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8"
                          disabled={item.is_default || actionKey === `default:${item.preset_id}`}
                          onClick={() => void handleSetDefault(item.preset_id)}
                        >
                          <Check className="size-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="size-8 text-destructive"
                          disabled={actionKey === `remove:${item.preset_id}`}
                          onClick={() => void handleRemove(item.preset_id)}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-muted-foreground">
                      <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1">
                        <Sparkles className="size-3" />
                        {t("project.settingsPanel.presets.stats.skills", {
                          count: item.preset.skill_ids.length,
                        })}
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1">
                        {t("project.settingsPanel.presets.stats.mcp", {
                          count: item.preset.mcp_server_ids.length,
                        })}
                      </span>
                      <span className="inline-flex items-center gap-1 rounded-full bg-muted px-2.5 py-1">
                        {t("project.settingsPanel.presets.stats.plugins", {
                          count: item.preset.plugin_ids.length,
                        })}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </section>
        </div>
      </CapabilityDialogContent>
    </Dialog>
  );
}
