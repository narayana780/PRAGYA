import { useQuery } from '@tanstack/react-query';
import { getEmergingSkills } from '@/lib/api-client';

export const emergingSkillsKeys = {
  all: ['emerging-skills'] as const,
  list: (domainId?: string) => [...emergingSkillsKeys.all, 'list', domainId || 'ALL'] as const,
};

export function useEmergingSkills(domainId?: string) {
  return useQuery({
    queryKey: emergingSkillsKeys.list(domainId),
    queryFn: () => getEmergingSkills(domainId),
    staleTime: 60 * 1000,
  });
}
