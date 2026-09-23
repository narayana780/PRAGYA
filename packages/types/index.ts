/**
 * PRAGYA Foundation Core Types
 * Shared domain contracts between Frontend (apps/web) and Backend (apps/api)
 */

export type UserRole = 'EMPLOYEE' | 'TRAINER' | 'ADMIN' | 'SUPER_ADMIN';

export interface ApiErrorDetail {
  code: string;
  message: string;
  field?: string;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiErrorDetail;
}

export interface HealthStatusResponse {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  version: string;
  database?: {
    connected: boolean;
    dialect?: string;
  };
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface JobRole {
  id: string;
  name: string;
  code: string;
  description: string | null;
  career_level: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TrainingHistory {
  id: string;
  employee_id: string;
  title: string;
  provider: string;
  provider_type: 'IGOT' | 'NSSTA_TPAC' | 'OTHER' | string;
  course_id: string | null;
  programme_id: string | null;
  completed_at: string | null;
  status: string;
  score: number | null;
  duration_hours: number | null;
  certificate_reference: string | null;
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: string;
  employee_code: string;
  user_id: string | null;
  full_name: string;
  designation: string;
  department_id: string;
  department_name: string | null;
  department_code: string | null;
  job_role_id: string;
  job_role_name: string | null;
  job_role_code: string | null;
  current_assignment: string | null;
  education: string | null;
  experience_years: number;
  preferred_language: string;
  target_role_id: string | null;
  target_role_name: string | null;
  profile_image_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  training_count?: number;
}

export interface EmployeeUpdatePayload {
  current_assignment?: string;
  education?: string;
  experience_years?: number;
  preferred_language?: string;
  target_role_id?: string | null;
}

// ============================================================================
// Stage 4: Competency Framework & Taxonomy Types
// ============================================================================

export interface CompetencyDomain {
  id: string;
  code: 'STATISTICAL' | 'TECHNICAL' | 'DIGITAL_GOVERNANCE' | 'BEHAVIOURAL_MANAGERIAL' | string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  competency_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProficiencyLevel {
  id: string;
  level_number: number;
  name: 'Awareness' | 'Foundation' | 'Working' | 'Proficient' | 'Advanced' | string;
  description: string;
  minimum_score: number;
  maximum_score: number;
  display_order: number;
  is_active: boolean;
}

export interface CompetencyRelationship {
  id: string;
  source_competency_id: string;
  source_competency_name?: string | null;
  source_competency_code?: string | null;
  target_competency_id: string;
  target_competency_name?: string | null;
  target_competency_code?: string | null;
  relationship_type: string;
  strength: number;
}

export interface RoleRequiringCompetency {
  job_role_id: string;
  job_role_name: string;
  job_role_code: string;
  career_level: string;
  required_level_number: number;
  required_level_name: string;
  criticality: string;
  rationale?: string | null;
}

export interface CompetencySummary {
  id: string;
  code: string;
  name: string;
  domain_id: string;
  domain_code: string | null;
  domain_name: string | null;
  short_description: string;
  version: string;
  is_active: boolean;
  source_reference: string;
  created_at: string;
  updated_at: string;
}

export interface CompetencyDetail extends CompetencySummary {
  description: string;
  learning_objectives: string | null;
  measurement_guidance: string | null;
  aliases: string | null;
  prerequisites: CompetencyRelationship[];
  requiring_roles: RoleRequiringCompetency[];
}

export interface PaginatedCompetencies {
  items: CompetencySummary[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface RoleCompetencyRequirement {
  id: string;
  job_role_id: string;
  job_role_name: string;
  job_role_code: string;
  competency_id: string;
  competency_name: string;
  competency_code: string;
  domain_code: string;
  domain_name: string;
  required_level_id: string;
  required_level_number: number;
  required_level_name: string;
  required_score: number;
  criticality: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  task_relevance: 'LOW' | 'MEDIUM' | 'HIGH' | string;
  priority: number;
  rationale: string | null;
  source_reference: string;
}

// ============================================================================
// Stage 5: Assessment Engine & Competency Evidence Types
// ============================================================================

export interface Assessment {
  id: string;
  title: string;
  description: string;
  assessment_type: 'DIAGNOSTIC' | 'QUIZ' | 'ADAPTIVE' | 'PRACTICE' | string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | string;
  duration_minutes: number;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface AssessmentDetail extends Assessment {
  competencies: { id: string; code: string; name: string }[];
}

export interface QuestionPublic {
  id: string;
  assessment_id: string;
  competency_id: string;
  question_text: string;
  options: string[];
  difficulty: 'EASY' | 'MEDIUM' | 'HARD' | string;
  points: number;
  order_index: number;
}

export interface AssessmentAttempt {
  id: string;
  assessment_id: string;
  employee_id: string;
  started_at: string;
  completed_at: string | null;
  raw_score: number;
  percentage: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED' | string;
}

export interface AttemptDetail extends AssessmentAttempt {
  assessment_title: string;
  duration_minutes: number;
  questions: QuestionPublic[];
  answered_question_ids: string[];
}

export interface RecordResponseResult {
  attempt_id: string;
  question_id: string;
  selected_option: number;
  responded_at: string;
}

export interface CompetencyBreakdownItem {
  competency_id: string;
  competency_name: string;
  competency_code: string;
  questions_tested: number;
  correct_count: number;
  score_percentage: number;
}

export interface CompleteAttemptResult {
  attempt_id: string;
  assessment_id: string;
  employee_id: string;
  status: string;
  completed_at: string;
  raw_score: number;
  max_score: number;
  percentage: number;
  total_questions: number;
  answered_questions: number;
  competency_breakdown: CompetencyBreakdownItem[];
}

export type AssessmentQuestion = QuestionPublic;
export type AttemptResultResponse = CompleteAttemptResult;

export interface CompetencyEvidence {
  id: string;
  employee_id: string;
  competency_id: string;
  evidence_type: 'DIAGNOSTIC' | 'RECENT_ASSESSMENT' | 'TRAINING' | 'EXPERIENCE' | 'SELF_ASSESSMENT' | string;
  source_id: string | null;
  raw_value: number;
  normalized_score: number;
  weight_used: number;
  contribution: number;
  confidence: number;
  recorded_at: string;
  metadata: Record<string, any> | null;
}

export interface EmployeeCompetency {
  id: string;
  employee_id: string;
  competency_id: string;
  competency_name: string;
  competency_code: string;
  domain_name: string;
  domain_code: string;
  current_score: number;
  proficiency_level_number: number;
  proficiency_level_name: string;
  confidence: number;
  confidence_label: 'LOW' | 'MEDIUM' | 'HIGH' | 'VERY_HIGH' | string;
  last_assessed_at: string;
  evidence_count: number;
}

export interface CompetencyScoreHistory {
  id: string;
  employee_id: string;
  competency_id: string;
  competency_name: string | null;
  previous_score: number | null;
  new_score: number;
  previous_confidence: number | null;
  new_confidence: number;
  change_reason: string;
  created_at: string;
}

export interface SelfAssessmentPayload {
  competency_id: string;
  level: number;
}

export interface SelfAssessmentResult {
  competency_id: string;
  level: number;
  normalized_score: number;
  new_competency_score: number;
  confidence: number;
  confidence_label: string;
}

// ============================================================================
// Stage 6: Skill Gap & Gap Priority Intelligence Types
// ============================================================================

export type PriorityLevel = 'NO_GAP' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type ConfidenceFlag = 'LOW_CONFIDENCE' | 'MEDIUM_CONFIDENCE' | 'HIGH_CONFIDENCE' | 'VERY_HIGH_CONFIDENCE';
export type CriticalityLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type TaskRelevanceLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type MissionUrgencyLevel = 'HIGH' | 'MEDIUM' | 'LOW';

export interface PriorityBreakdown {
  gap_component: number;
  criticality_component: number;
  task_relevance_component: number;
  mission_urgency_component: number;
  confidence_component: number;
}

export interface SkillGap {
  id: string;
  employee_id: string;
  competency_id: string;
  competency_code: string;
  competency_name: string;
  domain_name: string;
  domain_code: string;
  current_score: number;
  required_score: number;
  gap_score: number;
  current_level_id: string | null;
  current_level_number: number | null;
  current_level_name: string | null;
  required_level_id: string;
  required_level_number: number;
  required_level_name: string;
  confidence: number;
  confidence_flag: ConfidenceFlag;
  criticality: CriticalityLevel | string;
  task_relevance: TaskRelevanceLevel | string;
  mission_urgency: MissionUrgencyLevel | string;
  priority_score: number;
  priority_level: PriorityLevel;
  role_relevance: string | null;
  explanation: string;
  calculated_at: string;
  updated_at: string;
  priority_breakdown: PriorityBreakdown;
}

export interface SkillGapSummary {
  total_competencies: number;
  gaps_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  no_gap_count: number;
  average_gap: number;
  highest_priority_gap: SkillGap | null;
  last_calculated_at: string | null;
}

// =========================================================================
// STAGE 7: PERSONALIZED LEARNING & RECOMMENDATION ENGINE TYPES
// =========================================================================
export type LearningProviderType = 'IGOT' | 'NSSTA_TPAC' | 'PRAGYA';
export type LearningItemType = 'COURSE' | 'PROGRAMME' | 'LAB' | 'PATH';
export type LearningItemFormat = 'SELF_PACED' | 'INSTRUCTOR_LED' | 'BLENDED' | 'INTERACTIVE_LAB';
export type LearningDifficulty = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';
export type RecommendationStatus = 'ACTIVE' | 'STARTED' | 'COMPLETED' | 'DISMISSED';
export type LearningPathStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'ARCHIVED';

export interface LearningItemCompetencyMapping {
  competency_id: string;
  competency_code: string | null;
  competency_name: string | null;
  domain_name: string | null;
  coverage_level: 'INTRODUCTORY' | 'FOUNDATION' | 'WORKING' | 'ADVANCED' | string;
  learning_outcome: string | null;
}

export interface LearningItem {
  id: string;
  provider: LearningProviderType | string;
  provider_item_id: string;
  title: string;
  description: string;
  type: LearningItemType | string;
  difficulty: LearningDifficulty | string;
  level: number;
  duration_minutes: number;
  language: string;
  format: LearningItemFormat | string;
  url: string | null;
  prerequisites: Array<Record<string, unknown>>;
  is_active: boolean;
  source_mode: 'MOCK' | 'LIVE';
  item_metadata: Record<string, unknown>;
  competencies: LearningItemCompetencyMapping[];
  created_at: string;
  updated_at: string;
}

export interface RecommendationBreakdown {
  gap_priority_component: number;
  semantic_match_component: number;
  level_fit_component: number;
  outcome_coverage_component: number;
  prerequisite_fit_component: number;
  duration_fit_component: number;
  novelty_component: number;
}

export interface RecommendationReason {
  summary: string;
  gap_reason: string;
  role_reason: string;
  competency_reason: string;
  level_reason: string;
  novelty_reason: string;
}

export interface LearningRecommendation {
  id: string;
  employee_id: string;
  learning_item_id: string;
  target_competency_id: string;
  target_competency_name: string;
  target_competency_code: string;
  domain_name: string;
  learning_item: LearningItem;
  gap_id: string | null;
  gap_score: number | null;
  score: number;
  rank: number;
  reason: string;
  structured_reason: RecommendationReason;
  priority_breakdown: RecommendationBreakdown;
  matched_competencies: Array<Record<string, unknown>>;
  priority_level: PriorityLevel | string;
  status: RecommendationStatus | string;
  expires_at: string | null;
  generated_at: string;
  updated_at: string;
}

export interface LearningPathItem {
  id: string;
  learning_item_id: string;
  sequence_order: number;
  reason: string;
  target_competency_id: string;
  target_competency_name?: string | null;
  target_competency_code?: string | null;
  estimated_duration: number;
  status: LearningPathStatus | string;
  learning_item: LearningItem;
}

export interface LearningPath {
  id: string;
  employee_id: string;
  target_role_id: string | null;
  target_role_name: string | null;
  title: string;
  description: string;
  status: string;
  items: LearningPathItem[];
  generated_at: string;
  updated_at: string;
}

export interface ProviderInfo {
  provider: LearningProviderType | string;
  name: string;
  mode: 'MOCK' | 'LIVE';
  status: 'AVAILABLE' | 'MAINTENANCE' | 'DEGRADED';
  description: string;
  catalogue_count: number;
}

// ============================================================================
// Stage 8: Document Intelligence & RAG Retrieval Types
// ============================================================================

export type MaterialStatus =
  | 'UPLOADED'
  | 'PROCESSING'
  | 'PROCESSED'
  | 'FAILED'
  | 'DELETED';

export type DocumentType = 'PDF' | 'PPT' | 'PPTX' | 'TXT';

export interface DocumentSummary {
  id: string;
  uploaded_material_id: string;
  document_type: DocumentType;
  title: string;
  page_count?: number | null;
  slide_count?: number | null;
  language: string;
  processing_version: string;
  created_at: string;
}

export interface UploadedMaterial {
  id: string;
  employee_id: string;
  original_filename: string;
  mime_type: string;
  file_size: number;
  checksum_sha256: string;
  status: MaterialStatus;
  error_code?: string | null;
  created_at: string;
  updated_at: string;
  documents?: DocumentSummary[];
}

export interface PaginatedMaterials {
  items: UploadedMaterial[];
  total: number;
  skip: number;
  limit: number;
}

export interface MaterialStatusDetail {
  material_id: string;
  status: MaterialStatus;
  error_code?: string | null;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  text: string;
  page_number?: number | null;
  slide_number?: number | null;
  section_title?: string | null;
  token_count?: number | null;
  competency_id?: string | null;
  metadata: Record<string, unknown>;
}

export interface RAGSearchRequest {
  query: string;
  top_k?: number;
  document_id?: string | null;
  competency_id?: string | null;
}

export interface RAGSearchResultItem {
  chunk_id: string;
  document_id: string;
  text: string;
  score: number;
  page_number?: number | null;
  slide_number?: number | null;
  section_title?: string | null;
  document_title: string;
}

export interface RAGSearchResponse {
  query: string;
  results: RAGSearchResultItem[];
  retrieval_mode: string;
  status?: string;
  message?: string | null;
  warning?: string | null;
}

// ==================================================
// STAGE 9: AI LEARNING ASSISTANT TYPES
// ==================================================

export type AssistantContextType =
  | 'GENERAL_LEARNING'
  | 'COURSE'
  | 'MATERIAL'
  | 'COMPETENCY'
  | 'SKILL_GAP';

export type AssistantMessageRole = 'USER' | 'ASSISTANT' | 'SYSTEM';

export type AssistantGroundingStatus =
  | 'GROUNDED'
  | 'PARTIALLY_GROUNDED'
  | 'INSUFFICIENT_EVIDENCE'
  | 'ERROR';

export type AssistantExplanationLevel = 'FOUNDATION' | 'WORKING' | 'ADVANCED';

export type AssistantIntent =
  | 'EXPLAIN'
  | 'DEFINE'
  | 'SUMMARIZE'
  | 'EXAMPLE'
  | 'HINT'
  | 'PRACTICE'
  | 'REVISE'
  | 'COMPARE';

export interface AssistantSource {
  id: string;
  message_id: string;
  document_id: string;
  chunk_id: string;
  page_number?: number | null;
  slide_number?: number | null;
  similarity_score: number;
  citation_label: string;
  created_at: string;
  document_title?: string;
  snippet?: string;
}

export interface AssistantMessage {
  id: string;
  conversation_id: string;
  role: AssistantMessageRole;
  content: string;
  created_at: string;
  metadata?: {
    grounding_status?: AssistantGroundingStatus;
    intent?: AssistantIntent;
    explanation_level?: AssistantExplanationLevel;
    model?: string;
    tokens_used?: number;
    explanation?: string | null;
    example?: string | null;
    raw_answer?: string;
  } | null;
  sources?: AssistantSource[];
}

export interface AssistantConversation {
  id: string;
  employee_id: string;
  title: string;
  context_type: AssistantContextType;
  course_id?: string | null;
  document_id?: string | null;
  competency_id?: string | null;
  skill_gap_id?: string | null;
  created_at: string;
  updated_at: string;
  message_count?: number;
  last_message?: AssistantMessage | null;
  messages?: AssistantMessage[];
}

export interface CreateConversationRequest {
  title?: string;
  context_type?: AssistantContextType;
  course_id?: string | null;
  document_id?: string | null;
  competency_id?: string | null;
  skill_gap_id?: string | null;
  initial_query?: string;
}

export interface SendMessageRequest {
  content: string;
  document_id?: string | null;
  competency_id?: string | null;
  course_id?: string | null;
  skill_gap_id?: string | null;
  language?: string;
}

export interface AssistantResponse {
  conversation_id: string;
  user_message: AssistantMessage;
  assistant_message: AssistantMessage;
  answer: string;
  explanation?: string | null;
  example?: string | null;
  citations: AssistantSource[];
  grounding_status: AssistantGroundingStatus;
  retrieval_used: boolean;
  retrieval_count: number;
  model: string;
  context_type: AssistantContextType;
  explanation_level: AssistantExplanationLevel;
  intent: AssistantIntent;
}

// ============================================================================
// Stage 10: AI Quiz + MCQ Generation Engine Types
// ============================================================================

export type QuizDifficulty = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED';

export type BloomLevel =
  | 'REMEMBER'
  | 'UNDERSTAND'
  | 'APPLY'
  | 'ANALYZE'
  | 'EVALUATE'
  | 'CREATE';

export type QuizStatus = 'DRAFT' | 'READY' | 'IN_PROGRESS' | 'COMPLETED' | 'ARCHIVED';

export type QuestionType = 'MCQ_SINGLE' | 'MCQ_MULTI';

export type AttemptStatus = 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';

export interface QuestionOptionSummary {
  id: string;
  question_id: string;
  option_text: string;
  option_order: number;
  is_correct?: boolean;
}

export interface QuizQuestionSummary {
  id: string;
  quiz_id: string;
  question_text: string;
  question_type: QuestionType;
  difficulty: QuizDifficulty;
  bloom_level: BloomLevel;
  competency_id?: string | null;
  source_document_id: string;
  source_chunk_id?: string | null;
  source_page_number?: number | null;
  explanation?: string;
  options: QuestionOptionSummary[];
  document_title?: string;
  competency_name?: string;
}

export interface QuizSummary {
  id: string;
  employee_id?: string | null;
  title: string;
  description?: string | null;
  source_document_id?: string | null;
  competency_id?: string | null;
  question_count: number;
  difficulty: QuizDifficulty;
  status: QuizStatus;
  created_at: string;
  updated_at: string;
  document_title?: string;
  competency_name?: string;
}

export interface QuizDetail extends QuizSummary {
  questions: QuizQuestionSummary[];
}

export interface GenerateQuizRequest {
  document_id?: string | null;
  material_id?: string | null;
  competency_id?: string | null;
  difficulty?: QuizDifficulty;
  question_count?: number;
  bloom_level?: BloomLevel;
}

export interface QuizAttemptSummary {
  id: string;
  quiz_id: string;
  employee_id: string;
  started_at: string;
  completed_at?: string | null;
  score?: number | null;
  percentage?: number | null;
  status: AttemptStatus;
  quiz_title?: string;
}

export interface SubmitAnswerRequest {
  question_id: string;
  selected_option_id: string;
}

export interface AnswerResponse {
  response_id: string;
  question_id: string;
  selected_option_id: string;
  is_correct: boolean;
  correct_option_id: string;
  explanation: string;
  citation?: {
    document_title?: string;
    page_number?: number | null;
  };
}

export interface QuizResultResponse {
  attempt_id: string;
  quiz_id: string;
  score: number;
  total_questions: number;
  percentage: number;
  completed_at: string;
  competencies_tested: string[];
  difficulty_distribution: Record<string, number>;
}

export interface QuizReviewItem {
  question_id: string;
  question_text: string;
  selected_option_id: string;
  correct_option_id: string;
  is_correct: boolean;
  options: QuestionOptionSummary[];
  explanation: string;
  source_document_title?: string;
  source_page_number?: number | null;
}

export interface QuizReviewResponse {
  attempt_id: string;
  quiz_id: string;
  score: number;
  percentage: number;
  items: QuizReviewItem[];
}

// ============================================================================
// Stage 11: Adaptive Assessment & Closed-Loop Recalibration Types
// ============================================================================

export interface AdaptiveSessionCreateRequest {
  competency_id: string;
  source_document_id?: string | null;
}

export interface AdaptiveQuestionOption {
  id: string;
  option_text: string;
  option_order: number;
}

export interface AdaptiveQuestionPresentation {
  id: string;
  session_id: string;
  question_text: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string;
  bloom_level: string;
  question_number: number;
  total_target_questions: number;
  options: AdaptiveQuestionOption[];
  source_document_title?: string | null;
  source_page_number?: number | null;
}

export interface AdaptiveSubmitAnswerRequest {
  question_id: string;
  selected_option_id: string;
  response_time_ms?: number | null;
}

export interface AdaptiveSubmitAnswerResponse {
  response_id: string;
  session_id: string;
  question_id: string;
  selected_option_id: string;
  is_correct: boolean;
  correct_option_id: string;
  explanation: string;
  current_difficulty: string;
  next_difficulty: string;
  question_count: number;
  confidence: number;
  can_complete: boolean;
  should_stop: boolean;
  stop_reason?: string | null;
}

export interface AdaptiveSessionSummary {
  id: string;
  employee_id: string;
  competency_id: string;
  competency_name?: string | null;
  source_document_id?: string | null;
  source_document_title?: string | null;
  initial_level: string;
  current_level: string;
  question_count: number;
  correct_count: number;
  incorrect_count: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED' | string;
  confidence: number;
  started_at: string;
  completed_at?: string | null;
}

export interface RecalibrationResultResponse {
  session_id: string;
  competency_id: string;
  competency_name: string;
  previous_score: number;
  assessment_score: number;
  recalibrated_score: number;
  delta: number;
  confidence: number;
  reason: string;
  questions_answered: number;
  correct_count: number;
  incorrect_count: number;
  difficulty_distribution: Record<string, number>;
  updated_gap_score?: number | null;
  updated_priority_level?: string | null;
  updated_priority_score?: number | null;
  completed_at: string;
}

// ============================================================================
// Stage 12: PRAGYA Statistical Virtual Lab Types
// ============================================================================

export type LabScenarioType =
  | 'DATA_QUALITY_AUDIT'
  | 'SURVEY_SAMPLING'
  | 'DESCRIPTIVE_STATISTICS'
  | 'MISSING_DATA_ANALYSIS'
  | string;

export interface LabDatasetSummary {
  id: string;
  title: string;
  description: string;
  scenario_type: LabScenarioType;
  row_count: number;
  is_synthetic: boolean;
  schema_definition: Record<string, any>;
}

export interface LabDatasetDetail extends LabDatasetSummary {
  dataset_json: Array<Record<string, any>>;
}

export interface LabScenarioSummary {
  id: string;
  title: string;
  description: string;
  scenario_type: LabScenarioType;
  competency_id: string;
  competency_name?: string | null;
  competency_code?: string | null;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string;
  estimated_minutes: number;
  learning_objectives: string[];
  status: 'READY' | 'DRAFT' | 'ARCHIVED' | string;
  dataset_id: string;
  dataset_row_count: number;
  is_synthetic: boolean;
  created_at: string;
}

export interface LabScenarioStep {
  step_number: number;
  title: string;
  description: string;
  task_instructions: string;
  action_type: string;
}

export interface LabScenarioDetail extends LabScenarioSummary {
  instructions: {
    overview: string;
    total_steps: number;
    steps: LabScenarioStep[];
  };
  dataset: LabDatasetDetail;
}

export interface LabActionResponse {
  id: string;
  session_id: string;
  step_number: number;
  action_type: string;
  action_payload: Record<string, any>;
  is_correct: boolean;
  score_awarded: number;
  feedback: string;
  created_at: string;
}

export interface LabSessionResponse {
  id: string;
  employee_id: string;
  scenario_id: string;
  scenario_title: string;
  scenario_type: LabScenarioType;
  difficulty: string;
  competency_id: string;
  competency_name?: string | null;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED' | string;
  current_step: number;
  total_steps: number;
  score?: number | null;
  percentage?: number | null;
  confidence?: number | null;
  started_at: string;
  completed_at?: string | null;
  actions: LabActionResponse[];
}

export interface LabActionSubmitRequest {
  step_number: number;
  action_type: string;
  action_payload?: Record<string, any>;
}

export interface LabActionEvaluationResult {
  action_id: string;
  session_id: string;
  step_number: number;
  action_type: string;
  is_correct: boolean;
  score_awarded: number;
  feedback: string;
  current_score: number;
  next_step: number;
  is_completed: boolean;
  data_preview?: Array<Record<string, any>> | null;
  metrics?: Record<string, any> | null;
}

export interface LabCompleteResponse {
  session_id: string;
  scenario_id: string;
  scenario_title?: string | null;
  scenario_type?: LabScenarioType;
  difficulty?: string;
  total_score: number;
  percentage: number;
  passed: boolean;
  confidence: number;
  competency_id?: string | null;
  competency_name?: string | null;
  evidence_id?: string | null;
  actions_completed?: number;
  correct_actions?: number;
  incorrect_actions?: number;
  actions_history?: LabActionResponse[];
  learning_feedback?: string[];
  summary_metrics?: Record<string, unknown>;
  completed_at: string;
  message: string;
}

export interface LabResultDetail {
  id: string;
  session_id: string;
  scenario_id: string;
  scenario_title: string;
  scenario_type: LabScenarioType;
  difficulty: string;
  total_score: number;
  percentage: number;
  passed: boolean;
  confidence: number;
  competency_id?: string | null;
  competency_name?: string | null;
  evidence_id?: string | null;
  actions_completed: number;
  correct_actions: number;
  incorrect_actions: number;
  actions_history: LabActionResponse[];
  learning_feedback: string[];
  summary_metrics?: Record<string, unknown>;
  created_at: string;
}

export interface LabHintResponse {
  step_number: number;
  hint: string;
  guidance: string;
}

export interface CourseResource {
  id: string;
  title: string;
  type: 'VIDEO' | 'READING';
  duration?: string;
  duration_seconds?: number;
  duration_display?: string;
  read_time?: string;
  description?: string;
  provider?: string;
  external_provider?: string;
  external_resource_id?: string | null;
  external_url?: string | null;
  completion_required?: boolean;
  completion_status?: string;
  verification_status?: string;
  url?: string;
  video_url?: string;
  source_type?: string;
  summary?: string;
  content_markdown?: string;
  key_takeaways?: string[];
}

export interface ProviderSyncResponse {
  resource_id?: string | null;
  provider: string;
  verified: boolean;
  status: string;
  reason: string;
  message: string;
  completed_at?: string | null;
  certificate_id?: string | null;
}

export interface ResourceLaunchResponse {
  resource_id: string;
  status: string;
  verification_status: string;
  provider: string;
  external_url?: string | null;
  message: string;
}

export interface CourseModule {
  id: number;
  title: string;
  description: string;
  duration: string;
  is_lab: boolean;
  lab_scenario_id?: string;
  resources?: CourseResource[];
  knowledge_check?: {
    module_id: number;
    title: string;
    pass_threshold?: number;
    pass_threshold_percentage?: number;
    questions: Array<{
      id: string;
      question: string;
      options: string[];
      correct_index: number;
      explanation: string;
    }>;
  };
  assignment?: {
    module_id: number;
    title: string;
    description: string;
    scenario: Record<string, unknown>;
    pass_threshold: number;
    rubric?: Array<{ criterion: string; weight: number; description: string }>;
  };
}

export interface FinalAssessmentData {
  title?: string;
  description?: string;
  pass_threshold_percentage?: number;
  questions?: Array<{
    id: string;
    question: string;
    options: string[];
    explanation?: string;
  }>;
}

export interface CourseCurriculumResponse {
  learning_item_id: string;
  course_title: string;
  course_code: string;
  is_demo_content: boolean;
  modules: CourseModule[];
  final_assessment: FinalAssessmentData;
}

export interface CourseResourceProgressPayload {
  module_id: number;
  resource_type: 'VIDEO' | 'READING';
  progress_seconds: number;
  duration_seconds: number;
  progress_percentage: number;
  is_completed: boolean;
}

export interface CourseResourceProgressItem {
  resource_id?: string;
  module_id: number;
  resource_type: string;
  progress_seconds: number;
  duration_seconds: number;
  progress_percentage: number;
  is_completed: boolean;
  provider?: string;
  status?: string;
  verification_status?: string;
  external_resource_id?: string | null;
  external_url?: string | null;
  completed_at?: string | null;
}

export interface QuestionEvaluationResult {
  question_id: string;
  selected_index: number;
  correct_index: number;
  is_correct: boolean;
  explanation: string;
}

export interface KnowledgeCheckResultResponse {
  module_id: number;
  total_questions: number;
  correct_answers: number;
  score: number;
  percentage: number;
  passed: boolean;
  pass_threshold: number;
  question_results: QuestionEvaluationResult[];
  module_completed: boolean;
}

export interface AssignmentResultResponse {
  module_id: number;
  score: number;
  max_score: number;
  percentage: number;
  passed: boolean;
  feedback: string;
  rubric_breakdown: Record<string, unknown>;
  evidence_id?: string | null;
  module_completed: boolean;
}

export interface FinalAssessmentResultResponse {
  total_questions: number;
  correct_answers: number;
  score: number;
  percentage: number;
  passed: boolean;
  pass_threshold: number;
  question_results: QuestionEvaluationResult[];
  evidence_id?: string | null;
}

export interface CourseProgressResponse {
  learning_item_id: string;
  employee_id: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED';
  progress_percentage: number;
  completed_modules: number[];
  unlocked_modules: number[];
  resource_progress: Record<string, CourseResourceProgressItem>;
  activities_status: {
    m1_kc_passed: boolean;
    m2_assignment_passed: boolean;
    m2_kc_passed: boolean;
    m3_kc_passed: boolean;
    m4_lab_verified: boolean;
    final_assessment_passed: boolean;
  };
  is_lab_verified: boolean;
  final_assessment_passed: boolean;
  final_assessment_score?: number | null;
  course_completed: boolean;
  enrolled_at: string;
  completed_at?: string | null;
}

export interface CourseCompleteResponse {
  success: boolean;
  message: string;
  progress_percentage: number;
  completed_at: string;
  evidence_id?: string | null;
}

export interface RecalibrateCourseResponse {
  recalibrated: boolean;
  recalibrated_competencies: Array<{
    competency_id: string;
    competency_code?: string | null;
    competency_name?: string | null;
    current_score?: number;
    confidence?: number;
    confidence_label?: string;
    error?: string;
  }>;
  message: string;
}

// ============================================================================
// Stage 13: Employee Performance Analysis & Longitudinal Tracking Interfaces
// ============================================================================

export interface OverallPerformanceSummary {
  baseline_score?: number | null;
  current_score: number;
  target_score?: number | null;
  improvement_points: number;
  improvement_percentage: number;
  competencies_evaluated: number;
  competencies_with_baseline: number;
  target_readiness_percentage?: number | null;
}

export type PerformanceStatus =
  | 'MASTERED'
  | 'IMPROVING'
  | 'STABLE'
  | 'NEEDS_FOCUS'
  | 'NO_BASELINE';

export interface CompetencyPerformanceDetail {
  competency_id: string;
  competency_code: string;
  competency_name: string;
  domain_id?: string | null;
  domain_name?: string | null;
  baseline_score?: number | null;
  current_score: number;
  target_score?: number | null;
  improvement_points: number;
  improvement_percentage: number;
  status: PerformanceStatus | string;
  confidence: number;
  confidence_label: string;
  last_assessed_at?: string | null;
  evidence_count: number;
}

export interface CompetencyStrengthItem {
  competency_id: string;
  competency_code: string;
  competency_name: string;
  domain_name?: string | null;
  current_score: number;
  improvement_points: number;
  rank: number;
  highlight: string;
}

export interface CompetencyFocusItem {
  competency_id: string;
  competency_code: string;
  competency_name: string;
  domain_name?: string | null;
  current_score: number;
  target_score?: number | null;
  gap_score: number;
  priority_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NO_GAP' | string;
  priority_score: number;
  explanation: string;
}

export interface DiagnosticModalitySummary {
  attempts_count: number;
  completed_count: number;
  average_score?: number | null;
  latest_score?: number | null;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'NO_DATA' | string;
}

export interface QuizModalitySummary {
  attempts_count: number;
  completed_count: number;
  average_percentage?: number | null;
  best_percentage?: number | null;
  pass_rate?: number | null;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'NO_DATA' | string;
}

export interface AdaptiveModalitySummary {
  sessions_count: number;
  completed_count: number;
  average_confidence?: number | null;
  competencies_evaluated_count: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'NO_DATA' | string;
}

export interface LabModalitySummary {
  sessions_count: number;
  completed_count: number;
  average_score?: number | null;
  pass_rate?: number | null;
  completed_scenarios_count: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'NO_DATA' | string;
}

export interface CourseModalitySummary {
  enrolled_courses_count: number;
  completed_courses_count: number;
  average_progress_percentage?: number | null;
  completed_modules_count: number;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'NO_DATA' | string;
}

export interface ModalitiesSummary {
  diagnostic: DiagnosticModalitySummary;
  quizzes: QuizModalitySummary;
  adaptive_assessment: AdaptiveModalitySummary;
  virtual_labs: LabModalitySummary;
  courses: CourseModalitySummary;
}

export interface PerformanceCountsSummary {
  competencies_improved: number;
  competencies_declined: number;
  competencies_mastered: number;
  competencies_needing_focus: number;
  total_competencies: number;
}

export interface EmployeePerformanceResponse {
  employee_id: string;
  employee_name: string;
  job_role_id?: string | null;
  job_role_name?: string | null;
  department_name?: string | null;
  overall: OverallPerformanceSummary;
  competencies: CompetencyPerformanceDetail[];
  strongest_competencies: CompetencyStrengthItem[];
  focus_competencies: CompetencyFocusItem[];
  modalities: ModalitiesSummary;
  summary: PerformanceCountsSummary;
  generated_at: string;
}

export type TimelineEventType =
  | 'DIAGNOSTIC_ASSESSMENT'
  | 'QUIZ'
  | 'ADAPTIVE_ASSESSMENT'
  | 'VIRTUAL_LAB'
  | 'COURSE_ACTIVITY'
  | 'COMPETENCY_RECALIBRATION'
  | 'SCORE_UPDATE';

export interface TimelineEventItem {
  id: string;
  timestamp: string;
  type: TimelineEventType | string;
  title: string;
  description: string;
  score?: number | null;
  max_score?: number | null;
  percentage?: number | null;
  competency_id?: string | null;
  competency_name?: string | null;
  source: string;
  status?: string | null;
  metadata?: Record<string, any> | null;
}

export interface EmployeeTimelineResponse {
  employee_id: string;
  total_events: number;
  events: TimelineEventItem[];
}

// =============================================================================
// STAGE 14: ADMINISTRATOR WORKFORCE INTELLIGENCE & CADRE ANALYTICS
// =============================================================================

export interface WorkforceOverview {
  total_employees: number;
  active_employees: number;
  departments_count: number;
  roles_count: number;
  competencies_tracked: number;
  employees_assessed: number;
  employees_with_competencies: number;
  average_competency_score: number | null;
  average_role_readiness: number | null;
  employees_needing_attention: number;
}

export interface WorkforceCompetencyItem {
  competency_id: string;
  code: string;
  name: string;
  domain: string;
  employee_count: number;
  average_score: number;
  minimum_score: number;
  maximum_score: number;
  proficiency_distribution: Record<string, number>;
  gap_count: number;
  critical_gap_count: number;
}

export interface WorkforceCompetenciesResponse {
  competencies: WorkforceCompetencyItem[];
  total_tracked: number;
}

export interface DepartmentAnalyticsItem {
  department_id: string;
  department_name: string;
  department_code: string;
  employee_count: number;
  average_competency_score: number | null;
  average_role_readiness: number | null;
  average_skill_gap_score: number | null;
  critical_gap_count: number;
  high_gap_count: number;
  top_competency_strengths: string[];
  top_competency_gaps: string[];
}

export interface DepartmentAnalyticsResponse {
  departments: DepartmentAnalyticsItem[];
}

export interface DepartmentHeatmapCompetencyItem {
  competency_id: string;
  competency_name: string;
  competency_code: string;
  domain_name: string;
  average_score: number | null;
  gap_level: string; // 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NO_GAP' | 'NO_DATA'
  employee_count: number;
}

export interface DepartmentHeatmapDepartmentItem {
  department_id: string;
  department_name: string;
  department_code: string;
  employee_count: number;
  competencies: DepartmentHeatmapCompetencyItem[];
}

export interface DepartmentHeatmapResponse {
  departments: DepartmentHeatmapDepartmentItem[];
  competencies_reference: Array<{
    id: string;
    code: string;
    name: string;
    domain: string;
  }>;
}

export interface WorkforceGapSummaryItem {
  competency_id: string;
  competency_name: string;
  competency_code: string;
  domain_name: string;
  affected_employees: number;
  average_gap_score: number;
  highest_priority_level: string;
}

export interface WorkforceGapsResponse {
  total_gaps: number;
  critical_gaps: number;
  high_gaps: number;
  medium_gaps: number;
  low_gaps: number;
  no_gap_count: number;
  top_workforce_gaps: WorkforceGapSummaryItem[];
}

export interface RoleAnalyticsItem {
  role_id: string;
  role_name: string;
  role_code: string;
  career_level: string;
  employee_count: number;
  average_competency_score: number | null;
  average_role_readiness: number | null;
  competency_requirements_count: number;
  major_skill_gaps: string[];
  employees_below_target: number;
}

export interface RoleAnalyticsResponse {
  roles: RoleAnalyticsItem[];
}

export interface TopCourseLearningItem {
  course_id: string;
  course_code: string;
  title: string;
  provider: string;
  enrolled_count: number;
  completed_count: number;
  completion_rate: number;
  average_progress: number;
}

export interface WorkforceTrainingOverviewResponse {
  total_learners: number;
  total_enrollments: number;
  completed_courses_count: number;
  average_learning_progress: number;
  total_learning_activities: number;
  top_courses: TopCourseLearningItem[];
  employees_with_competency_growth: number;
}

export interface AdminEmployeeListItem {
  id: string;
  employee_code: string;
  full_name: string;
  designation: string;
  department_name: string;
  role_name: string;
  average_competency: number | null;
  role_readiness: number | null;
  critical_gaps_count: number;
  needs_attention: boolean;
}

export interface AdminEmployeeListResponse {
  employees: AdminEmployeeListItem[];
  total: number;
}

// =============================================================================
// STAGE 15: TRAINING EFFECTIVENESS & RECOMMENDATION ANALYTICS
// =============================================================================

export interface CompetencyImprovementSummary {
  competency_id: string;
  competency_code: string;
  competency_name: string;
  domain_name: string;
  measurable_learners: number;
  average_pre_score: number | null;
  average_post_score: number | null;
  average_improvement: number | null;
  improvement_percentage: number | null;
}

export interface CourseEffectivenessItem {
  course_id: string;
  course_code: string;
  title: string;
  provider: string;
  duration_hours: number | null;
  enrolled_count: number;
  completed_count: number;
  completion_rate: number;
  measurable_learners: number;
  average_pre_score: number | null;
  average_post_score: number | null;
  average_improvement: number | null;
  improvement_percentage: number | null;
  effectiveness_index: number | null;
  effectiveness_status: 'HIGH_EFFECTIVENESS' | 'MODERATE_EFFECTIVENESS' | 'LOW_EFFECTIVENESS' | 'INSUFFICIENT_DATA' | 'NO_DATA';
  competencies_affected: string[];
}

export interface CourseEffectivenessResponse {
  courses: CourseEffectivenessItem[];
  total_courses: number;
}

export interface RecommendationOutcomesSummary {
  recommendations_issued: number;
  recommendations_started: number;
  recommendations_completed: number;
  measurable_recommendations: number;
  recommendations_with_improvement: number;
  start_rate: number;
  completion_rate: number;
  improvement_rate: number;
  average_observed_improvement: number | null;
  by_priority: Record<string, number>;
}

export interface RecommendationEffectivenessResponse {
  summary: RecommendationOutcomesSummary;
}

export interface OverallTrainingEffectivenessResponse {
  total_learners: number;
  total_enrollments: number;
  completed_enrollments: number;
  completion_rate: number;
  measurable_interventions: number;
  effective_interventions: number;
  average_observed_improvement: number | null;
  average_improvement_percentage: number | null;
  competencies_improved_count: number;
  competency_improvements: CompetencyImprovementSummary[];
  top_effective_courses: CourseEffectivenessItem[];
  recommendation_summary: RecommendationOutcomesSummary;
}

export interface EmployeeCourseEffectivenessItem {
  course_id: string;
  course_title: string;
  status: string;
  enrolled_at: string;
  completed_at: string | null;
  competency_name: string;
  pre_training_score: number | null;
  post_training_score: number | null;
  improvement_points: number | null;
  improvement_percentage: number | null;
  status_label: 'OBSERVED_IMPROVEMENT' | 'NO_CHANGE' | 'DECLINE' | 'NO_BASELINE' | 'NO_POST_DATA' | 'NO_DATA' | string;
}

export interface EmployeeTrainingEffectivenessResponse {
  employee_id: string;
  employee_code: string;
  full_name: string;
  designation: string;
  interventions: EmployeeCourseEffectivenessItem[];
  total_interventions: number;
  average_observed_improvement: number | null;
}

// =============================================================================
// STAGE 16: EMERGING SKILLS & TECHNOLOGY HORIZON SCANNING
// =============================================================================

export interface EmergingSkillItem {
  competency_id: string;
  code: string;
  name: string;
  domain_id: string;
  domain_name: string;
  signal_score: number;
  affected_employees: number;
  gap_frequency: number;
  recommendation_frequency: number;
  training_demand: number;
  role_coverage: number;
  catalogue_coverage: number;
  status: 'EMERGING' | 'WATCH' | 'ESTABLISHED' | 'INSUFFICIENT_DATA';
  signals: string[];
}

export interface EmergingSkillsResponse {
  skills: EmergingSkillItem[];
  total_analyzed: number;
  emerging_count: number;
  watch_count: number;
  established_count: number;
  insufficient_data_count: number;
  methodology: string;
}

// =============================================================================
// STAGE 17: PREDICTIVE WORKFORCE PLANNING & CAPACITY FORECASTING
// =============================================================================

export interface PlanningDataQuality {
  historical_periods: number;
  records_used: number;
  status: 'SUFFICIENT' | 'INSUFFICIENT_DATA';
  quality_grade: 'HIGH' | 'MEDIUM' | 'LOW';
}

export interface WorkforcePopulationMetrics {
  total_employees: number;
  active_employees: number;
  departments_count: number;
  roles_count: number;
  competencies_tracked: number;
}

export interface WorkforceCapacityMetrics {
  employees_with_gaps: number;
  employees_learning: number;
  employees_with_improvement: number;
  average_role_readiness: number;
  overall_planning_pressure: number;
}

export interface WorkforcePlanningOverviewResponse {
  status: string;
  population: WorkforcePopulationMetrics;
  capacity: WorkforceCapacityMetrics;
  data_quality: PlanningDataQuality;
}

export interface WorkforceTrendPeriod {
  period: string;
  period_start: string;
  period_end: string;
  average_competency_score: number;
  employees_meeting_target: number;
  employees_below_target: number;
  active_skill_gaps: number;
  learning_participation: number;
  observed_improvement: number;
}

export interface WorkforceTrendsResponse {
  status: 'OK' | 'INSUFFICIENT_DATA';
  message?: string | null;
  periods_count: number;
  trends: WorkforceTrendPeriod[];
  data_quality: PlanningDataQuality;
}

export interface ForecastMethodology {
  type: string;
  historical_window: string;
  signals: string[];
  assumptions: string[];
  data_quality: string;
  limitations: string[];
}

export interface WorkforceCapacityForecastResponse {
  current_capacity: number;
  total_workforce: number;
  current_capacity_percentage: number;
  estimated_capacity_requirement: number;
  capacity_gap: number;
  projected_gap: number;
  overall_pressure_index: number;
  priority_competencies: string[];
  priority_roles: string[];
  priority_departments: string[];
  methodology: ForecastMethodology;
}

export interface CompetencyCapacityForecastItem {
  competency_id: string;
  name: string;
  domain: string;
  current_coverage: number;
  target_coverage: number;
  gap_population: number;
  learning_demand: number;
  emerging_signal: number;
  planning_pressure: number;
  status: 'HIGH_DEFICIT' | 'MODERATE_DEFICIT' | 'BALANCED' | 'INSUFFICIENT_DATA';
  rationale: string[];
}

export interface CompetencyCapacityForecastResponse {
  total_competencies: number;
  competencies: CompetencyCapacityForecastItem[];
  data_quality: PlanningDataQuality;
}

export interface RoleCapacityForecastItem {
  role_id: string;
  role_name: string;
  cadre_level?: string | null;
  employee_count: number;
  required_competencies_count: number;
  employees_meeting_target: number;
  employees_below_target: number;
  critical_skill_gaps: number;
  learning_demand: number;
  readiness_signal: number;
  projected_capacity_pressure: number;
  status: 'HIGH_PRESSURE' | 'MODERATE_PRESSURE' | 'ADEQUATE';
  rationale: string[];
}

export interface RoleCapacityForecastResponse {
  total_roles: number;
  roles: RoleCapacityForecastItem[];
  data_quality: PlanningDataQuality;
}

export interface DepartmentCapacityForecastItem {
  department_id: string;
  department_name: string;
  code?: string | null;
  workforce_size: number;
  competency_coverage: number;
  major_skill_gaps: number;
  learning_demand: number;
  emerging_skill_pressure: number;
  projected_capacity_pressure: number;
  status: 'HIGH_PRESSURE' | 'MODERATE_PRESSURE' | 'BALANCED';
  rationale: string[];
}

export interface DepartmentCapacityForecastResponse {
  total_departments: number;
  departments: DepartmentCapacityForecastItem[];
  data_quality: PlanningDataQuality;
}

export interface PlanningRecommendationItem {
  id: string;
  type: 'COMPETENCY_TRAINING' | 'ROLE_CAPACITY' | 'DEPARTMENT_FOCUS' | 'HORIZON_MONITORING' | 'REASSESSMENT';
  title: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  affected_population: number;
  evidence_signals: string[];
  rationale: string;
  suggested_action: string;
  data_quality_status: string;
}

export interface PlanningRecommendationsResponse {
  total_recommendations: number;
  recommendations: PlanningRecommendationItem[];
  data_quality: PlanningDataQuality;
}

export interface EmployeePlanningTrajectoryPoint {
  timestamp: string;
  competency_name: string;
  score: number;
  source: string;
}

export interface EmployeePlanningDrilldownResponse {
  employee_id: string;
  full_name: string;
  employee_code?: string | null;
  designation?: string | null;
  department_name?: string | null;
  role_name?: string | null;
  current_average_score: number;
  role_readiness_percentage: number;
  active_gaps_count: number;
  learning_modules_completed: number;
  observed_improvement_points: number;
  readiness_indicator: 'READY' | 'DEVELOPING' | 'AT_RISK';
  historical_trajectory: EmployeePlanningTrajectoryPoint[];
  planning_signals: string[];
}



