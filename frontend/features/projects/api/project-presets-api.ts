import { apiClient, API_ENDPOINTS } from "@/services/api-client";
import type {
  PresetOrderUpdateInput,
  ProjectPreset,
  ProjectPresetAddInput,
} from "@/features/capabilities/presets/lib/preset-types";

export const projectPresetsService = {
  list: async (
    projectId: string,
    options?: { revalidate?: number },
  ): Promise<ProjectPreset[]> => {
    return apiClient.get<ProjectPreset[]>(
      API_ENDPOINTS.projectPresets(projectId),
      {
        next: { revalidate: options?.revalidate },
      },
    );
  },

  add: async (
    projectId: string,
    input: ProjectPresetAddInput,
  ): Promise<ProjectPreset> => {
    return apiClient.post<ProjectPreset>(
      API_ENDPOINTS.projectPresets(projectId),
      input,
    );
  },

  setDefault: async (
    projectId: string,
    presetId: number,
  ): Promise<ProjectPreset> => {
    return apiClient.put<ProjectPreset>(
      API_ENDPOINTS.projectPresetDefault(projectId, presetId),
    );
  },

  remove: async (
    projectId: string,
    presetId: number,
  ): Promise<Record<string, unknown>> => {
    return apiClient.delete<Record<string, unknown>>(
      API_ENDPOINTS.projectPreset(projectId, presetId),
    );
  },

  updateOrder: async (
    projectId: string,
    presetId: number,
    input: PresetOrderUpdateInput,
  ): Promise<ProjectPreset> => {
    return apiClient.patch<ProjectPreset>(
      API_ENDPOINTS.projectPresetOrder(projectId, presetId),
      input,
    );
  },
};
