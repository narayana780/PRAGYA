import { useQuery } from '@tanstack/react-query';
import {
  getCompetencyCapacityForecast,
  getDepartmentCapacityForecast,
  getEmployeePlanningDrilldown,
  getPlanningRecommendations,
  getRoleCapacityForecast,
  getWorkforceCapacityForecast,
  getWorkforcePlanningOverview,
  getWorkforcePlanningTrends,
} from '@/lib/api-client';

export function useWorkforcePlanningOverview() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'overview'],
    queryFn: getWorkforcePlanningOverview,
    staleTime: 60 * 1000,
  });
}

export function useWorkforcePlanningTrends() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'trends'],
    queryFn: getWorkforcePlanningTrends,
    staleTime: 60 * 1000,
  });
}

export function useWorkforceCapacityForecast() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'forecast'],
    queryFn: getWorkforceCapacityForecast,
    staleTime: 60 * 1000,
  });
}

export function useCompetencyCapacityForecast() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'competencies'],
    queryFn: getCompetencyCapacityForecast,
    staleTime: 60 * 1000,
  });
}

export function useRoleCapacityForecast() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'roles'],
    queryFn: getRoleCapacityForecast,
    staleTime: 60 * 1000,
  });
}

export function useDepartmentCapacityForecast() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'departments'],
    queryFn: getDepartmentCapacityForecast,
    staleTime: 60 * 1000,
  });
}

export function usePlanningRecommendations() {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'recommendations'],
    queryFn: getPlanningRecommendations,
    staleTime: 60 * 1000,
  });
}

export function useEmployeePlanningDrilldown(employeeId: string) {
  return useQuery({
    queryKey: ['admin', 'workforce', 'planning', 'employee', employeeId],
    queryFn: () => getEmployeePlanningDrilldown(employeeId),
    enabled: Boolean(employeeId),
    staleTime: 60 * 1000,
  });
}
