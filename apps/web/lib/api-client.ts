import type {
  Employee,
  Department,
  JobRole,
  TrainingHistory,
  EmployeeUpdatePayload,
  HealthStatusResponse,
  CompetencyDomain,
  ProficiencyLevel,
  CompetencySummary,
  CompetencyDetail,
  PaginatedCompetencies,
  RoleCompetencyRequirement,
  RoleRequiringCompetency,
  Assessment,
  AssessmentDetail,
  AssessmentAttempt,
  AttemptDetail,
  RecordResponseResult,
  CompleteAttemptResult,
  CompetencyEvidence,
  EmployeeCompetency,
  CompetencyScoreHistory,
  SelfAssessmentPayload,
  SelfAssessmentResult,
  SkillGap,
  SkillGapSummary,
  LearningItem,
  LearningRecommendation,
  LearningPath,
  ProviderInfo,
  UploadedMaterial,
  PaginatedMaterials,
  MaterialStatusDetail,
  DocumentChunk,
  RAGSearchRequest,
  RAGSearchResponse,
  AssistantConversation,
  AssistantMessage,
  AssistantResponse,
  CreateConversationRequest,
  SendMessageRequest,
  QuizSummary,
  QuizDetail,
  QuizAttemptSummary,
  GenerateQuizRequest,
  SubmitAnswerRequest,
  AnswerResponse,
  QuizResultResponse,
  QuizReviewResponse,
  AdaptiveSessionCreateRequest,
  AdaptiveSessionSummary,
  AdaptiveQuestionPresentation,
  AdaptiveSubmitAnswerRequest,
  AdaptiveSubmitAnswerResponse,
  RecalibrationResultResponse,
  LabScenarioSummary,
  LabScenarioDetail,
  LabSessionResponse,
  LabActionSubmitRequest,
  LabActionEvaluationResult,
  LabCompleteResponse,
  LabResultDetail,
  LabHintResponse,
  CourseResourceProgressPayload,
  CourseResourceProgressItem,
  KnowledgeCheckResultResponse,
  AssignmentResultResponse,
  FinalAssessmentResultResponse,
  CourseProgressResponse,
  CourseCompleteResponse,
  RecalibrateCourseResponse,
  CourseCurriculumResponse,
  ResourceLaunchResponse,
  ProviderSyncResponse,
  EmployeePerformanceResponse,
  EmployeeTimelineResponse,
  WorkforceOverview,
  WorkforceCompetenciesResponse,
  DepartmentAnalyticsResponse,
  DepartmentHeatmapResponse,
  WorkforceGapsResponse,
  RoleAnalyticsResponse,
  WorkforceTrainingOverviewResponse,
  AdminEmployeeListResponse,
  OverallTrainingEffectivenessResponse,
  CourseEffectivenessResponse,
  RecommendationEffectivenessResponse,
  EmployeeTrainingEffectivenessResponse,
  EmergingSkillsResponse,
  WorkforcePlanningOverviewResponse,
  WorkforceTrendsResponse,
  WorkforceCapacityForecastResponse,
  CompetencyCapacityForecastResponse,
  RoleCapacityForecastResponse,
  DepartmentCapacityForecastResponse,
  PlanningRecommendationsResponse,
  EmployeePlanningDrilldownResponse,
} from '@pragya/types';

export const API_BASE_URL =
  typeof window !== 'undefined'
    ? (process.env.NEXT_PUBLIC_API_BASE_URL && !process.env.NEXT_PUBLIC_API_BASE_URL.includes('localhost')
        ? process.env.NEXT_PUBLIC_API_BASE_URL
        : window.location.origin)
    : (process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000');

class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code = 'API_ERROR', status = 500) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

/**
 * Robust fetch wrapper with configurable timeout (default 15 seconds) via AbortController.
 * Ensures that API requests never hang indefinitely.
 */
export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 15000
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(url, {
      ...options,
      signal: options.signal || controller.signal,
    });
    return response;
  } catch (err: unknown) {
    if (err instanceof Error && (err.name === 'AbortError' || err.name === 'TimeoutError')) {
      throw new ApiError(
        `Request timed out after ${Math.round(timeoutMs / 1000)} seconds. Please check your connection and try again.`,
        'REQUEST_TIMEOUT',
        408
      );
    }
    throw err;
  } finally {
    clearTimeout(id);
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorData: { error?: { code?: string; message?: string } } | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Non-JSON response
    }
    const message =
      errorData?.error?.message ||
      `Request failed with status ${response.status} (${response.statusText})`;
    const code = errorData?.error?.code || 'API_ERROR';
    throw new ApiError(message, code, response.status);
  }
  if (response.status === 204) {
    return {} as T;
  }
  return response.json();
}

export async function fetchHealth(): Promise<HealthStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthStatusResponse>(response);
}

