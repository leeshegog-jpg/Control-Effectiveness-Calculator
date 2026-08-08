"""3-gate Control/Support/Verification classification -- ported verbatim
from bowtie-ccm-generator.html:1505-1510 (GOHS-REF-SMS-001). This is the
V1 parity check: every case here is drawn directly from that logic.
"""

import pytest
from app.services.controls.rules import classify_from_gates


@pytest.mark.parametrize(
    ("gate_1", "gate_2", "gate_3", "is_verification_check", "expected"),
    [
        (True, True, True, False, "Control"),
        (
            True,
            True,
            True,
            True,
            "Control",
        ),  # all gates pass -> Control regardless of follow-up
        (False, True, True, False, "Support"),
        (True, False, True, False, "Support"),
        (True, True, False, False, "Support"),
        (False, False, False, False, "Support"),
        (False, True, True, True, "Verification"),
        (True, False, True, True, "Verification"),
    ],
)
def test_classify_from_gates_matches_bowtie_generator(
    gate_1, gate_2, gate_3, is_verification_check, expected
):
    assert (
        classify_from_gates(gate_1, gate_2, gate_3, is_verification_check) == expected
    )
