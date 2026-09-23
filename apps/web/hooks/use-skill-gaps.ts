import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getEmployeeSkillGaps,
  getSkillGapSummary,
  getSkillGapDetail,
  recalculateEmployeeSkillGaps,
  type SkillGapFilterParams,
} from '@/lib/api-client';

export function useEmployeeSkillGaps(
  employeeId?: string,
  params?: SkillGapFilterParams
) {
  return useQuery({
    queryKey: [
      'skill-gaps',
      employeeId,
      params?.priority,
      params?.domain,
      params?.competency,
      params?.confidence,
    ],
    queryFn: () =>
      employeeId
        ? getEmployeeSkillGaps(employeeId, params)
        : Promise.reject('No employee ID'),
    enabled: !!employeeId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useSkillGapSummary(employeeId?: string) {
  return useQuery({
    queryKey: ['skill-gap-summary', employeeId],
    queryFn: () =>
      employeeId
        ? getSkillGapSummary(employeeId)
        : Promise.reject('No employee ID'),
    enabled: !!employeeId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useSkillGapDetail(
  employeeId?: string,
  competencyId?: string
) {
  return useQuery({
    queryKey: ['skill-gap-detail', employeeId, competencyId],
    queryFn: () =>
      employeeId && competencyId
        ? getSkillGapDetail(employeeId, competencyId)
        : Promise.reject('Missing IDs'),
    enabled: !!employeeId && !!competencyId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useRecalculateSkillGaps(employeeId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () =>
      employeeId
        ? recalculateEmployeeSkillGaps(employeeId)
        : Promise.reject('No employee ID'),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skill-gaps', employeeId] });
      queryClient.invalidateQueries({ queryKey: ['skill-gap-summary', employeeId] });
      queryClient.invalidateQueries({ queryKey: ['employee-competencies', employeeId] });
    },
  });
}
