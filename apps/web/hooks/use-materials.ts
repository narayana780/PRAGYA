import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getMaterials,
  getMaterial,
  getMaterialStatus,
  getMaterialChunks,
  uploadMaterial,
  deleteMaterial,
} from '@/lib/api-client';

export const MATERIALS_QUERY_KEY = 'materials';
export const MATERIAL_QUERY_KEY = 'material';
export const MATERIAL_STATUS_QUERY_KEY = 'material-status';
export const MATERIAL_CHUNKS_QUERY_KEY = 'material-chunks';

/**
 * Hook to retrieve paginated learning materials for the current officer.
 * Automatically refetches every 3s if any material is in UPLOADED or PROCESSING state.
 */
export function useMaterials(skip = 0, limit = 20) {
  return useQuery({
    queryKey: [MATERIALS_QUERY_KEY, skip, limit],
    queryFn: () => getMaterials(skip, limit),
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return false;
      const hasPending = data.items.some(
        (m) => m.status === 'UPLOADED' || m.status === 'PROCESSING'
      );
      return hasPending ? 3000 : false;
    },
  });
}

/**
 * Hook to retrieve specific material details.
 */
export function useMaterial(id?: string) {
  return useQuery({
    queryKey: [MATERIAL_QUERY_KEY, id],
    queryFn: () => (id ? getMaterial(id) : Promise.reject('No ID provided')),
    enabled: !!id,
  });
}

/**
 * Hook to poll specific material status.
 */
export function useMaterialStatus(
  id?: string,
  options?: { enabled?: boolean; refetchInterval?: number | false }
) {
  return useQuery({
    queryKey: [MATERIAL_STATUS_QUERY_KEY, id],
    queryFn: () => (id ? getMaterialStatus(id) : Promise.reject('No ID provided')),
    enabled: !!id && (options?.enabled ?? true),
    refetchInterval: options?.refetchInterval ?? 2000,
  });
}

/**
 * Hook to retrieve extracted text chunks for an uploaded material.
 */
export function useMaterialChunks(id?: string) {
  return useQuery({
    queryKey: [MATERIAL_CHUNKS_QUERY_KEY, id],
    queryFn: () => (id ? getMaterialChunks(id) : Promise.reject('No ID provided')),
    enabled: !!id,
  });
}

/**
 * Mutation to upload a new learning material document.
 */
export function useUploadMaterial() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadMaterial(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MATERIALS_QUERY_KEY] });
    },
  });
}

/**
 * Mutation to delete an uploaded material.
 */
export function useDeleteMaterial() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteMaterial(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [MATERIALS_QUERY_KEY] });
    },
  });
}
