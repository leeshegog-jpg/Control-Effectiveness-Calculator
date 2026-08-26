// Typed fetch wrappers over @sms/shared-types, one function per currently
// implemented OpenAPI operation -- see
// docs/implementation-blueprint/13-application-foundation-scaffold.md §4.
//
// Scope: the 46 operations that are both contracted in
// docs/knowledge-graph/10-openapi.yaml and actually route-registered on
// main as of commit 3424b2c. The remaining 67 contracted-but-unimplemented
// operations (Emergency Planning, Competency Management, Safety Case
// Demonstration, Document AI, Management of Change, Audits, Gap Analysis,
// Persons/Roles, Requirements coverage, critical-control sub-resources,
// asset boundary/interfaces) have no wrapper here -- adding one ahead of
// the corresponding API implementation would contract against endpoints
// that don't exist yet.
//
// Each wrapper's parameter type is the generated `<Operation>Data` type
// itself (minus the literal `url` field), so path/query/body shapes are
// never duplicated by hand -- they come straight from shared-types, which
// is generated straight from the frozen spec.

import type {
  DeleteIncidentsByIdActionsByActionIdData,
  DeleteIncidentsByIdActionsByActionIdResponse,
  DeleteIncidentsByIdHazardsByHazardIdData,
  DeleteIncidentsByIdHazardsByHazardIdResponse,
  GetActionsData,
  GetActionsResponse,
  GetAssetsByIdData,
  GetAssetsByIdResponse,
  GetAssetsData,
  GetAssetsResponse,
  GetControlsByIdData,
  GetControlsByIdResponse,
  GetCriticalControlsByIdData,
  GetCriticalControlsByIdPerformanceStandardsData,
  GetCriticalControlsByIdPerformanceStandardsResponse,
  GetCriticalControlsByIdResponse,
  GetHazardsByIdData,
  GetHazardsByIdResponse,
  GetHazardsData,
  GetHazardsResponse,
  GetIncidentsByIdActionsData,
  GetIncidentsByIdActionsResponse,
  GetIncidentsByIdData,
  GetIncidentsByIdEvidenceData,
  GetIncidentsByIdEvidenceResponse,
  GetIncidentsByIdHazardsData,
  GetIncidentsByIdHazardsResponse,
  GetIncidentsByIdInvestigationData,
  GetIncidentsByIdInvestigationResponse,
  GetIncidentsByIdResponse,
  GetIncidentsData,
  GetIncidentsResponse,
  GetOntologyConceptsData,
  GetOntologyConceptsResponse,
  GetOntologySchemesData,
  GetOntologySchemesResponse,
  GetPerformanceStandardsByIdVerificationActivitiesData,
  GetPerformanceStandardsByIdVerificationActivitiesResponse,
  GetRisksByIdData,
  GetRisksByIdResponse,
  GetRisksByRiskIdControlsData,
  GetRisksByRiskIdControlsResponse,
  GetRisksData,
  GetRisksResponse,
  GetVerificationActivitiesByIdEvidenceData,
  GetVerificationActivitiesByIdEvidenceResponse,
  PatchActionsByIdData,
  PatchActionsByIdResponse,
  PatchAssetsByIdData,
  PatchAssetsByIdResponse,
  PatchCriticalControlsByIdData,
  PatchCriticalControlsByIdResponse,
  PatchHazardsByIdData,
  PatchHazardsByIdResponse,
  PatchIncidentsByIdData,
  PatchIncidentsByIdInvestigationData,
  PatchIncidentsByIdInvestigationResponse,
  PatchIncidentsByIdResponse,
  PatchRisksByIdData,
  PatchRisksByIdResponse,
  PostActionsData,
  PostActionsResponse,
  PostAssetsData,
  PostAssetsResponse,
  PostControlsByIdCriticalControlTestData,
  PostControlsByIdCriticalControlTestResponse,
  PostControlsByIdEiaTestData,
  PostControlsByIdEiaTestResponse,
  PostControlsByIdGateTestData,
  PostControlsByIdGateTestResponse,
  PostCriticalControlsByIdPerformanceStandardsData,
  PostCriticalControlsByIdPerformanceStandardsResponse,
  PostHazardsData,
  PostHazardsResponse,
  PostIncidentsByIdActionsData,
  PostIncidentsByIdActionsResponses,
  PostIncidentsByIdEvidenceData,
  PostIncidentsByIdEvidenceResponse,
  PostIncidentsByIdHazardsData,
  PostIncidentsByIdHazardsResponses,
  PostIncidentsByIdInvestigationData,
  PostIncidentsByIdInvestigationResponse,
  PostIncidentsData,
  PostIncidentsResponse,
  PostPerformanceStandardsByIdVerificationActivitiesData,
  PostPerformanceStandardsByIdVerificationActivitiesResponse,
  PostRisksByRiskIdControlsData,
  PostRisksByRiskIdControlsResponse,
  PostRisksData,
  PostRisksResponse,
  PostVerificationActivitiesByIdEvidenceData,
  PostVerificationActivitiesByIdEvidenceResponse,
} from '@sms/shared-types';

