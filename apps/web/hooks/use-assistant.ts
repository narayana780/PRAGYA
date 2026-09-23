import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createAssistantConversation,
  getAssistantConversations,
  getAssistantConversation,
  deleteAssistantConversation,
  getAssistantMessages,
  sendAssistantMessage,
  answerDirect,
} from '@/lib/api-client';
import type {
  AssistantConversation,
  AssistantResponse,
  CreateConversationRequest,
  SendMessageRequest,
} from '@pragya/types';

export const ASSISTANT_CONVERSATIONS_KEY = 'assistant-conversations';
export const ASSISTANT_CONVERSATION_KEY = 'assistant-conversation';
export const ASSISTANT_MESSAGES_KEY = 'assistant-messages';

export function useAssistantConversations(limit = 30, offset = 0) {
  return useQuery({
    queryKey: [ASSISTANT_CONVERSATIONS_KEY, limit, offset],
    queryFn: () => getAssistantConversations(limit, offset),
  });
}

export function useAssistantConversation(id?: string) {
  return useQuery({
    queryKey: [ASSISTANT_CONVERSATION_KEY, id],
    queryFn: () => (id ? getAssistantConversation(id) : Promise.reject('No conversation ID')),
    enabled: !!id,
  });
}

export function useAssistantMessages(conversationId?: string) {
  return useQuery({
    queryKey: [ASSISTANT_MESSAGES_KEY, conversationId],
    queryFn: () =>
      conversationId
        ? getAssistantMessages(conversationId)
        : Promise.reject('No conversation ID'),
    enabled: !!conversationId,
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation<AssistantConversation, Error, CreateConversationRequest>({
    mutationFn: (req) => createAssistantConversation(req),
    onSuccess: (newConv) => {
      queryClient.setQueryData(
        [ASSISTANT_CONVERSATIONS_KEY, 30, 0],
        (old: AssistantConversation[] | undefined) => [newConv, ...(old || [])]
      );
      queryClient.invalidateQueries({ queryKey: [ASSISTANT_CONVERSATIONS_KEY] });
    },
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation<{ success: boolean; message: string }, Error, string>({
    mutationFn: (id) => deleteAssistantConversation(id),
    onSuccess: (_, deletedId) => {
      queryClient.setQueriesData<AssistantConversation[]>(
        { queryKey: [ASSISTANT_CONVERSATIONS_KEY] },
        (old) => (old ? old.filter((c) => c.id !== deletedId) : [])
      );
      queryClient.removeQueries({ queryKey: [ASSISTANT_CONVERSATION_KEY, deletedId] });
      queryClient.removeQueries({ queryKey: [ASSISTANT_MESSAGES_KEY, deletedId] });
      queryClient.invalidateQueries({ queryKey: [ASSISTANT_CONVERSATIONS_KEY] });
    },
  });
}

export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();
  return useMutation<AssistantResponse, Error, SendMessageRequest>({
    mutationFn: (req) => sendAssistantMessage(conversationId, req),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [ASSISTANT_MESSAGES_KEY, conversationId] });
      queryClient.invalidateQueries({ queryKey: [ASSISTANT_CONVERSATIONS_KEY] });
    },
  });
}

export function useAnswerDirect() {
  return useMutation<AssistantResponse, Error, SendMessageRequest>({
    mutationFn: (req) => answerDirect(req),
  });
}
