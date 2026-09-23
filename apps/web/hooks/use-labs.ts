import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  completeLabSession,
  getLabHint,
  getLabResult,
  getLabScenario,
  getLabScenarios,
  getLabSession,
  getMyLabSessions,
  startLabSession,
  submitLabAction,
} from '@/lib/api-client';
import type {
  LabActionEvaluationResult,
  LabActionSubmitRequest,
  LabCompleteResponse,
  LabHintResponse,
  LabResultDetail,
  LabScenarioDetail,
  LabScenarioSummary,
  LabSessionResponse,
} from '@pragya/types';

export const LAB_SCENARIOS_KEY = 'lab-scenarios';
export const LAB_SCENARIO_KEY = 'lab-scenario';
export const LAB_SESSION_KEY = 'lab-session';
export const LAB_RESULT_KEY = 'lab-result';

export function useLabScenarios(params?: {
  competencyId?: string;
  scenarioType?: string;
  difficulty?: string;
}) {
  return useQuery<LabScenarioSummary[]>({
    queryKey: [LAB_SCENARIOS_KEY, params],
    queryFn: () => getLabScenarios(params),
  });
}

export function useLabScenario(scenarioId?: string) {
  return useQuery<LabScenarioDetail>({
    queryKey: [LAB_SCENARIO_KEY, scenarioId],
    queryFn: () => (scenarioId ? getLabScenario(scenarioId) : Promise.reject('No scenario ID')),
    enabled: !!scenarioId,
  });
}

export function useLabSession(sessionId?: string) {
  return useQuery<LabSessionResponse>({
    queryKey: [LAB_SESSION_KEY, sessionId],
    queryFn: () => (sessionId ? getLabSession(sessionId) : Promise.reject('No session ID')),
    enabled: !!sessionId,
  });
}

export function useStartLabSession() {
  const queryClient = useQueryClient();
  return useMutation<LabSessionResponse, Error, string>({
    mutationFn: (scenarioId) => startLabSession(scenarioId),
    onSuccess: (session) => {
      queryClient.setQueryData([LAB_SESSION_KEY, session.id], session);
    },
  });
}

export function useSubmitLabAction(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<LabActionEvaluationResult, Error, LabActionSubmitRequest>({
    mutationFn: (req) => submitLabAction(sessionId, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [LAB_SESSION_KEY, sessionId] });
    },
  });
}

export function useCompleteLabSession(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<LabCompleteResponse, Error, void>({
    mutationFn: () => completeLabSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [LAB_RESULT_KEY, sessionId] });
      queryClient.invalidateQueries({ queryKey: [LAB_SESSION_KEY, sessionId] });
      queryClient.invalidateQueries({ queryKey: ['competencies'] });
      queryClient.invalidateQueries({ queryKey: ['skill-gaps'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
}

export function useLabResult(sessionId?: string) {
  return useQuery<LabResultDetail>({
    queryKey: [LAB_RESULT_KEY, sessionId],
    queryFn: () => (sessionId ? getLabResult(sessionId) : Promise.reject('No session ID')),
    enabled: !!sessionId,
  });
}

export function useLabHint(sessionId: string) {
  return useMutation<LabHintResponse, Error, number>({
    mutationFn: (stepNumber) => getLabHint(sessionId, stepNumber),
  });
}

export function useMyLabSessions(employeeId?: string) {
  return useQuery<LabSessionResponse[]>({
    queryKey: ['my-lab-sessions', employeeId],
    queryFn: () => getMyLabSessions(employeeId),
  });
}