export interface ApiClientConfig {
  /** Prefixed to every request URL. Defaults to '' (relative paths). */
  baseUrl?: string;
  /** Extra headers merged into every request. */
  headers?: HeadersInit;
  /** Override fetch (e.g. a mocked implementation in tests). Defaults to the global fetch. */
  fetch?: typeof fetch;
}

/** Thrown when the server responds with a non-2xx status. */
export class ApiError extends Error {
  readonly method: string;
  readonly url: string;
  readonly status: number;
  readonly body: string;

  constructor(method: string, url: string, status: number, body: string) {
    super(`${method} ${url} -> ${status}`);
    this.name = 'ApiError';
    this.method = method;
    this.url = url;
    this.status = status;
    this.body = body;
  }
}

/** Runtime shape shared by every generated `<Operation>Data` type, minus `url`. */
interface OperationOptions {
  path?: Record<string, string>;
  query?: Record<string, unknown>;
  body?: unknown;
}

function buildUrl(
  template: string,
  path: Record<string, string> | undefined,
  query: Record<string, unknown> | undefined,
  baseUrl: string,
): string {
  let pathname = template;
  if (path) {
    for (const [key, value] of Object.entries(path)) {
      pathname = pathname.replace(`{${key}}`, encodeURIComponent(value));
    }
  }
  const url = new URL(pathname, baseUrl || 'http://localhost');
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
  }
  return baseUrl ? url.toString() : url.pathname + url.search;
}

async function request<TResponse>(
  config: ApiClientConfig | undefined,
  method: string,
  urlTemplate: string,
  options: OperationOptions,
): Promise<TResponse> {
  const fetchImpl = config?.fetch ?? fetch;
  const baseUrl = config?.baseUrl ?? '';
  const href = buildUrl(urlTemplate, options.path, options.query, baseUrl);

  const headers = new Headers(config?.headers);
  const init: RequestInit = { method, headers };
  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
    init.body = JSON.stringify(options.body);
  }

  const response = await fetchImpl(href, init);
  if (!response.ok) {
    throw new ApiError(method, href, response.status, await response.text());
  }
  if (response.status === 204) return undefined as TResponse;
  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as TResponse;
}


