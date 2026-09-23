import { useMutation } from '@tanstack/react-query';
import { searchEvidence } from '@/lib/api-client';
import type { RAGSearchRequest, RAGSearchResponse } from '@pragya/types';

/**
 * Mutation hook to perform semantic evidence retrieval across ingested officer documents.
 */
export function useRAGSearch() {
  return useMutation<RAGSearchResponse, Error, RAGSearchRequest>({
    mutationFn: (req: RAGSearchRequest) => searchEvidence(req),
  });
}
