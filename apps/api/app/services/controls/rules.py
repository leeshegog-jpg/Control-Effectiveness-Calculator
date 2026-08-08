"""Controls business rules -- the 3-gate Control/Support/Verification
classification test. See docs/knowledge-graph/08-critical-control-assurance-model.md
§2 and docs/implementation-blueprint/17-r1-milestone-2-ccm-discovery-reconciliation.md.

Ported verbatim from bowtie-ccm-generator.html:1505-1510 (GOHS-REF-SMS-001),
not reinvented. V1's UI answers gates one at a time and can leave the
follow-up unanswered (an intermediate "Gated" state); this milestone's
OpenAPI endpoint (POST /controls/{id}/gate-test) requires all three gates
plus the follow-up in one call, so that intermediate state is skipped --
the two reachable outcomes are identical to V1's eventual result.
"""


def classify_from_gates(
    gate_1: bool, gate_2: bool, gate_3: bool, is_verification_check: bool
) -> str:
    if gate_1 and gate_2 and gate_3:
        return "Control"
    return "Verification" if is_verification_check else "Support"
