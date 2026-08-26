// Unit tests for the api-client wrappers -- request construction and
// response handling only. No Postgres, Neo4j, Docker, or running API
// required: `fetch` is mocked via ApiClientConfig.fetch.

import assert from 'node:assert/strict';
import { test } from 'node:test';

import {
  ApiError,
  deleteIncidentsByIdActionsByActionId,
  getActions,
  getIncidentsById,
  getRisksByRiskIdControls,
  patchActionsById,
  postAssets,
  postIncidentsByIdActions,
} from './index.ts';

function mockFetch(
  handler: (input: string | URL | Request, init?: RequestInit) => Response,
): typeof fetch {
  return (async (input: string | URL | Request, init?: RequestInit) => handler(input, init)) as typeof fetch;
}

test('getActions -- no-arg operation builds the bare path with no query string', async () => {
  let capturedUrl = '';
  const fetchMock = mockFetch((url) => {
    capturedUrl = String(url);
    return new Response(JSON.stringify([]), { status: 200 });
  });

  const result = await getActions({}, { fetch: fetchMock });

  assert.equal(capturedUrl, '/actions');
  assert.deepEqual(result, []);
});

test('getActions -- query params are appended, undefined values omitted', async () => {
  let capturedUrl = '';
  const fetchMock = mockFetch((url) => {
    capturedUrl = String(url);
    return new Response(JSON.stringify([]), { status: 200 });
  });

  await getActions({ query: { status: 'Open', limit: undefined } }, { fetch: fetchMock });

  assert.equal(capturedUrl, '/actions?status=Open');
});

test('getIncidentsById -- required path param substituted into the URL template', async () => {
  let capturedUrl = '';
  const fetchMock = mockFetch((url) => {
    capturedUrl = String(url);
    return new Response(JSON.stringify({ id: 'abc' }), { status: 200 });
  });

  await getIncidentsById({ path: { id: 'abc-123' } }, { fetch: fetchMock });

  assert.equal(capturedUrl, '/incidents/abc-123');
});

test('getRisksByRiskIdControls -- differently-named path param (riskId) still substitutes correctly', async () => {
  let capturedUrl = '';
  const fetchMock = mockFetch((url) => {
    capturedUrl = String(url);
    return new Response(JSON.stringify([]), { status: 200 });
  });

  await getRisksByRiskIdControls({ path: { riskId: 'risk-1' } }, { fetch: fetchMock });

  assert.equal(capturedUrl, '/risks/risk-1/controls');
});

test('deleteIncidentsByIdActionsByActionId -- two path params in one template both substitute', async () => {
  let capturedUrl = '';
  let capturedMethod = '';
  const fetchMock = mockFetch((url, init) => {
    capturedUrl = String(url);
    capturedMethod = init?.method ?? '';
    return new Response(null, { status: 204 });
  });

  const result = await deleteIncidentsByIdActionsByActionId(
    { path: { id: 'incident-1', actionId: 'action-1' } },
    { fetch: fetchMock },
  );

  assert.equal(capturedUrl, '/incidents/incident-1/actions/action-1');
  assert.equal(capturedMethod, 'DELETE');
  assert.equal(result, undefined);
});

test('postAssets -- required body is JSON-serialized with the correct Content-Type', async () => {
  let capturedBody = '';
  let capturedContentType: string | null = null;
  const fetchMock = mockFetch((_url, init) => {
    capturedBody = String(init?.body ?? '');
    capturedContentType = new Headers(init?.headers).get('Content-Type');
    return new Response(JSON.stringify({ id: 'asset-1', name: 'Test' }), { status: 201 });
  });

  const result = await postAssets({ body: { name: 'Test' } }, { fetch: fetchMock });

  assert.equal(capturedContentType, 'application/json');
  assert.deepEqual(JSON.parse(capturedBody), { name: 'Test' });
  assert.equal(result.name, 'Test');
});

test('patchActionsById -- optional body omitted entirely means no request body is sent', async () => {
  let bodyWasSent = false;
  const fetchMock = mockFetch((_url, init) => {
    bodyWasSent = init?.body !== undefined;
    return new Response(JSON.stringify({ id: 'a1', status: 'Open' }), { status: 200 });
  });

  await patchActionsById({ path: { id: 'a1' } }, { fetch: fetchMock });

  assert.equal(bodyWasSent, false);
});

test('postIncidentsByIdActions -- link operation with an undocumented (unknown) 201 body', async () => {
  const fetchMock = mockFetch(() => new Response(null, { status: 201 }));

  const result = await postIncidentsByIdActions(
    { path: { id: 'incident-1' }, body: { action_id: 'action-1' } },
    { fetch: fetchMock },
  );

  assert.equal(result, undefined);
});

test('non-2xx response throws ApiError with method, url, and status', async () => {
  const fetchMock = mockFetch(
    () => new Response(JSON.stringify({ code: 'not_found' }), { status: 404 }),
  );

  await assert.rejects(
    () => getIncidentsById({ path: { id: 'missing' } }, { fetch: fetchMock }),
    (error: unknown) => {
      assert.ok(error instanceof ApiError);
      assert.equal(error.method, 'GET');
      assert.equal(error.status, 404);
      assert.match(error.url, /\/incidents\/missing$/);
      return true;
    },
  );
});

test('baseUrl config produces an absolute URL', async () => {
  let capturedUrl = '';
  const fetchMock = mockFetch((url) => {
    capturedUrl = String(url);
    return new Response(JSON.stringify([]), { status: 200 });
  });

  await getActions({}, { baseUrl: 'https://api.example.test', fetch: fetchMock });

  assert.equal(capturedUrl, 'https://api.example.test/actions');
});