export async function fetchV1Health(): Promise<HealthStatusResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`);
  return handleResponse<HealthStatusResponse>(response);
}

/**
 * Retrieves the current primary demonstration officer profile.
 */
export async function getCurrentEmployee(): Promise<Employee> {
  const response = await fetch(`${API_BASE_URL}/api/v1/employees/me`);
  return handleResponse<Employee>(response);
}

/**
 * Retrieves an employee by their unique ID.
 */
export async function getEmployee(id: string): Promise<Employee> {
  const response = await fetch(`${API_BASE_URL}/api/v1/employees/${id}`);
  return handleResponse<Employee>(response);
}

/**
 * Updates editable profile attributes of an officer.
 */
export async function updateEmployee(
  id: string,
  payload: EmployeeUpdatePayload
): Promise<Employee> {
  const response = await fetch(`${API_BASE_URL}/api/v1/employees/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  return handleResponse<Employee>(response);
}

/**
 * Retrieves verified training records for an officer.
 */
export async function getEmployeeTrainingHistory(
  employeeId: string
): Promise<TrainingHistory[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/training-history`
  );
  return handleResponse<TrainingHistory[]>(response);
}

/**
 * Retrieves all active departments in the statistical system.
 */
export async function getDepartments(): Promise<Department[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/departments`);
  return handleResponse<Department[]>(response);
}

/**
 * Retrieves all official job roles / cadre levels.
 */
export async function getJobRoles(): Promise<JobRole[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/job-roles`);
  return handleResponse<JobRole[]>(response);
}

// ============================================================================
// Stage 4: Competency Dictionary & Framework API Methods
// ============================================================================

/**
 * Lists competencies from the dictionary with optional domain, search, and pagination.
 */
export async function getCompetencies(params?: {
  domain?: string;
  search?: string;
  page?: number;
  pageSize?: number;
}): Promise<PaginatedCompetencies> {
  const query = new URLSearchParams();
  if (params?.domain) query.append('domain', params.domain);
  if (params?.search) query.append('search', params.search);
  if (params?.page) query.append('page', params.page.toString());
  if (params?.pageSize) query.append('page_size', params.pageSize.toString());

  const queryString = query.toString() ? `?${query.toString()}` : '';
  const response = await fetch(`${API_BASE_URL}/api/v1/competencies${queryString}`);
  return handleResponse<PaginatedCompetencies>(response);
}

/**
 * Retrieves detailed competency metadata including prerequisites and demanding roles.
 */
export async function getCompetency(id: string): Promise<CompetencyDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/competencies/${id}`);
  return handleResponse<CompetencyDetail>(response);
}

/**
 * Lists the 4 canonical competency domains with current competency counts.
 */
export async function getCompetencyDomains(): Promise<CompetencyDomain[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/domains`);
  return handleResponse<CompetencyDomain[]>(response);
}

/**
 * Retrieves all competencies belonging to a specific domain.
 */
export async function getDomainCompetencies(
  domainId: string
): Promise<CompetencySummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/domains/${domainId}/competencies`);
  return handleResponse<CompetencySummary[]>(response);
}

/**
 * Retrieves the 5 canonical proficiency levels and score bounds.
 */
export async function getProficiencyLevels(): Promise<ProficiencyLevel[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/proficiency-levels`);
  return handleResponse<ProficiencyLevel[]>(response);
}

/**
 * Retrieves competency requirements and required levels for a job role.
 */
export async function getRoleCompetencies(
  roleId: string
): Promise<RoleCompetencyRequirement[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/job-roles/${roleId}/competencies`);
  return handleResponse<RoleCompetencyRequirement[]>(response);
}

/**
 * Retrieves roles that require a specific competency.
 */
export async function getCompetencyRoles(
  competencyId: string
): Promise<RoleRequiringCompetency[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/competencies/${competencyId}/roles`);
  return handleResponse<RoleRequiringCompetency[]>(response);
}

// ============================================================================
// Stage 5: Assessment & Competency Evidence API Methods
// ============================================================================

/**
 * Lists all active published assessments.
 */
export async function getAssessments(): Promise<Assessment[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments`);
  return handleResponse<Assessment[]>(response);
}

/**
 * Retrieves detailed assessment metadata with competencies tested.
 */
export async function getAssessment(id: string): Promise<AssessmentDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/${id}`);
  return handleResponse<AssessmentDetail>(response);
}

/**
 * Starts a new assessment attempt for an employee.
 */
export async function startAssessmentAttempt(
  assessmentId: string,
  employeeId: string
): Promise<AssessmentAttempt> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assessments/${assessmentId}/attempts`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employee_id: employeeId }),
    }
  );
  return handleResponse<AssessmentAttempt>(response);
}

/**
 * Retrieves attempt details and questions (answers hidden).
 */
