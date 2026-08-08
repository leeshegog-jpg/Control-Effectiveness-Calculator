"""Risk business rules -- R1 (rating derivation) and R4 (SFARP gate).
See docs/knowledge-graph/07-inference-rules-catalogue.md.

Both rules are ported verbatim from V1, not reinvented:
- R1 from sms-shared.js's SMS.riskScore/riskBand.
- R4 from bowtie-ccm-generator.html's validateDraft() SFARP check. The
  catalogue itself flags this as a weak, regex-only check and recommends
  a required-fields upgrade before it becomes the sole gate in a
  regulator-facing system -- that upgrade is future work, not something to
  silently strengthen here while porting.
"""

import re

_SFARP_WEAK_PATTERN = re.compile(r"risk is acceptable", re.IGNORECASE)


def risk_score(likelihood: int | None, consequence: int | None) -> int | None:
    if not likelihood or not consequence:
        return None
    return likelihood * consequence


def risk_band(score: int | None) -> str | None:
    """VRTP Risk Matrix (GOHS2.1.2): Extreme 15-25, High 10-14, Medium 5-9, Low 1-4."""
    if score is None:
        return None
    if score >= 15:
        return "Extreme"
    if score >= 10:
        return "High"
    if score >= 5:
        return "Medium"
    if score >= 1:
        return "Low"
    return None


def sfarp_justification_insufficient(
    current_rating: str | None, sfarp_justification: str | None
) -> bool:
    """True if the SFARP gate (R4) should reject this justification."""
    if current_rating not in ("Extreme", "High"):
        return False
    if not sfarp_justification:
        return True
    return bool(_SFARP_WEAK_PATTERN.search(sfarp_justification))
