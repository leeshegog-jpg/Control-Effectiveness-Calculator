# ACR-012 — Schemathesis `Allow` Header Conformance Test Decision

**Status:** Approved — implementation pending CI verification  
**Raised:** 2026-09-06  
**Scope:** ADR-007 P5 (`AllowHeaderMismatch` ×20)

## 1. Decision

Exclude Schemathesis `allow_header_conformance` from the contract-test check set for the implemented R1 surface.

This is a **test-methodology decision**, not an API remediation. The underlying FastAPI/Starlette routing behaviour is unchanged.

The Schemathesis `AllowHeaderMismatch` finding arises from coverage scenarios that exercise an unsupported HTTP method. Starlette constructs the resulting `Allow` header from the mounted route's method set, while Schemathesis compares that response with the frozen contract operation-method set. The resulting mismatch does not establish a defect in the implemented operation itself.

The unsupported-method response check remains enabled; only the `Allow` header comparison is excluded.

## 2. Scope boundary

This ACR changes only the contract-test harness configuration and its wiring tests/documentation.

It does **not**:

- change API routing or HTTP behaviour;
- modify the OpenAPI contract;
- remove or add an API response;
- change authentication treatment under ADR-007 D2;
- change the deferred-operation classification;
- address P6 `negative_data` behaviour;
- address P7/S4 authentication enforcement.

## 3. Implementation

`tests/contract/test_openapi_contract.py` adds `allow_header_conformance` to `_EXCLUDED_CHECKS` alongside the two existing ADR-007 D2 authentication exclusions.

`tests/contract/test_contract_classification.py` asserts the exact three excluded checks: `ignored_auth`, `missing_required_header`, and `allow_header_conformance`.

## 4. Verification requirement

The PR must demonstrate that the P5 `AllowHeaderMismatch` failures are removed without changing the operation population or introducing unrelated regressions.

The contract suite remains **report-only** under ADR-007 D4. This ACR does not promote it to a required CI check.

## 5. Traceability

- ADR-007 D1–D4 — contract population, authentication treatment, deferred operations and report-only CI treatment.
- P5 — `AllowHeaderMismatch` ×20 from the ADR-007 defect discovery baseline.
- ACR-008 — prior documentation that P5 is a test-methodology decision and that the underlying Starlette route behaviour is not being remediated.
