import { useCallback } from "react";

interface UseProjectActionsOptions {
  updateProject: (
    projectId: string,
    updates: Record<string, unknown>,
  ) => Promise<unknown>;
  deleteProject: (projectId: string) => Promise<void>;
}

interface UseProjectActionsResult {
  handleEditProject: (
    projectId: string,
    updates: Record<string, unknown>,
  ) => void;
  handleDeleteProject: (projectId: string) => Promise<void>;
}

/**
 * Hook to create stable callbacks for project edit and delete actions.
 */
export function useProjectActions({
  updateProject,
  deleteProject,
}: UseProjectActionsOptions): UseProjectActionsResult {
  const handleEditProject = useCallback(
    (projectId: string, updates: Record<string, unknown>) => {
      void updateProject(projectId, updates);
    },
    [updateProject],
  );

  const handleDeleteProject = useCallback(
    async (projectId: string) => {
      await deleteProject(projectId);
    },
    [deleteProject],
  );

  return {
    handleEditProject,
    handleDeleteProject,
  };
}