export function deleteIncidentsByIdActionsByActionId(
  data: Omit<DeleteIncidentsByIdActionsByActionIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<DeleteIncidentsByIdActionsByActionIdResponse> {
  return request(config, 'DELETE', '/incidents/{id}/actions/{actionId}', data as OperationOptions);
}

export function deleteIncidentsByIdHazardsByHazardId(
  data: Omit<DeleteIncidentsByIdHazardsByHazardIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<DeleteIncidentsByIdHazardsByHazardIdResponse> {
  return request(config, 'DELETE', '/incidents/{id}/hazards/{hazardId}', data as OperationOptions);
}

export function getActions(
  data: Omit<GetActionsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetActionsResponse> {
  return request(config, 'GET', '/actions', data as OperationOptions);
}

export function getAssets(
  data: Omit<GetAssetsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetAssetsResponse> {
  return request(config, 'GET', '/assets', data as OperationOptions);
}

export function getAssetsById(
  data: Omit<GetAssetsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetAssetsByIdResponse> {
  return request(config, 'GET', '/assets/{id}', data as OperationOptions);
}

export function getControlsById(
  data: Omit<GetControlsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetControlsByIdResponse> {
  return request(config, 'GET', '/controls/{id}', data as OperationOptions);
}

export function getCriticalControlsById(
  data: Omit<GetCriticalControlsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetCriticalControlsByIdResponse> {
  return request(config, 'GET', '/critical-controls/{id}', data as OperationOptions);
}

export function getCriticalControlsByIdPerformanceStandards(
  data: Omit<GetCriticalControlsByIdPerformanceStandardsData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetCriticalControlsByIdPerformanceStandardsResponse> {
  return request(config, 'GET', '/critical-controls/{id}/performance-standards', data as OperationOptions);
}

export function getHazards(
  data: Omit<GetHazardsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetHazardsResponse> {
  return request(config, 'GET', '/hazards', data as OperationOptions);
}

export function getHazardsById(
  data: Omit<GetHazardsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetHazardsByIdResponse> {
  return request(config, 'GET', '/hazards/{id}', data as OperationOptions);
}

export function getIncidents(
  data: Omit<GetIncidentsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetIncidentsResponse> {
  return request(config, 'GET', '/incidents', data as OperationOptions);
}

export function getIncidentsById(
  data: Omit<GetIncidentsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetIncidentsByIdResponse> {
  return request(config, 'GET', '/incidents/{id}', data as OperationOptions);
}

export function getIncidentsByIdActions(
  data: Omit<GetIncidentsByIdActionsData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetIncidentsByIdActionsResponse> {
  return request(config, 'GET', '/incidents/{id}/actions', data as OperationOptions);
}

export function getIncidentsByIdEvidence(
  data: Omit<GetIncidentsByIdEvidenceData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetIncidentsByIdEvidenceResponse> {
  return request(config, 'GET', '/incidents/{id}/evidence', data as OperationOptions);
}

export function getIncidentsByIdHazards(
  data: Omit<GetIncidentsByIdHazardsData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetIncidentsByIdHazardsResponse> {
  return request(config, 'GET', '/incidents/{id}/hazards', data as OperationOptions);
}

export function getIncidentsByIdInvestigation(
  data: Omit<GetIncidentsByIdInvestigationData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetIncidentsByIdInvestigationResponse> {
  return request(config, 'GET', '/incidents/{id}/investigation', data as OperationOptions);
}

export function getOntologyConcepts(
  data: Omit<GetOntologyConceptsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetOntologyConceptsResponse> {
  return request(config, 'GET', '/ontology/concepts', data as OperationOptions);
}

export function getOntologySchemes(
  data: Omit<GetOntologySchemesData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetOntologySchemesResponse> {
  return request(config, 'GET', '/ontology/schemes', data as OperationOptions);
}

export function getPerformanceStandardsByIdVerificationActivities(
  data: Omit<GetPerformanceStandardsByIdVerificationActivitiesData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetPerformanceStandardsByIdVerificationActivitiesResponse> {
  return request(config, 'GET', '/performance-standards/{id}/verification-activities', data as OperationOptions);
}

export function getRisks(
  data: Omit<GetRisksData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<GetRisksResponse> {
  return request(config, 'GET', '/risks', data as OperationOptions);
}

export function getRisksById(
  data: Omit<GetRisksByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetRisksByIdResponse> {
  return request(config, 'GET', '/risks/{id}', data as OperationOptions);
}

export function getRisksByRiskIdControls(
  data: Omit<GetRisksByRiskIdControlsData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetRisksByRiskIdControlsResponse> {
  return request(config, 'GET', '/risks/{riskId}/controls', data as OperationOptions);
}

export function getVerificationActivitiesByIdEvidence(
  data: Omit<GetVerificationActivitiesByIdEvidenceData, 'url'>,
  config?: ApiClientConfig,
): Promise<GetVerificationActivitiesByIdEvidenceResponse> {
  return request(config, 'GET', '/verification-activities/{id}/evidence', data as OperationOptions);
}

export function patchActionsById(
  data: Omit<PatchActionsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchActionsByIdResponse> {
  return request(config, 'PATCH', '/actions/{id}', data as OperationOptions);
}

export function patchAssetsById(
  data: Omit<PatchAssetsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchAssetsByIdResponse> {
  return request(config, 'PATCH', '/assets/{id}', data as OperationOptions);
}

export function patchCriticalControlsById(
  data: Omit<PatchCriticalControlsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchCriticalControlsByIdResponse> {
  return request(config, 'PATCH', '/critical-controls/{id}', data as OperationOptions);
}

export function patchHazardsById(
  data: Omit<PatchHazardsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchHazardsByIdResponse> {
  return request(config, 'PATCH', '/hazards/{id}', data as OperationOptions);
}

export function patchIncidentsById(
  data: Omit<PatchIncidentsByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchIncidentsByIdResponse> {
  return request(config, 'PATCH', '/incidents/{id}', data as OperationOptions);
}

export function patchIncidentsByIdInvestigation(
  data: Omit<PatchIncidentsByIdInvestigationData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchIncidentsByIdInvestigationResponse> {
  return request(config, 'PATCH', '/incidents/{id}/investigation', data as OperationOptions);
}

export function patchRisksById(
  data: Omit<PatchRisksByIdData, 'url'>,
  config?: ApiClientConfig,
): Promise<PatchRisksByIdResponse> {
  return request(config, 'PATCH', '/risks/{id}', data as OperationOptions);
}

export function postActions(
  data: Omit<PostActionsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<PostActionsResponse> {
  return request(config, 'POST', '/actions', data as OperationOptions);
}

export function postAssets(
  data: Omit<PostAssetsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostAssetsResponse> {
  return request(config, 'POST', '/assets', data as OperationOptions);
}

export function postControlsByIdCriticalControlTest(
  data: Omit<PostControlsByIdCriticalControlTestData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostControlsByIdCriticalControlTestResponse> {
  return request(config, 'POST', '/controls/{id}/critical-control-test', data as OperationOptions);
}

export function postControlsByIdEiaTest(
  data: Omit<PostControlsByIdEiaTestData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostControlsByIdEiaTestResponse> {
  return request(config, 'POST', '/controls/{id}/eia-test', data as OperationOptions);
}

export function postControlsByIdGateTest(
  data: Omit<PostControlsByIdGateTestData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostControlsByIdGateTestResponse> {
  return request(config, 'POST', '/controls/{id}/gate-test', data as OperationOptions);
}

export function postCriticalControlsByIdPerformanceStandards(
  data: Omit<PostCriticalControlsByIdPerformanceStandardsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostCriticalControlsByIdPerformanceStandardsResponse> {
  return request(config, 'POST', '/critical-controls/{id}/performance-standards', data as OperationOptions);
}

export function postHazards(
  data: Omit<PostHazardsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostHazardsResponse> {
  return request(config, 'POST', '/hazards', data as OperationOptions);
}

export function postIncidents(
  data: Omit<PostIncidentsData, 'url'> = {},
  config?: ApiClientConfig,
): Promise<PostIncidentsResponse> {
  return request(config, 'POST', '/incidents', data as OperationOptions);
}

export function postIncidentsByIdActions(
  data: Omit<PostIncidentsByIdActionsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostIncidentsByIdActionsResponses[201]> {
  return request(config, 'POST', '/incidents/{id}/actions', data as OperationOptions);
}

export function postIncidentsByIdEvidence(
  data: Omit<PostIncidentsByIdEvidenceData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostIncidentsByIdEvidenceResponse> {
  return request(config, 'POST', '/incidents/{id}/evidence', data as OperationOptions);
}

export function postIncidentsByIdHazards(
  data: Omit<PostIncidentsByIdHazardsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostIncidentsByIdHazardsResponses[201]> {
  return request(config, 'POST', '/incidents/{id}/hazards', data as OperationOptions);
}

export function postIncidentsByIdInvestigation(
  data: Omit<PostIncidentsByIdInvestigationData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostIncidentsByIdInvestigationResponse> {
  return request(config, 'POST', '/incidents/{id}/investigation', data as OperationOptions);
}

export function postPerformanceStandardsByIdVerificationActivities(
  data: Omit<PostPerformanceStandardsByIdVerificationActivitiesData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostPerformanceStandardsByIdVerificationActivitiesResponse> {
  return request(config, 'POST', '/performance-standards/{id}/verification-activities', data as OperationOptions);
}

export function postRisks(
  data: Omit<PostRisksData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostRisksResponse> {
  return request(config, 'POST', '/risks', data as OperationOptions);
}

export function postRisksByRiskIdControls(
  data: Omit<PostRisksByRiskIdControlsData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostRisksByRiskIdControlsResponse> {
  return request(config, 'POST', '/risks/{riskId}/controls', data as OperationOptions);
}

export function postVerificationActivitiesByIdEvidence(
  data: Omit<PostVerificationActivitiesByIdEvidenceData, 'url'>,
  config?: ApiClientConfig,
): Promise<PostVerificationActivitiesByIdEvidenceResponse> {
  return request(config, 'POST', '/verification-activities/{id}/evidence', data as OperationOptions);
}
