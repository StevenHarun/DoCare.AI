"""
Unit Tests untuk DoCare AI RAG Engine
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.rag.engine import rag_engine

def test_rag_emergency_interception():
    # Menguji apakah keluhan darurat langsung dipotong oleh triage guardrail
    query = "I see my friend is faint, no paramedics nearby, and the face is blue"
    res = rag_engine.ask(query)
    assert res["is_emergency"] is True
    assert "🚨" in res["response"]
    assert "119" in res["response"]

def test_rag_system_prompt_builder():
    context = "Glaucoma is a group of eye diseases that can cause vision loss."
    prompt = rag_engine.build_system_prompt(context, tone="professional and friendly")
    assert "DoCare AI" in prompt
    assert "Glaucoma" in prompt
    assert "MedQuAD" in prompt

def test_rag_general_consultation():
    query = "What is Glaucoma and how does it affect vision?"
    res = rag_engine.ask(query)
    assert res["is_emergency"] is False
    assert "DoCare AI" in res["response"]
    assert len(res["response"]) > 50

if __name__ == "__main__":
    test_rag_emergency_interception()
    test_rag_system_prompt_builder()
    test_rag_general_consultation()
    print("All RAG Engine Tests PASSED successfully!")
