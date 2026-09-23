import { useQuery } from '@tanstack/react-query';
import {
  getCompetencies,
  getCompetency,
  getCompetencyDomains,
  getDomainCompetencies,
  getProficiencyLevels,
  getRoleCompetencies,
  getCompetencyRoles,
} from '@/lib/api-client';

export function useCompetencyDomains() {
  return useQuery({
    queryKey: ['competency-domains'],
    queryFn: getCompetencyDomains,
    staleTime: 10 * 60 * 1000,
  });
}

export function useDomainCompetencies(domainId?: string) {
  return useQuery({
    queryKey: ['domain-competencies', domainId],
    queryFn: () => (domainId ? getDomainCompetencies(domainId) : Promise.reject('No domain ID')),
    enabled: !!domainId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useProficiencyLevels() {
  return useQuery({
    queryKey: ['proficiency-levels'],
    queryFn: getProficiencyLevels,
    staleTime: 10 * 60 * 1000,
  });
}

export function useCompetencies(params?: {
  domain?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}) {
  return useQuery({
    queryKey: ['competencies', params?.domain, params?.search, params?.page, params?.pageSize],
    queryFn: () => getCompetencies(params),
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompetency(id?: string) {
  return useQuery({
    queryKey: ['competency', id],
    queryFn: () => (id ? getCompetency(id) : Promise.reject('No competency ID')),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });
}

export function useRoleCompetencies(roleId?: string) {
  return useQuery({
    queryKey: ['role-competencies', roleId],
    queryFn: () => (roleId ? getRoleCompetencies(roleId) : Promise.reject('No role ID')),
    enabled: !!roleId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useCompetencyRoles(competencyId?: string) {
  return useQuery({
    queryKey: ['competency-roles', competencyId],
    queryFn: () => (competencyId ? getCompetencyRoles(competencyId) : Promise.reject('No competency ID')),
    enabled: !!competencyId,
    staleTime: 5 * 60 * 1000,
  });
}
