import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  generateQuiz,
  getQuizzes,
  getQuiz,
  startQuizAttempt,
  submitQuizAnswer,
  completeQuizAttempt,
  getQuizResult,
  getQuizReview,
  listQuizAttempts,
} from '@/lib/api-client';
import type {
  GenerateQuizRequest,
  SubmitAnswerRequest,
  QuizSummary,
  QuizDetail,
  QuizAttemptSummary,
  AnswerResponse,
  QuizResultResponse,
  QuizReviewResponse,
} from '@pragya/types';

export const QUIZZES_KEY = 'quizzes';
export const QUIZ_KEY = 'quiz';
export const QUIZ_RESULT_KEY = 'quiz-result';
export const QUIZ_REVIEW_KEY = 'quiz-review';

export function useQuizzes(limit = 50) {
  return useQuery<QuizSummary[]>({
    queryKey: [QUIZZES_KEY, limit],
    queryFn: () => getQuizzes(limit),
  });
}

export function useQuiz(quizId?: string) {
  return useQuery<QuizDetail>({
    queryKey: [QUIZ_KEY, quizId],
    queryFn: () => (quizId ? getQuiz(quizId) : Promise.reject('No quiz ID')),
    enabled: !!quizId,
  });
}

export function useGenerateQuiz() {
  const queryClient = useQueryClient();
  return useMutation<QuizDetail, Error, GenerateQuizRequest>({
    mutationFn: (req) => generateQuiz(req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUIZZES_KEY] });
    },
  });
}

export function useStartQuizAttempt() {
  return useMutation<QuizAttemptSummary, Error, string>({
    mutationFn: (quizId) => startQuizAttempt(quizId),
  });
}

export function useSubmitQuizAnswer(attemptId: string) {
  return useMutation<AnswerResponse, Error, SubmitAnswerRequest>({
    mutationFn: (req) => submitQuizAnswer(attemptId, req),
  });
}

export function useCompleteQuizAttempt(attemptId: string) {
  const queryClient = useQueryClient();
  return useMutation<QuizResultResponse, Error, void>({
    mutationFn: () => completeQuizAttempt(attemptId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUIZ_RESULT_KEY, attemptId] });
      queryClient.invalidateQueries({ queryKey: [QUIZ_REVIEW_KEY, attemptId] });
      queryClient.invalidateQueries({ queryKey: [QUIZZES_KEY] });
    },
  });
}

export function useQuizResult(attemptId?: string) {
  return useQuery<QuizResultResponse>({
    queryKey: [QUIZ_RESULT_KEY, attemptId],
    queryFn: () => (attemptId ? getQuizResult(attemptId) : Promise.reject('No attempt ID')),
    enabled: !!attemptId,
  });
}

export function useQuizReview(attemptId?: string) {
  return useQuery<QuizReviewResponse>({
    queryKey: [QUIZ_REVIEW_KEY, attemptId],
    queryFn: () => (attemptId ? getQuizReview(attemptId) : Promise.reject('No attempt ID')),
    enabled: !!attemptId,
  });
}

export interface RecentQuizScore {
  score: number;
  percentage: number;
  quizTitle: string;
  completedAt: string;
}

export function useRecentQuizScore() {
  const { data: quizzes = [], isLoading: isLoadingQuizzes } = useQuizzes(10);

  return useQuery<RecentQuizScore | null>({
    queryKey: ['recent-quiz-score', quizzes.map((q) => q.id)],
    queryFn: async () => {
      if (!quizzes.length) return null;
      const attemptPromises = quizzes.slice(0, 5).map(async (quiz) => {
        try {
          const attempts = await listQuizAttempts(quiz.id);
          return attempts.filter((a) => a.status === 'COMPLETED');
        } catch {
          return [];
        }
      });
      const results = await Promise.all(attemptPromises);
      const allCompleted = results.flat();
      if (!allCompleted.length) return null;

      allCompleted.sort((a, b) => {
        const dateA = a.completed_at ? new Date(a.completed_at).getTime() : 0;
        const dateB = b.completed_at ? new Date(b.completed_at).getTime() : 0;
        return dateB - dateA;
      });

      const latest = allCompleted[0];
      return {
        score: latest.score ?? 0,
        percentage: latest.percentage ?? 0,
        quizTitle: latest.quiz_title || 'AI Assessment Quiz',
        completedAt: latest.completed_at || '',
      };
    },
    enabled: !isLoadingQuizzes && quizzes.length > 0,
  });
}

