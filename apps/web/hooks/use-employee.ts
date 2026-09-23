import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getCurrentEmployee,
  getEmployee,
  getEmployeeTrainingHistory,
  updateEmployee,
} from '@/lib/api-client';
import type { EmployeeUpdatePayload } from '@pragya/types';

export function useCurrentEmployee() {
  return useQuery({
    queryKey: ['employee', 'me'],
    queryFn: getCurrentEmployee,
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployee(id?: string) {
  return useQuery({
    queryKey: ['employee', id],
    queryFn: () => (id ? getEmployee(id) : Promise.reject('No ID provided')),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useEmployeeTrainingHistory(employeeId?: string) {
  return useQuery({
    queryKey: ['employee', employeeId, 'training-history'],
    queryFn: () =>
      employeeId
        ? getEmployeeTrainingHistory(employeeId)
        : Promise.reject('No employee ID'),
    enabled: !!employeeId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useUpdateEmployee() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: EmployeeUpdatePayload;
    }) => updateEmployee(id, payload),
    onSuccess: (updatedEmployee) => {
      queryClient.setQueryData(['employee', 'me'], updatedEmployee);
      queryClient.setQueryData(['employee', updatedEmployee.id], updatedEmployee);
      queryClient.invalidateQueries({ queryKey: ['employee', 'me'] });
      queryClient.invalidateQueries({ queryKey: ['employee', updatedEmployee.id] });
    },
  });
}