export async function getAttempt(attemptId: string): Promise<AttemptDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assessments/attempts/${attemptId}`);
  return handleResponse<AttemptDetail>(response);
}

/**
 * Records an option selection for an assessment question.
 */
export async function recordAttemptResponse(
  attemptId: string,
  questionId: string,
  selectedOption: number,
  employeeId?: string
): Promise<RecordResponseResult> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (employeeId) headers['X-Employee-Id'] = employeeId;

  const response = await fetch(
    `${API_BASE_URL}/api/v1/assessments/attempts/${attemptId}/responses`,
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        question_id: questionId,
        selected_option: selectedOption,
      }),
    }
  );
  return handleResponse<RecordResponseResult>(response);
}

/**
 * Submits and completes an assessment attempt, calculating scores and creating evidence.
 */
export async function completeAttempt(
  attemptId: string,
  employeeId?: string
): Promise<CompleteAttemptResult> {
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;

  const response = await fetch(
    `${API_BASE_URL}/api/v1/assessments/attempts/${attemptId}/complete`,
    {
      method: 'POST',
      headers,
    }
  );
  return handleResponse<CompleteAttemptResult>(response);
}

/**
 * Retrieves all currently estimated competencies for an employee.
 */
export async function getEmployeeCompetencies(
  employeeId: string
): Promise<EmployeeCompetency[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/competencies`
  );
  return handleResponse<EmployeeCompetency[]>(response);
}

/**
 * Retrieves a single employee competency score and confidence rating.
 */
export async function getEmployeeCompetencyDetail(
  employeeId: string,
  competencyId: string
): Promise<EmployeeCompetency> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/competencies/${competencyId}`
  );
  return handleResponse<EmployeeCompetency>(response);
}

/**
 * Retrieves all empirical evidence records contributing to an employee's competency.
 */
export async function getCompetencyEvidence(
  employeeId: string,
  competencyId: string
): Promise<CompetencyEvidence[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/competencies/${competencyId}/evidence`
  );
  return handleResponse<CompetencyEvidence[]>(response);
}

/**
 * Retrieves score change audit history for an employee's competency.
 */
export async function getCompetencyHistory(
  employeeId: string,
  competencyId: string
): Promise<CompetencyScoreHistory[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/competencies/${competencyId}/history`
  );
  return handleResponse<CompetencyScoreHistory[]>(response);
}

/**
 * Submits employee self-assessment level (1-5) and receives recalibrated score.
 */
export async function submitSelfAssessment(
  employeeId: string,
  payload: SelfAssessmentPayload
): Promise<SelfAssessmentResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/self-assessment`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }
  );
  return handleResponse<SelfAssessmentResult>(response);
}

// ============================================================================
// Stage 6: Skill Gap Calculation & Gap Priority API Methods
// ============================================================================

export interface SkillGapFilterParams {
  priority?: string;
  domain?: string;
  competency?: string;
  confidence?: string;
}

/**
 * Retrieves all calculated skill gaps for an employee, with optional filters.
 */
export async function getEmployeeSkillGaps(
  employeeId: string,
  params?: SkillGapFilterParams
): Promise<SkillGap[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/employees/${employeeId}/skill-gaps`);
  if (params?.priority) url.searchParams.set('priority', params.priority);
  if (params?.domain) url.searchParams.set('domain', params.domain);
  if (params?.competency) url.searchParams.set('competency', params.competency);
  if (params?.confidence) url.searchParams.set('confidence', params.confidence);

  const response = await fetch(url.toString());
  return handleResponse<SkillGap[]>(response);
}

/**
 * Retrieves skill gap summary metrics for an employee.
 */
export async function getSkillGapSummary(
  employeeId: string
): Promise<SkillGapSummary> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/skill-gaps/summary`
  );
  return handleResponse<SkillGapSummary>(response);
}

/**
 * Retrieves detailed breakdown for a specific employee skill gap.
 */
export async function getSkillGapDetail(
  employeeId: string,
  competencyId: string
): Promise<SkillGap> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/skill-gaps/${competencyId}`
  );
  return handleResponse<SkillGap>(response);
}

/**
 * Explicitly triggers a recalculation of all skill gaps for an employee.
 */
export async function recalculateEmployeeSkillGaps(
  employeeId: string
): Promise<SkillGap[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/skill-gaps/recalculate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<SkillGap[]>(response);
}

// =========================================================================
// STAGE 7: LEARNING PROVIDER & RECOMMENDATION APIS
// =========================================================================

/**
 * Retrieves registry of all learning providers and integration modes (MOCK/LIVE).
 */
export async function getProviders(): Promise<ProviderInfo[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/providers`);
  return handleResponse<ProviderInfo[]>(response);
}

export interface LearningItemsQueryParams {
  search?: string;
  provider?: string;
  competency_id?: string;
  difficulty?: string;
  format?: string;
  skip?: number;
  limit?: number;
}

