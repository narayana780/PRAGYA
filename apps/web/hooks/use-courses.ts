import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getCourseCurriculum,
  getCourseProgress,
  updateCourseResourceProgress,
  submitCourseKnowledgeCheck,
  submitCourseAssignment,
  submitCourseFinalAssessment,
  completeCourse,
  recalibrateCourse,
  launchCourseResource,
  syncCourseResource,
  syncCourseIgot,
} from '@/lib/api-client';
import type {
  CourseProgressResponse,
  CourseResourceProgressPayload,
  CourseResourceProgressItem,
  KnowledgeCheckResultResponse,
  AssignmentResultResponse,
  FinalAssessmentResultResponse,
  CourseCompleteResponse,
  RecalibrateCourseResponse,
  ResourceLaunchResponse,
  ProviderSyncResponse,
} from '@pragya/types';

export const COURSE_PROGRESS_KEY = 'course-progress';
export const COURSE_CURRICULUM_KEY = 'course-curriculum';

export function useCourseCurriculum(courseId?: string) {
  return useQuery({
    queryKey: [COURSE_CURRICULUM_KEY, courseId],
    queryFn: () => (courseId ? getCourseCurriculum(courseId) : Promise.reject('No course ID')),
    enabled: !!courseId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCourseProgress(courseId?: string, employeeId?: string) {
  return useQuery<CourseProgressResponse>({
    queryKey: [COURSE_PROGRESS_KEY, courseId, employeeId],
    queryFn: () =>
      courseId && employeeId
        ? getCourseProgress(courseId, employeeId)
        : Promise.reject('Missing course ID or employee ID'),
    enabled: !!courseId && !!employeeId,
    staleTime: 0,
    refetchOnWindowFocus: true,
  });
}

export function useUpdateResourceProgress(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<
    CourseResourceProgressItem,
    Error,
    { resourceId: string; payload: CourseResourceProgressPayload }
  >({
    mutationFn: ({ resourceId, payload }) =>
      updateCourseResourceProgress(courseId, resourceId, payload, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
    },
  });
}

export function useSubmitKnowledgeCheck(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<
    KnowledgeCheckResultResponse,
    Error,
    { moduleId: number; answers: Record<string, number> }
  >({
    mutationFn: ({ moduleId, answers }) =>
      submitCourseKnowledgeCheck(courseId, moduleId, answers, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
    },
  });
}

export function useSubmitAssignment(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<
    AssignmentResultResponse,
    Error,
    {
      moduleId: number;
      payload: {
        sampling_method: string;
        allocation_strategy: string;
        non_response_buffer: string;
        justification_code: string;
      };
    }
  >({
    mutationFn: ({ moduleId, payload }) =>
      submitCourseAssignment(courseId, moduleId, payload, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.invalidateQueries({ queryKey: ['competencies'] });
    },
  });
}

export function useSubmitFinalAssessment(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<FinalAssessmentResultResponse, Error, Record<string, number>>({
    mutationFn: (answers) => submitCourseFinalAssessment(courseId, answers, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.invalidateQueries({ queryKey: ['competencies'] });
    },
  });
}

export function useCompleteCourse(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<CourseCompleteResponse, Error, void>({
    mutationFn: () => completeCourse(courseId, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.invalidateQueries({ queryKey: ['competencies'] });
      await queryClient.invalidateQueries({ queryKey: ['skill-gaps'] });
      await queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
}

export function useRecalibrateCourse(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<RecalibrateCourseResponse, Error, void>({
    mutationFn: () => recalibrateCourse(courseId, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['competencies'] });
      await queryClient.invalidateQueries({ queryKey: ['skill-gaps'] });
      await queryClient.invalidateQueries({ queryKey: ['recommendations'] });
    },
  });
}

export function useLaunchResource(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<ResourceLaunchResponse, Error, string>({
    mutationFn: (resourceId: string) => launchCourseResource(courseId, resourceId, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
    },
  });
}

export function useSyncResource(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<ProviderSyncResponse, Error, string>({
    mutationFn: (resourceId: string) => syncCourseResource(courseId, resourceId, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
    },
  });
}

export function useSyncIgotCourse(courseId: string, employeeId?: string) {
  const queryClient = useQueryClient();
  return useMutation<ProviderSyncResponse[], Error, void>({
    mutationFn: () => syncCourseIgot(courseId, employeeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: [COURSE_PROGRESS_KEY] });
      await queryClient.refetchQueries({ queryKey: [COURSE_PROGRESS_KEY] });
    },
  });
}

