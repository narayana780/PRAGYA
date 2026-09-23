import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getProviders,
  getLearningItems,
  getLearningItem,
  getRecommendations,
  getRecommendation,
  generateRecommendations,
  startRecommendation,
  dismissRecommendation,
  getLearningPath,
  generateLearningPath,
  type LearningItemsQueryParams,
  type RecommendationQueryParams,
} from '@/lib/api-client';

export function useProviders() {
  return useQuery({
    queryKey: ['providers'],
    queryFn: () => getProviders(),
    staleTime: 10 * 60 * 1000, // 10 minutes cache
  });
}

export function useLearningItems(params?: LearningItemsQueryParams) {
  return useQuery({
    queryKey: [
      'learning-items',
      params?.search,
      params?.provider,
      params?.competency_id,
      params?.difficulty,
      params?.format,
      params?.skip,
      params?.limit,
    ],
    queryFn: () => getLearningItems(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useLearningItem(id?: string) {
  return useQuery({
    queryKey: ['learning-item', id],
    queryFn: () => (id ? getLearningItem(id) : Promise.reject('No ID provided')),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRecommendations(
  employeeId?: string,
  params?: RecommendationQueryParams
) {
  return useQuery({
    queryKey: [
      'recommendations',
      employeeId,
      params?.priority,
      params?.provider,
      params?.competency,
      params?.type,
      params?.language,
    ],
    queryFn: () =>
      employeeId
        ? getRecommendations(employeeId, params)
        : Promise.reject('No employee ID'),
    enabled: !!employeeId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useRecommendation(
  employeeId?: string,
  recommendationId?: string
) {
  return useQuery({
    queryKey: ['recommendation', employeeId, recommendationId],
    queryFn: () =>
      employeeId && recommendationId
        ? getRecommendation(employeeId, recommendationId)
        : Promise.reject('Missing IDs'),
    enabled: !!employeeId && !!recommendationId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useLearningPath(employeeId?: string) {
  return useQuery({
    queryKey: ['learning-path', employeeId],
    queryFn: () =>
      employeeId ? getLearningPath(employeeId) : Promise.reject('No employee ID'),
    enabled: !!employeeId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useGenerateRecommendations(employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      employeeId
        ? generateRecommendations(employeeId)
        : Promise.reject('No employee ID'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', employeeId] });
      queryClient.invalidateQueries({ queryKey: ['learning-path', employeeId] });
    },
  });
}

export function useGenerateLearningPath(employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      employeeId
        ? generateLearningPath(employeeId)
        : Promise.reject('No employee ID'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-path', employeeId] });
    },
  });
}

export function useStartRecommendation(employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recommendationId: string) =>
      employeeId
        ? startRecommendation(employeeId, recommendationId)
        : Promise.reject('No employee ID'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', employeeId] });
      queryClient.invalidateQueries({ queryKey: ['learning-path', employeeId] });
    },
  });
}

export function useDismissRecommendation(employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recommendationId: string) =>
      employeeId
        ? dismissRecommendation(employeeId, recommendationId)
        : Promise.reject('No employee ID'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recommendations', employeeId] });
      queryClient.invalidateQueries({ queryKey: ['learning-path', employeeId] });
    },
  });
}
