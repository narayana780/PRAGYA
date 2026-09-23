import { useQuery } from '@tanstack/react-query';
import { getDepartments, getJobRoles } from '@/lib/api-client';

export function useDepartments() {
  return useQuery({
    queryKey: ['departments'],
    queryFn: getDepartments,
    staleTime: 10 * 60 * 1000, // 10 minutes cache for stable reference data
  });
}

export function useJobRoles() {
  return useQuery({
    queryKey: ['job-roles'],
    queryFn: getJobRoles,
    staleTime: 10 * 60 * 1000,
  });
}
