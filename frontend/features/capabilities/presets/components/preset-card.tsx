"use client";

import * as React from "react";
import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { PresetCardSurface } from "@/features/capabilities/presets/components/preset-card-surface";
import type { Preset } from "@/features/capabilities/presets/lib/preset-types";
import { useT } from "@/lib/i18n/client";

interface PresetCardProps {
  preset: Preset;
  isBusy?: boolean;
  onEdit: (preset: Preset) => void;
  onDelete: (preset: Preset) => void;
}

function isActionTarget(target: EventTarget | null): boolean {
  return (
    target instanceof HTMLElement &&
    Boolean(target.closest("[data-preset-card-action='true']"))
  );
}

export function PresetCard({
  preset,
  isBusy = false,
  onEdit,
  onDelete,
}: PresetCardProps) {
  const { t } = useT("translation");

  const handleOpenEdit = React.useCallback(() => {
    onEdit(preset);
  }, [onEdit, preset]);

  const handleCardClick = React.useCallback(
    (event: React.MouseEvent<HTMLDivElement>) => {
      if (isActionTarget(event.target)) {
        return;
      }

      handleOpenEdit();
    },
    [handleOpenEdit],
  );

  const handleCardKeyDown = React.useCallback(
    (event: React.KeyboardEvent<HTMLDivElement>) => {
      if (isActionTarget(event.target)) {
        return;
      }

      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        handleOpenEdit();
      }
    },
    [handleOpenEdit],
  );

  return (
    <PresetCardSurface
      preset={preset}
      onClick={handleCardClick}
      onKeyDown={handleCardKeyDown}
      meta={
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="size-8"
              data-preset-card-action="true"
            >
              <MoreHorizontal className="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" data-preset-card-action="true">
            <DropdownMenuItem onClick={handleOpenEdit}>
              <Pencil className="size-4" />
              <span>{t("common.edit")}</span>
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => onDelete(preset)}
              disabled={isBusy}
              className="text-destructive focus:text-destructive"
            >
              <Trash2 className="size-4" />
              <span>{t("common.delete")}</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      }
    />
  );
}
