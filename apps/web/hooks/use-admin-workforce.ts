import { useQuery } from '@tanstack/react-query';
import {
  getAdminEmployeeList,
  getDepartmentAnalytics,
  getDepartmentHeatmap,
  getRoleAnalytics,
  getWorkforceCompetencies,
  getWorkforceGaps,
  getWorkforceOverview,
  getWorkforceTrainingAnalytics,
} from '@/lib/api-client';

export const adminWorkforceKeys = {
  all: ['admin-workforce'] as const,
  overview: () => [...adminWorkforceKeys.all, 'overview'] as const,
  competencies: () => [...adminWorkforceKeys.all, 'competencies'] as const,
  departments: () => [...adminWorkforceKeys.all, 'departments'] as const,
  heatmap: () => [...adminWorkforceKeys.all, 'heatmap'] as const,
  gaps: () => [...adminWorkforceKeys.all, 'gaps'] as const,
  roles: () => [...adminWorkforceKeys.all, 'roles'] as const,
  training: () => [...adminWorkforceKeys.all, 'training'] as const,
  employees: () => [...adminWorkforceKeys.all, 'employees'] as const,
};

export function useWorkforceOverview() {
  return useQuery({
    queryKey: adminWorkforceKeys.overview(),
    queryFn: getWorkforceOverview,
    staleTime: 60 * 1000,
  });
}

export function useWorkforceCompetencies() {
  return useQuery({
    queryKey: adminWorkforceKeys.competencies(),
    queryFn: getWorkforceCompetencies,
    staleTime: 60 * 1000,
  });
}

export function useDepartmentAnalytics() {
  return useQuery({
    queryKey: adminWorkforceKeys.departments(),
    queryFn: getDepartmentAnalytics,
    staleTime: 60 * 1000,
  });
}

export function useDepartmentHeatmap() {
  return useQuery({
    queryKey: adminWorkforceKeys.heatmap(),
    queryFn: getDepartmentHeatmap,
    staleTime: 60 * 1000,
  });
}

export function useWorkforceGaps() {
  return useQuery({
    queryKey: adminWorkforceKeys.gaps(),
    queryFn: getWorkforceGaps,
    staleTime: 60 * 1000,
  });
}

export function useRoleAnalytics() {
  return useQuery({
    queryKey: adminWorkforceKeys.roles(),
    queryFn: getRoleAnalytics,
    staleTime: 60 * 1000,
  });
}

export function useWorkforceTrainingAnalytics() {
  return useQuery({
    queryKey: adminWorkforceKeys.training(),
    queryFn: getWorkforceTrainingAnalytics,
    staleTime: 60 * 1000,
  });
}

export function useAdminEmployeeList() {
  return useQuery({
    queryKey: adminWorkforceKeys.employees(),
    queryFn: getAdminEmployeeList,
    staleTime: 60 * 1000,
  });
}
