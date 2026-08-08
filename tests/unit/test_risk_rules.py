"""R1 (rating derivation) and R4 (SFARP gate) -- ported verbatim from V1
(sms-shared.js SMS.riskScore/riskBand; bowtie-ccm-generator.html
validateDraft()). These tests are the V1 parity check: every case here is
drawn directly from those two files, not invented.
"""

import pytest
from app.services.risks.rules import (
    risk_band,
    risk_score,
    sfarp_justification_insufficient,
)


@pytest.mark.parametrize(
    ("likelihood", "consequence", "expected"),
    [
        (1, 1, 1),
        (5, 5, 25),
        (3, 4, 12),
        (None, 3, None),
        (3, None, None),
        (0, 3, None),
    ],
)
def test_risk_score_matches_sms_shared_js(likelihood, consequence, expected):
    assert risk_score(likelihood, consequence) == expected


@pytest.mark.parametrize(
    ("score", "expected_band"),
    [
        (None, None),
        (0, None),
        (1, "Low"),
        (4, "Low"),
        (5, "Medium"),
        (9, "Medium"),
        (10, "High"),
        (14, "High"),
        (15, "Extreme"),
        (25, "Extreme"),
    ],
)
def test_risk_band_matches_vrtp_matrix_gohs212(score, expected_band):
    assert risk_band(score) == expected_band


@pytest.mark.parametrize(
    ("current_rating", "justification", "expected_insufficient"),
    [
        ("Low", None, False),
        ("Medium", None, False),
        ("High", None, True),
        ("Extreme", None, True),
        ("High", "", True),
        ("High", "The risk is acceptable.", True),
        ("Extreme", "the RISK IS ACCEPTABLE given controls", True),
        (
            "High",
            (
                "Reviewed against critical control performance standards; residual risk "
                "tolerable per WHS duty, controls independently verified quarterly."
            ),
            False,
        ),
    ],
)
def test_sfarp_gate_matches_bowtie_validate_draft(
    current_rating, justification, expected_insufficient
):
    assert (
        sfarp_justification_insufficient(current_rating, justification)
        is expected_insufficient
    )
