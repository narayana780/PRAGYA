import { useQuery } from '@tanstack/react-query';
import {
  getEmployeePerformance,
  getEmployeeTimeline,
} from '@/lib/api-client';

export const performanceKeys = {
  all: ['employee-performance'] as const,
  performance: (empId: string) => [...performanceKeys.all, 'detail', empId] as const,
  timeline: (empId: string, eventType?: string, limit?: number) =>
    [...performanceKeys.all, 'timeline', empId, eventType || 'ALL', limit || 100] as const,
};

export function useEmployeePerformance(employeeId?: string) {
  return useQuery({
    queryKey: performanceKeys.performance(employeeId || ''),
    queryFn: () =>
      employeeId
        ? getEmployeePerformance(employeeId)
        : Promise.reject(new Error('No employee ID provided')),
    enabled: Boolean(employeeId),
    staleTime: 60 * 1000,
  });
}

export function useEmployeePerformanceTimeline(
  employeeId?: string,
  eventType?: string,
  limit?: number
) {
  return useQuery({
    queryKey: performanceKeys.timeline(employeeId || '', eventType, limit),
    queryFn: () =>
      employeeId
        ? getEmployeeTimeline(employeeId, eventType, limit)
        : Promise.reject(new Error('No employee ID provided')),
    enabled: Boolean(employeeId),
    staleTime: 60 * 1000,
  });
}
