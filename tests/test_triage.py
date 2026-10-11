"""
Unit Tests untuk Emergency Triage Engine
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.triage.emergency import triage_service

def test_cyanosis_and_faint_detection():
    query = "i see my friend is faint, what should i do, no paramedics nearby, also the face is blue"
    res = triage_service.assess_urgency(query)
    assert res.is_emergency is True
    assert res.level == "CRITICAL"
    assert "Hypoxia" in res.category or "Respiratory" in res.category
    assert len(res.first_aid_steps) > 0
    assert "119" in str(res.emergency_contacts)

def test_chest_pain_detection():
    query = "Tiba-tiba dada saya sesak dan mengalami nyeri dada hebat seperti tertekan"
    res = triage_service.assess_urgency(query)
    assert res.is_emergency is True
    assert res.level == "CRITICAL"
    assert "Cardiovascular" in res.category

def test_non_emergency_query():
    query = "What are the common symptoms of mild glaucoma or dry eyes?"
    res = triage_service.assess_urgency(query)
    assert res.is_emergency is False
    assert res.level == "NON_EMERGENCY"
    assert len(res.first_aid_steps) == 0

if __name__ == "__main__":
    test_cyanosis_and_faint_detection()
    test_chest_pain_detection()
    test_non_emergency_query()
    print("All Triage Tests PASSED successfully!")