/**
 * Retrieves paginated catalogue of learning items with optional filters.
 */
export async function getLearningItems(
  params: LearningItemsQueryParams = {}
): Promise<{ items: LearningItem[]; total: number }> {
  const url = new URL(`${API_BASE_URL}/api/v1/learning-items`);
  const isValidParam = (val?: string) => {
    if (!val) return false;
    const s = val.trim().toUpperCase();
    return s !== '' && !['ALL', 'NONE', 'NULL', 'UNDEFINED'].includes(s);
  };

  if (params.search && params.search.trim()) url.searchParams.set('search', params.search.trim());
  if (isValidParam(params.provider)) url.searchParams.set('provider', params.provider!.trim());
  if (isValidParam(params.competency_id)) url.searchParams.set('competency_id', params.competency_id!.trim());
  if (isValidParam(params.difficulty)) url.searchParams.set('difficulty', params.difficulty!.trim());
  if (isValidParam(params.format)) {
    url.searchParams.set('format', params.format!.trim());
    url.searchParams.set('format_type', params.format!.trim());
  }
  if (params.skip !== undefined) {
    url.searchParams.set('skip', String(params.skip));
    url.searchParams.set('offset', String(params.skip));
  }
  if (params.limit !== undefined) url.searchParams.set('limit', String(params.limit));

  const response = await fetch(url.toString());
  return handleResponse<{ items: LearningItem[]; total: number }>(response);
}

/**
 * Retrieves a single learning item by ID with full competency mappings.
 */
export async function getLearningItem(id: string): Promise<LearningItem> {
  const response = await fetch(`${API_BASE_URL}/api/v1/learning-items/${id}`);
  return handleResponse<LearningItem>(response);
}

export interface RecommendationQueryParams {
  priority?: string;
  provider?: string;
  competency?: string;
  type?: string;
  language?: string;
}

/**
 * Retrieves personalized learning recommendations for an employee.
 */
export async function getRecommendations(
  employeeId: string,
  params: RecommendationQueryParams = {}
): Promise<LearningRecommendation[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/employees/${employeeId}/recommendations`);
  if (params.priority) url.searchParams.set('priority', params.priority);
  if (params.provider) url.searchParams.set('provider', params.provider);
  if (params.competency) url.searchParams.set('competency', params.competency);
  if (params.type) url.searchParams.set('type', params.type);
  if (params.language) url.searchParams.set('language', params.language);

  const response = await fetch(url.toString());
  return handleResponse<LearningRecommendation[]>(response);
}

/**
 * Retrieves a single learning recommendation by ID.
 */
export async function getRecommendation(
  employeeId: string,
  recommendationId: string
): Promise<LearningRecommendation> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/recommendations/${recommendationId}`
  );
  return handleResponse<LearningRecommendation>(response);
}

/**
 * Triggers re-generation of personalized recommendations for an employee.
 */
export async function generateRecommendations(
  employeeId: string
): Promise<LearningRecommendation[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/recommendations/generate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<LearningRecommendation[]>(response);
}

/**
 * Marks a learning recommendation as STARTED.
 */
export async function startRecommendation(
  employeeId: string,
  recommendationId: string
): Promise<LearningRecommendation> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/recommendations/${recommendationId}/start`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<LearningRecommendation>(response);
}

/**
 * Dismisses a learning recommendation.
 */
export async function dismissRecommendation(
  employeeId: string,
  recommendationId: string
): Promise<LearningRecommendation> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/recommendations/${recommendationId}/dismiss`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<LearningRecommendation>(response);
}

/**
 * Retrieves the current progressive learning path for an employee.
 */
export async function getLearningPath(
  employeeId: string
): Promise<LearningPath> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/learning-path`
  );
  return handleResponse<LearningPath>(response);
}

/**
 * Generates or refreshes the progressive learning path for an employee.
 */
export async function generateLearningPath(
  employeeId: string
): Promise<LearningPath> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/learning-path/generate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    }
  );
  return handleResponse<LearningPath>(response);
}

// ============================================================================
// Stage 8: Document Intelligence & RAG Retrieval
// ============================================================================

/**
 * Uploads a document (PDF, PPT, PPTX, TXT) for background processing and vector ingestion.
 */
export async function uploadMaterial(file: File): Promise<UploadedMaterial> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/v1/materials/upload`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse<UploadedMaterial>(response);
}

/**
 * Retrieves paginated list of uploaded materials for the current employee.
 */
