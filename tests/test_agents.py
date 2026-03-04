import os
import sys
import pytest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.differ.tools.differ_tool import generate_diff
from agents.summarizer.tools.summarize_tool import generate_summary
from agents.analyser.tools.analyser_tool import analyze_changes
from llm_client import call_llm

def test_generate_diff(tmp_path):
    # Setup test files
    md1 = tmp_path / "initial.md"
    md1.write_text("Line 1\nLine 2\n")
    md2 = tmp_path / "modified.md"
    md2.write_text("Line 1\nLine Modified\n")
    
    out = tmp_path / "diff.md"
    
    generate_diff(str(md1), str(md2), str(out))
    
    assert out.exists()
    content = out.read_text()
    assert "# Changes" in content
    assert "+Line Modified" in content
    assert "-Line 2" in content

def test_call_llm_empty_prompt():
    """Test the fallback message directly."""
    res = call_llm(prompt="")
    assert "Agent execution failed due to API error or empty input" in res

@pytest.fixture
def mock_llm(mocker):
    """Mocks the LLM API call entirely."""
    def _mock_call(prompt, **kwargs):
        if "Summarize" in prompt:
            return "MOCK SUMMARY DATA."
        if "analyze" in prompt.lower() or "report" in prompt.lower():
            return "MOCK ANALYSIS REPORT."
        return "MOCK RESPONSE."
    
    mocker.patch('agents.summarizer.tools.summarize_tool.call_llm', side_effect=_mock_call)
    mocker.patch('agents.analyser.tools.analyser_tool.call_llm', side_effect=_mock_call)

def test_summarizer(tmp_path, mock_llm):
    inp = tmp_path / "memoriu.md"
    inp.write_text("This is a huge memorandum text to be summarized.")
    out = tmp_path / "summary.md"
    
    generate_summary(str(inp), str(out))
    
    assert out.exists()
    assert "MOCK SUMMARY DATA." in out.read_text()

def test_analyser(tmp_path, mock_llm):
    summ = tmp_path / "summary.md"
    summ.write_text("Require modifications.")
    diff = tmp_path / "differs.md"
    diff.write_text("Changes made.")
    out = tmp_path / "raport.md"
    
    analyze_changes(str(summ), str(diff), str(out))
    
    assert out.exists()
    assert "MOCK ANALYSIS REPORT." in out.read_text()
