import { useQuery } from '@tanstack/react-query';
import {
  getCourseEffectiveness,
  getEmployeeTrainingEffectiveness,
  getOverallTrainingEffectiveness,
  getRecommendationEffectiveness,
} from '@/lib/api-client';

export const trainingEffectivenessKeys = {
  all: ['training-effectiveness'] as const,
  overall: () => [...trainingEffectivenessKeys.all, 'overall'] as const,
  courses: () => [...trainingEffectivenessKeys.all, 'courses'] as const,
  recommendations: () => [...trainingEffectivenessKeys.all, 'recommendations'] as const,
  employee: (id: string) => [...trainingEffectivenessKeys.all, 'employee', id] as const,
};

export function useOverallTrainingEffectiveness() {
  return useQuery({
    queryKey: trainingEffectivenessKeys.overall(),
    queryFn: getOverallTrainingEffectiveness,
    staleTime: 60 * 1000,
  });
}

export function useCourseEffectiveness() {
  return useQuery({
    queryKey: trainingEffectivenessKeys.courses(),
    queryFn: getCourseEffectiveness,
    staleTime: 60 * 1000,
  });
}

export function useRecommendationEffectiveness() {
  return useQuery({
    queryKey: trainingEffectivenessKeys.recommendations(),
    queryFn: getRecommendationEffectiveness,
    staleTime: 60 * 1000,
  });
}

export function useEmployeeTrainingEffectiveness(employeeId?: string) {
  return useQuery({
    queryKey: trainingEffectivenessKeys.employee(employeeId || ''),
    queryFn: () => getEmployeeTrainingEffectiveness(employeeId!),
    enabled: !!employeeId,
    staleTime: 60 * 1000,
  });
}
