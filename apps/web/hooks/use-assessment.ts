import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getAssessments,
  getAssessment,
  getAttempt,
  startAssessmentAttempt,
  recordAttemptResponse,
  completeAttempt,
  getEmployeeCompetencies,
  getCompetencyEvidence,
  getCompetencyHistory,
  submitSelfAssessment,
} from '@/lib/api-client';
import type {
  SelfAssessmentPayload,
} from '@pragya/types';

export const assessmentKeys = {
  all: ['assessments'] as const,
  lists: () => [...assessmentKeys.all, 'list'] as const,
  detail: (id: string) => [...assessmentKeys.all, 'detail', id] as const,
  attempts: ['attempts'] as const,
  attempt: (id: string) => [...assessmentKeys.attempts, id] as const,
  employeeCompetencies: (empId: string) => ['employee-competencies', empId] as const,
  competencyEvidence: (empId: string, compId: string) =>
    ['competency-evidence', empId, compId] as const,
  competencyHistory: (empId: string, compId: string) =>
    ['competency-history', empId, compId] as const,
};

export function useAssessments() {
  return useQuery({
    queryKey: assessmentKeys.lists(),
    queryFn: getAssessments,
    staleTime: 5 * 60 * 1000,
  });
}

export function useAssessment(id: string | null) {
  return useQuery({
    queryKey: assessmentKeys.detail(id || ''),
    queryFn: () => getAssessment(id!),
    enabled: Boolean(id),
    staleTime: 5 * 60 * 1000,
  });
}

export const useAssessmentDetails = useAssessment;

export function useAttempt(attemptId: string | null) {
  return useQuery({
    queryKey: assessmentKeys.attempt(attemptId || ''),
    queryFn: () => getAttempt(attemptId!),
    enabled: Boolean(attemptId),
    staleTime: 0, // Fresh data for active attempt
  });
}

export const useAssessmentAttempt = useAttempt;

export function useStartAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      assessmentId,
      employeeId,
    }: {
      assessmentId: string;
      employeeId: string;
    }) => startAssessmentAttempt(assessmentId, employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assessmentKeys.attempts });
    },
  });
}

export function useRecordResponse() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      attemptId,
      questionId,
      selectedOption,
      employeeId,
    }: {
      attemptId: string;
      questionId: string;
      selectedOption: number;
      employeeId?: string;
    }) =>
      recordAttemptResponse(attemptId, questionId, selectedOption, employeeId),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.attempt(vars.attemptId),
      });
    },
  });
}

export function useCompleteAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      attemptId,
      employeeId,
    }: {
      attemptId: string;
      employeeId?: string;
    }) => completeAttempt(attemptId, employeeId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assessmentKeys.attempts });
      queryClient.invalidateQueries({ queryKey: ['employee-competencies'] });
      queryClient.invalidateQueries({ queryKey: ['competency-evidence'] });
      queryClient.invalidateQueries({ queryKey: ['competency-history'] });
    },
  });
}

export function useEmployeeCompetencies(employeeId: string | undefined) {
  return useQuery({
    queryKey: assessmentKeys.employeeCompetencies(employeeId || ''),
    queryFn: () => getEmployeeCompetencies(employeeId!),
    enabled: Boolean(employeeId),
    staleTime: 60 * 1000,
  });
}

export function useCompetencyEvidence(
  employeeId: string | undefined,
  competencyId: string | null
) {
  return useQuery({
    queryKey: assessmentKeys.competencyEvidence(employeeId || '', competencyId || ''),
    queryFn: () => getCompetencyEvidence(employeeId!, competencyId!),
    enabled: Boolean(employeeId && competencyId),
    staleTime: 60 * 1000,
  });
}

export function useCompetencyHistory(
  employeeId: string | undefined,
  competencyId: string | null
) {
  return useQuery({
    queryKey: assessmentKeys.competencyHistory(employeeId || '', competencyId || ''),
    queryFn: () => getCompetencyHistory(employeeId!, competencyId!),
    enabled: Boolean(employeeId && competencyId),
    staleTime: 60 * 1000,
  });
}

export function useSubmitSelfAssessment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      employeeId,
      payload,
    }: {
      employeeId: string;
      payload: SelfAssessmentPayload;
    }) => submitSelfAssessment(employeeId, payload),
    onSuccess: (_, vars) => {
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.employeeCompetencies(vars.employeeId),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.competencyEvidence(
          vars.employeeId,
          vars.payload.competency_id
        ),
      });
      queryClient.invalidateQueries({
        queryKey: assessmentKeys.competencyHistory(
          vars.employeeId,
          vars.payload.competency_id
        ),
      });
    },
  });
}
