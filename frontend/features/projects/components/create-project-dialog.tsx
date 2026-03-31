"use client";

import * as React from "react";
import { useT } from "@/lib/i18n/client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateProject: (data: { name: string; description?: string }) => void;
}

/**
 * Dialog for creating a new project
 * Replaces the native prompt() function
 */
export function CreateProjectDialog({
  open,
  onOpenChange,
  onCreateProject,
}: CreateProjectDialogProps) {
  const { t } = useT("translation");
  const [projectName, setProjectName] = React.useState("");
  const [projectDescription, setProjectDescription] = React.useState("");
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Reset input when dialog opens
  React.useEffect(() => {
    if (open) {
      setProjectName("");
      setProjectDescription("");
      // Focus input after dialog opens
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [open]);

  if (!mounted) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (projectName.trim()) {
      onCreateProject({
        name: projectName.trim(),
        description: projectDescription.trim() || undefined,
      });
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle>{t("sidebar.newProject")}</DialogTitle>
            <DialogDescription>
              {t("sidebar.newProjectPrompt")}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="project-name">{t("sidebar.projects")}</Label>
              <Input
                ref={inputRef}
                id="project-name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder={t("sidebar.newProject")}
                onKeyDown={(e) => {
                  if (e.key === "Escape") {
                    onOpenChange(false);
                  }
                }}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="project-description">
                {t("project.descriptionLabel")}
              </Label>
              <Textarea
                id="project-description"
                value={projectDescription}
                onChange={(e) => setProjectDescription(e.target.value)}
                placeholder={t("project.detail.descriptionPlaceholder")}
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              {t("projectDialogs.cancel")}
            </Button>
            <Button type="submit" disabled={!projectName.trim()}>
              {t("projectDialogs.create")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
