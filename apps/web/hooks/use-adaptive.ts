import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createAdaptiveSession,
  getAdaptiveSession,
  submitAdaptiveResponse,
  completeAdaptiveSession,
  getAdaptiveResult,
} from '@/lib/api-client';
import type {
  AdaptiveSessionCreateRequest,
  AdaptiveSessionSummary,
  AdaptiveSubmitAnswerRequest,
  AdaptiveSubmitAnswerResponse,
  RecalibrationResultResponse,
} from '@pragya/types';

export const ADAPTIVE_SESSION_KEY = 'adaptive-session';
export const ADAPTIVE_QUESTION_KEY = 'adaptive-question';
export const ADAPTIVE_RESULT_KEY = 'adaptive-result';

export function useAdaptiveSession(sessionId?: string) {
  return useQuery<AdaptiveSessionSummary>({
    queryKey: [ADAPTIVE_SESSION_KEY, sessionId],
    queryFn: () => (sessionId ? getAdaptiveSession(sessionId) : Promise.reject('No session ID')),
    enabled: !!sessionId,
  });
}

export function useCreateAdaptiveSession() {
  const queryClient = useQueryClient();
  return useMutation<AdaptiveSessionSummary, Error, AdaptiveSessionCreateRequest>({
    mutationFn: (req) => createAdaptiveSession(req),
    onSuccess: (session) => {
      queryClient.setQueryData([ADAPTIVE_SESSION_KEY, session.id], session);
    },
  });
}

export function useSubmitAdaptiveResponse(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<AdaptiveSubmitAnswerResponse, Error, AdaptiveSubmitAnswerRequest>({
    mutationFn: (req) => submitAdaptiveResponse(sessionId, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ADAPTIVE_SESSION_KEY, sessionId] });
    },
  });
}

export function useCompleteAdaptiveSession(sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation<RecalibrationResultResponse, Error, void>({
    mutationFn: () => completeAdaptiveSession(sessionId),
    onSuccess: (result) => {
      queryClient.setQueryData([ADAPTIVE_RESULT_KEY, sessionId], result);
      queryClient.invalidateQueries({ queryKey: [ADAPTIVE_SESSION_KEY, sessionId] });
      // Invalidate competency and gaps queries so the rest of the application reflects the recalibration
      queryClient.invalidateQueries({ queryKey: ['competencies'] });
      queryClient.invalidateQueries({ queryKey: ['skill-gaps'] });
      queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
}

export function useAdaptiveResult(sessionId?: string) {
  return useQuery<RecalibrationResultResponse>({
    queryKey: [ADAPTIVE_RESULT_KEY, sessionId],
    queryFn: () => (sessionId ? getAdaptiveResult(sessionId) : Promise.reject('No session ID')),
    enabled: !!sessionId,
  });
}
