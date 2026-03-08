# Plan: Fix ApiVlmOptions Validation Error in Formatter Agent

## Problem Statement
The `ApiVlmOptions` instantiation in `ollama_pipeline_api_model.py` is missing required fields:
- `prompt` field is required but not provided
- `response_format` needs proper validation

This causes the formatter agent to fail when processing PDFs with the error:
```
2 validation errors for ApiVlmOptions
prompt
Field required [type=missing, input_value={'url': '...', 'params': {...}, 'timeout': 300}, input_type=dict]
response_format
```

## Root Cause Analysis
The current code in `ollama_pipeline_api_model.py` (lines 175-186) uses a direct `ApiVlmOptions` instantiation but doesn't provide all required fields that Pydantic validation expects.

The file previously had a commented-out section (lines 120-125) showing the **preset-based approach** using `VlmConvertOptions.from_preset()`, which handles all required fields automatically.

## Solution Approach

### Recommendation: Use Preset-Based Configuration
**Why this approach:**
1. **Autolizes all required fields** - Pydantic validation passes automatically
2. **Better maintainability** - Changes in Docling's validation rules don't break our code
3. **Follow official pattern** - Aligns with Docling's documented usage
4. **Simpler code** - Less boilerplate, clearer intent

**Alternative (not recommended):** Manually add `prompt` field to `ApiVlmOptions` (band-aid approach, may break with future Docling updates)

## Implementation Steps

### Phase 1: Code Replacement
**File:** `ollama_pipeline_api_model.py`
**Location:** Lines 175-186 (in `run_ollama_document_converter()` function)

**Current code:**
```python
vlm_options = ApiVlmOptions(
    url=REMOTE_OLLAMA_URL,
    params={
        "model": model_name,
        "temperature": 0.0,
        "max_tokens": 4096,
        "options": {"num_ctx": 8192},
    },
    response_format=ResponseFormat.MARKDOWN,
    timeout=300,
)
```

**Replace with:**
```python
vlm_options = VlmConvertOptions.from_preset(
    "granite_docling",
    engine_options=ApiVlmEngineOptions(
        runtime_type=VlmEngineType.API_OLLAMA,
        url=REMOTE_OLLAMA_URL,
        model_name=model_name,
        timeout=300,
    ),
)
```

**Reasoning:**
- Uses the official preset pattern from Docling
- Automatically includes required `prompt` field from preset
- Properly validates `response_format` through preset
- Maintains timeout and model configuration
- Preserves remote API capability

### Phase 2: Remove Problematic Imports (If Applicable)
Review if `ApiVlmOptions` needs to be removed from imports after switching to preset approach. The imports at the top should already include `VlmConvertOptions` and `ApiVlmEngineOptions`.

### Phase 3: Testing & Validation
1. **Unit Test:** Run formatter agent on `formular_modificat.pdf`
   ```bash
   python -c "from agents.formatter.formatter_agent import FormatterAgent; \
     fa = FormatterAgent(); \
     fa.process(['formular_modificat.pdf'])"
   ```

2. **Verify Output:**
   - Check `output/formular_modificat.md` exists
   - Confirm no validation errors in logs
   - Inspect markdown content for proper formatting

3. **Integration Test:** Run full pipeline to ensure downstream agents process correctly

## Alternative Solutions Considered

### Option A: Manually Add Missing `prompt` Field
Add a system prompt directly to `ApiVlmOptions`:
```python
vlm_options = ApiVlmOptions(
    url=REMOTE_OLLAMA_URL,
    prompt="Convert this PDF document to markdown format...",  # Added
    params={...},
    response_format=ResponseFormat.MARKDOWN,
    timeout=300,
)
```
**Pros:** Minimal code change
**Cons:** Fragile, may break with Docling updates; doesn't follow official pattern

### Option B: Use Custom API Configuration
Apply custom API opts while keeping preset structure (for non-standard APIs)
**Not applicable here** - We're using Ollama which has a pre-configured type

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Docling version incompatibility | Low | Preset approach is more future-proof than manual field addition |
| Runtime parameter changes | Low | `timeout` and `model_name` still configurable in `ApiVlmEngineOptions` |
| API endpoint issues | Low | Existing fallback error handling (FALLBACK_MESSAGE) remains |
| Network timeouts | Medium | Already handled by 300s timeout; no change needed |

## Success Criteria
- ✅ No Pydantic validation errors when running formatter agent
- ✅ PDF successfully converts to markdown output
- ✅ Output file created in `output/` directory
- ✅ Full pipeline completes without errors (Formatter → Summarizer → Differ → Analyser → Reporter)
- ✅ Markdown content is properly formatted and readable

## Files to Modify
1. `ollama_pipeline_api_model.py` - Replace ApiVlmOptions instantiation with preset-based approach

## Rollback Plan
If preset approach causes issues:
1. Revert to current `ApiVlmOptions` code
2. Add explicit `prompt` field with appropriate system instruction
3. Test and document the constraint

## Related Code Points
- **pdf_formatter.py** (lines 34-35): Calls `run_ollama_document_converter()` — no changes needed
- **formatter_agent.py** (line 26): Exception handler catches conversion errors — will report validation errors clearly
- **Model reference:** "ibm/granite-docling:258m" — kept consistent across both approaches