export async function getMaterials(
  skip = 0,
  limit = 20
): Promise<PaginatedMaterials> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/materials?skip=${skip}&limit=${limit}`
  );
  return handleResponse<PaginatedMaterials>(response);
}

/**
 * Retrieves detailed information for a specific uploaded material.
 */
export async function getMaterial(id: string): Promise<UploadedMaterial> {
  const response = await fetch(`${API_BASE_URL}/api/v1/materials/${id}`);
  return handleResponse<UploadedMaterial>(response);
}

/**
 * Polls the current processing status of an uploaded material.
 */
export async function getMaterialStatus(
  id: string
): Promise<MaterialStatusDetail> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/materials/${id}/status`
  );
  return handleResponse<MaterialStatusDetail>(response);
}

/**
 * Deletes an uploaded learning material and its associated vectors and documents.
 */
export async function deleteMaterial(
  id: string
): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/api/v1/materials/${id}`, {
    method: 'DELETE',
  });
  return handleResponse<{ status: string; message: string }>(response);
}

/**
 * Retrieves the extracted and indexed text chunks for an uploaded material.
 */
export async function getMaterialChunks(
  id: string
): Promise<DocumentChunk[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/materials/${id}/chunks`
  );
  return handleResponse<DocumentChunk[]>(response);
}

/**
 * Retrieves evidence chunks relevant to a query using semantic vector search.
 */
export async function searchEvidence(
  req: RAGSearchRequest
): Promise<RAGSearchResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/rag/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return handleResponse<RAGSearchResponse>(response);
}

/**
 * Creates a new learning assistant conversation.
 */
export async function createAssistantConversation(
  req: CreateConversationRequest
): Promise<AssistantConversation> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assistant/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return handleResponse<AssistantConversation>(response);
}

/**
 * Retrieves the list of conversations for the current employee.
 */
export async function getAssistantConversations(
  limit = 20,
  offset = 0
): Promise<AssistantConversation[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assistant/conversations?limit=${limit}&offset=${offset}`
  );
  return handleResponse<AssistantConversation[]>(response);
}

/**
 * Retrieves a single conversation by ID.
 */
export async function getAssistantConversation(
  id: string
): Promise<AssistantConversation> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assistant/conversations/${id}`
  );
  return handleResponse<AssistantConversation>(response);
}

/**
 * Deletes a conversation and its messages.
 */
export async function deleteAssistantConversation(
  id: string
): Promise<{ success: boolean; message: string }> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assistant/conversations/${id}`,
    {
      method: 'DELETE',
    }
  );
  if (!response.ok) {
    let errorData: { error?: { code?: string; message?: string } } | null = null;
    try {
      errorData = await response.json();
    } catch {
      // Non-JSON response
    }
    const message =
      errorData?.error?.message ||
      `Request failed with status ${response.status} (${response.statusText})`;
    const code = errorData?.error?.code || 'API_ERROR';
    throw new ApiError(message, code, response.status);
  }
  return { success: true, message: 'Conversation deleted successfully' };
}

/**
 * Retrieves messages for a conversation.
 */
export async function getAssistantMessages(
  conversationId: string,
  limit = 50
): Promise<AssistantMessage[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assistant/conversations/${conversationId}/messages?limit=${limit}`
  );
  return handleResponse<AssistantMessage[]>(response);
}

/**
 * Sends a message in a conversation and gets a grounded response.
 */
export async function sendAssistantMessage(
  conversationId: string,
  req: SendMessageRequest
): Promise<AssistantResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/assistant/conversations/${conversationId}/messages`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    }
  );
  return handleResponse<AssistantResponse>(response);
}

/**
 * Optional stateless endpoint to ask a question directly without creating a conversation.
 */
export async function answerDirect(
  req: SendMessageRequest
): Promise<AssistantResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/assistant/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return handleResponse<AssistantResponse>(response);
}

/**
 * ============================================================================
 * Stage 10: AI Quiz & MCQ Generation API Methods
 * ============================================================================
 */

export async function generateQuiz(req: GenerateQuizRequest): Promise<QuizDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quizzes/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return handleResponse<QuizDetail>(response);
}

export async function getQuizzes(limit = 50): Promise<QuizSummary[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quizzes?limit=${limit}`);
  return handleResponse<QuizSummary[]>(response);
}

export async function getQuiz(quizId: string): Promise<QuizDetail> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quizzes/${quizId}`);
  return handleResponse<QuizDetail>(response);
}

export async function startQuizAttempt(quizId: string): Promise<QuizAttemptSummary> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quizzes/${quizId}/attempts`, {
    method: 'POST',
  });
  return handleResponse<QuizAttemptSummary>(response);
}

export async function listQuizAttempts(quizId?: string): Promise<QuizAttemptSummary[]> {
  const url = quizId
    ? `${API_BASE_URL}/api/v1/quizzes/${quizId}/attempts`
    : `${API_BASE_URL}/api/v1/quizzes/attempts`;
  const response = await fetch(url);
  return handleResponse<QuizAttemptSummary[]>(response);
}

export async function submitQuizAnswer(
  attemptId: string,
  req: SubmitAnswerRequest
): Promise<AnswerResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/quiz-attempts/${attemptId}/answers`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    }
  );
  return handleResponse<AnswerResponse>(response);
}

export async function completeQuizAttempt(
  attemptId: string
): Promise<QuizResultResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/quiz-attempts/${attemptId}/complete`,
    {
      method: 'POST',
    }
  );
  return handleResponse<QuizResultResponse>(response);
}

export async function getQuizResult(
  attemptId: string
): Promise<QuizResultResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/quiz-attempts/${attemptId}/result`
  );
  return handleResponse<QuizResultResponse>(response);
}

export async function getQuizReview(
  attemptId: string
): Promise<QuizReviewResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/quiz-attempts/${attemptId}/review`
  );
  return handleResponse<QuizReviewResponse>(response);
}

// ============================================================================
// Stage 11: Adaptive Assessment & Competency Recalibration API Methods
// ============================================================================

export async function createAdaptiveSession(
  req: AdaptiveSessionCreateRequest
): Promise<AdaptiveSessionSummary> {
  const response = await fetch(`${API_BASE_URL}/api/v1/adaptive-assessments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return handleResponse<AdaptiveSessionSummary>(response);
}

export async function getAdaptiveSession(
  sessionId: string
): Promise<AdaptiveSessionSummary> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/adaptive-assessments/${sessionId}`
  );
  return handleResponse<AdaptiveSessionSummary>(response);
}

export async function getNextAdaptiveQuestion(
  sessionId: string
): Promise<AdaptiveQuestionPresentation> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/adaptive-assessments/${sessionId}/questions/next`,
    {
      method: 'POST',
    }
  );
  return handleResponse<AdaptiveQuestionPresentation>(response);
}

export async function submitAdaptiveResponse(
  sessionId: string,
  req: AdaptiveSubmitAnswerRequest
): Promise<AdaptiveSubmitAnswerResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/adaptive-assessments/${sessionId}/responses`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req),
    }
  );
  return handleResponse<AdaptiveSubmitAnswerResponse>(response);
}

export async function completeAdaptiveSession(
  sessionId: string
): Promise<RecalibrationResultResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/adaptive-assessments/${sessionId}/complete`,
    {
      method: 'POST',
    }
  );
  return handleResponse<RecalibrationResultResponse>(response);
}

export async function getAdaptiveResult(
  sessionId: string
): Promise<RecalibrationResultResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/adaptive-assessments/${sessionId}/result`
  );
  return handleResponse<RecalibrationResultResponse>(response);
}

// ============================================================================
// Stage 12: PRAGYA Statistical Virtual Lab API Methods
// ============================================================================

export async function getLabScenarios(params?: {
  competencyId?: string;
  scenarioType?: string;
  difficulty?: string;
}): Promise<LabScenarioSummary[]> {
  const query = new URLSearchParams();
  if (params?.competencyId) query.set('competency_id', params.competencyId);
  if (params?.scenarioType) query.set('scenario_type', params.scenarioType);
  if (params?.difficulty) query.set('difficulty', params.difficulty);

  const qs = query.toString();
  const url = `${API_BASE_URL}/api/v1/labs${qs ? `?${qs}` : ''}`;
  const response = await fetchWithTimeout(url);
  return handleResponse<LabScenarioSummary[]>(response);
}

export async function getLabScenario(id: string): Promise<LabScenarioDetail> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/labs/${id}`);
  return handleResponse<LabScenarioDetail>(response);
}

export async function startLabSession(scenarioId: string): Promise<LabSessionResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/labs/${scenarioId}/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });
  return handleResponse<LabSessionResponse>(response);
}

export async function getLabSession(sessionId: string): Promise<LabSessionResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/lab-sessions/${sessionId}`);
  return handleResponse<LabSessionResponse>(response);
}

export async function submitLabAction(
  sessionId: string,
  payload: LabActionSubmitRequest
): Promise<LabActionEvaluationResult> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/lab-sessions/${sessionId}/actions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  return handleResponse<LabActionEvaluationResult>(response);
}

export async function completeLabSession(sessionId: string): Promise<LabCompleteResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/lab-sessions/${sessionId}/complete`, {
    method: 'POST',
  });
  return handleResponse<LabCompleteResponse>(response);
}

export async function getLabResult(sessionId: string): Promise<LabResultDetail> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/lab-sessions/${sessionId}/result`);
  return handleResponse<LabResultDetail>(response);
}

export async function getLabHint(
  sessionId: string,
  stepNumber: number
): Promise<LabHintResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/lab-sessions/${sessionId}/hint`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ step_number: stepNumber }),
  });
  return handleResponse<LabHintResponse>(response);
}

export async function getMyLabSessions(employeeId?: string): Promise<LabSessionResponse[]> {
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/labs/sessions/my`, { headers });
  return handleResponse<LabSessionResponse[]>(response);
}

// -----------------------------------------------------------------------------
// Course Learning Path & Progress Client Methods
// -----------------------------------------------------------------------------

export async function getCourseCurriculum(courseId: string): Promise<CourseCurriculumResponse> {
  const response = await fetchWithTimeout(`${API_BASE_URL}/api/v1/courses/${courseId}/curriculum`);
  return handleResponse<CourseCurriculumResponse>(response);
}

export async function getCourseProgress(
  courseId: string,
  employeeId?: string
): Promise<CourseProgressResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/progress`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), { headers });
  return handleResponse<CourseProgressResponse>(response);
}

export async function updateCourseResourceProgress(
  courseId: string,
  resourceId: string,
  payload: CourseResourceProgressPayload,
  employeeId?: string
): Promise<CourseResourceProgressItem> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/resources/${resourceId}/progress`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
  return handleResponse<CourseResourceProgressItem>(response);
}

export async function submitCourseKnowledgeCheck(
  courseId: string,
  moduleId: number,
  answers: Record<string, number>,
  employeeId?: string
): Promise<KnowledgeCheckResultResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/modules/${moduleId}/knowledge-check`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify({ answers }),
  });
  return handleResponse<KnowledgeCheckResultResponse>(response);
}

export async function submitCourseAssignment(
  courseId: string,
  moduleId: number,
  payload: {
    sampling_method: string;
    allocation_strategy: string;
    non_response_buffer: string;
    justification_code: string;
  },
  employeeId?: string
): Promise<AssignmentResultResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/modules/${moduleId}/assignment`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify(payload),
  });
  return handleResponse<AssignmentResultResponse>(response);
}

export async function submitCourseFinalAssessment(
  courseId: string,
  answers: Record<string, number>,
  employeeId?: string
): Promise<FinalAssessmentResultResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/final-assessment`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
    body: JSON.stringify({ answers }),
  });
  return handleResponse<FinalAssessmentResultResponse>(response);
}

export async function completeCourse(
  courseId: string,
  employeeId?: string
): Promise<CourseCompleteResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/complete`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
  });
  return handleResponse<CourseCompleteResponse>(response);
}

export async function recalibrateCourse(
  courseId: string,
  employeeId?: string
): Promise<RecalibrateCourseResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/recalibrate`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
  });
  return handleResponse<RecalibrateCourseResponse>(response);
}

export async function launchCourseResource(
  courseId: string,
  resourceId: string,
  employeeId?: string
): Promise<ResourceLaunchResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/resources/${resourceId}/launch`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
  });
  return handleResponse<ResourceLaunchResponse>(response);
}

export async function syncCourseResource(
  courseId: string,
  resourceId: string,
  employeeId?: string
): Promise<ProviderSyncResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/resources/${resourceId}/sync`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
  });
  return handleResponse<ProviderSyncResponse>(response);
}

export async function syncCourseIgot(
  courseId: string,
  employeeId?: string
): Promise<ProviderSyncResponse[]> {
  const url = new URL(`${API_BASE_URL}/api/v1/courses/${courseId}/providers/igot/sync`);
  if (employeeId) url.searchParams.set('employee_id', employeeId);
  const headers: Record<string, string> = {};
  if (employeeId) headers['X-Employee-Id'] = employeeId;
  const response = await fetchWithTimeout(url.toString(), {
    method: 'POST',
    headers,
  });
  return handleResponse<ProviderSyncResponse[]>(response);
}

// ============================================================================
// Stage 13: Employee Performance Analysis & Longitudinal Tracking API Methods
// ============================================================================

export async function getEmployeePerformance(
  employeeId: string
): Promise<EmployeePerformanceResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/performance`
  );
  return handleResponse<EmployeePerformanceResponse>(response);
}

export async function getEmployeeTimeline(
  employeeId: string,
  eventType?: string,
  limit?: number
): Promise<EmployeeTimelineResponse> {
  const url = new URL(
    `${API_BASE_URL}/api/v1/employees/${employeeId}/history/timeline`
  );
  if (eventType && eventType !== 'ALL') {
    url.searchParams.set('event_type', eventType);
  }
  if (limit) {
    url.searchParams.set('limit', limit.toString());
  }
  const response = await fetchWithTimeout(url.toString());
  return handleResponse<EmployeeTimelineResponse>(response);
}

// ============================================================================
// Stage 14: Administrator Workforce Intelligence & Cadre Analytics API Methods
// ============================================================================

const ADMIN_HEADERS: HeadersInit = {
  'Content-Type': 'application/json',
  'X-User-Role': 'ADMIN',
};

export async function getWorkforceOverview(): Promise<WorkforceOverview> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/overview`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceOverview>(response);
}

export async function getWorkforceCompetencies(): Promise<WorkforceCompetenciesResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/competencies`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceCompetenciesResponse>(response);
}

export async function getDepartmentAnalytics(): Promise<DepartmentAnalyticsResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/departments/analytics`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<DepartmentAnalyticsResponse>(response);
}

export async function getDepartmentHeatmap(): Promise<DepartmentHeatmapResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/departments/heatmap`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<DepartmentHeatmapResponse>(response);
}

export async function getWorkforceGaps(): Promise<WorkforceGapsResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/gaps`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceGapsResponse>(response);
}

export async function getRoleAnalytics(): Promise<RoleAnalyticsResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/roles/analytics`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<RoleAnalyticsResponse>(response);
}

export async function getWorkforceTrainingAnalytics(): Promise<WorkforceTrainingOverviewResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/training/analytics`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceTrainingOverviewResponse>(response);
}

export async function getAdminEmployeeList(): Promise<AdminEmployeeListResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/employees`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<AdminEmployeeListResponse>(response);
}

// ============================================================================
// Stage 15: Training Effectiveness & Recommendation Analytics API Methods
// ============================================================================

export async function getOverallTrainingEffectiveness(): Promise<OverallTrainingEffectivenessResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/training/effectiveness`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<OverallTrainingEffectivenessResponse>(response);
}

export async function getCourseEffectiveness(): Promise<CourseEffectivenessResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/training/courses/effectiveness`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<CourseEffectivenessResponse>(response);
}

export async function getRecommendationEffectiveness(): Promise<RecommendationEffectivenessResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/recommendations/effectiveness`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<RecommendationEffectivenessResponse>(response);
}

export async function getEmployeeTrainingEffectiveness(
  employeeId: string
): Promise<EmployeeTrainingEffectivenessResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/training/employees/${employeeId}/effectiveness`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<EmployeeTrainingEffectivenessResponse>(response);
}

// ============================================================================
// Stage 16: Emerging Skills & Technology Horizon Scanning API Methods
// ============================================================================

export async function getEmergingSkills(domainId?: string): Promise<EmergingSkillsResponse> {
  const url = new URL(`${API_BASE_URL}/api/v1/admin/emerging-skills`);
  if (domainId && domainId !== 'ALL') {
    url.searchParams.set('domain_id', domainId);
  }
  const response = await fetchWithTimeout(url.toString(), {
    headers: ADMIN_HEADERS,
  });
  return handleResponse<EmergingSkillsResponse>(response);
}

// ============================================================================
// Stage 17: Predictive Workforce Planning & Capacity Forecasting API Methods
// ============================================================================

export async function getWorkforcePlanningOverview(): Promise<WorkforcePlanningOverviewResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/overview`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforcePlanningOverviewResponse>(response);
}

export async function getWorkforcePlanningTrends(): Promise<WorkforceTrendsResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/trends`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceTrendsResponse>(response);
}

export async function getWorkforceCapacityForecast(): Promise<WorkforceCapacityForecastResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/forecast`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<WorkforceCapacityForecastResponse>(response);
}

export async function getCompetencyCapacityForecast(): Promise<CompetencyCapacityForecastResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/competencies`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<CompetencyCapacityForecastResponse>(response);
}

export async function getRoleCapacityForecast(): Promise<RoleCapacityForecastResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/roles`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<RoleCapacityForecastResponse>(response);
}

export async function getDepartmentCapacityForecast(): Promise<DepartmentCapacityForecastResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/departments`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<DepartmentCapacityForecastResponse>(response);
}

export async function getPlanningRecommendations(): Promise<PlanningRecommendationsResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/recommendations`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<PlanningRecommendationsResponse>(response);
}

export async function getEmployeePlanningDrilldown(
  employeeId: string
): Promise<EmployeePlanningDrilldownResponse> {
  const response = await fetchWithTimeout(
    `${API_BASE_URL}/api/v1/admin/workforce/planning/employees/${employeeId}`,
    { headers: ADMIN_HEADERS }
  );
  return handleResponse<EmployeePlanningDrilldownResponse>(response);
}

/**
 * Triggers a secure authenticated download of an administrative report file (PDF or Excel).
 */
export async function downloadAdminReport(
  endpointPath: string,
  filename: string
): Promise<void> {
  const url = `${API_BASE_URL}${endpointPath}`;
  const response = await fetchWithTimeout(
    url,
    { headers: ADMIN_HEADERS },
    45000
  );

  if (!response.ok) {
    let errMsg = `Export failed with status ${response.status}`;
    try {
      const errJson = await response.json();
      errMsg = errJson.detail || errMsg;
    } catch {
      // fallback
    }
    throw new Error(errMsg);
  }

  const blob = await response.blob();
  const blobUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = blobUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(blobUrl);
}








