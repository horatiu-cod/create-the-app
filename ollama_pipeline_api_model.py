# %% [markdown]
# Use the VLM pipeline with remote API models (LM Studio, Ollama, VLLM, watsonx.ai).
#
# What this example does
# - Demonstrates using presets with API runtimes (LM Studio, Ollama, VLLM, watsonx.ai)
# - Shows that API is just a runtime choice, not a different options class
# - Explains pre-configured API types and custom API configuration
#
# Prerequisites
# - Install Docling with VLM extras and `python-dotenv` if using environment files.
# - For local APIs: run LM Studio, Ollama, or VLLM locally.
# - For cloud APIs: set required environment variables (see watsonx.ai example).
#
# How to run
# - From the repo root: `python docs/examples/vlm_pipeline_api_model.py`.
# - Each example checks its own prerequisites and skips if not available.
#
# Notes
# - The NEW runtime system unifies API and local inference
# - For legacy approach, see legacy examples in docs/examples/legacy/

# %%

import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmConvertOptions,
    VlmPipelineOptions,
)
from docling.datamodel.vlm_engine_options import (
    ApiVlmEngineOptions,
    VlmEngineType,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from typer import prompt

# Configure basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Fallback string
FALLBACK_MESSAGE = "Agent execution failed due to API error or empty input. Downstream tasks might be impacted."


def check_and_pull_ollama_model(model_name: str, base_url: str) -> bool:
    """Check if model exists in Ollama and attempt to pull if not.

    Args:
        model_name: The model name to check/pull

    Returns:
        True if model exists or successfully pulled, False otherwise
    """
    try:
        # Check if model exists
        logger.info(f"Checking if model '{model_name}' exists in Ollama...")
        logger.info(f"Base URL: {base_url}")
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            # Check for exact match or with :latest tag
            if model_name in model_names or f"{model_name}:latest" in model_names:
                logger.info(f"✓ Model '{model_name}' is already available in Ollama")
                return True

            # Try to pull the model using Ollama API
            logger.info(f"Attempting to pull model '{model_name}' in Ollama...")
            logger.info("This may take a few minutes...")

            # Ollama pull API endpoint
            pull_response = requests.post(
                f"{base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=300,
            )
            logger.info(f"Pull response status code: {pull_response.status_code}")
            if pull_response.status_code == 200:
                # Stream the response to show progress
                logger.info("Pulling model...")
                for line in pull_response.iter_lines():
                    if line:
                        import json

                        try:
                            data = json.loads(line)
                            status = data.get("status", "")
                            if status:
                                print(f"{status}", end="\r")
                        except json.JSONDecodeError:
                            logger.warning(f"Non-JSON line in pull response: {line}")
                            pass
                print()  # New line after progress
                logger.info(f"✓ Successfully pulled model '{model_name}'")
                return True
            else:
                logger.error(
                    f"✗ Failed to pull model: HTTP {pull_response.status_code}"
                )
                return False
        return False
    except requests.exceptions.Timeout:
        logger.error("✗ Timeout while trying to pull model (this can take a while)")
        logger.error("Please try pulling manually: ollama pull", model_name)
        return False
    except Exception as e:
        logger.error(f"✗ Error checking/pulling model: {e}")
        return False


def run_ollama_document_converter(
    input_doc_path: Path, model_name: str = "ibm/granite-docling"
) -> tuple[str, bool]:
    # Load environment variables
    # from dotenv import load_dotenv

    load_dotenv()
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    REMOTE_OLLAMA_URL = f"{base_url}/v1/chat/completions"
    """Example 2: Using Granite-Docling preset with Ollama.

    Returns:
        True if example ran successfully, False if skipped
    """
    print("\n" + "=" * 70)
    print(f"Example {base_url}: Granite-Docling with Ollama (pre-configured API type)")
    print("=" * 70)
    print("\nPrerequisites:")
    print("- Install Ollama: https://ollama.ai")
    print("- Pull model: ollama pull ibm/granite-docling:258m")
    print()

    # Check if Ollama is running
    logger.info(f"Checking if Ollama server is running at {base_url}...")

    try:
        response = requests.get(f"{base_url}/api/tags", timeout=2)
        if response.status_code != 200:
            logger.warning("WARNING: Ollama server not responding correctly")
            return FALLBACK_MESSAGE, False
    except requests.exceptions.RequestException:
        logger.warning(f"WARNING: Ollama server not running at {base_url}")
        return FALLBACK_MESSAGE, False

    # Check and pull the model
    # model_name = "ibm/granite-docling:258m"
    logger.info(f"Checking if model '{model_name}' exists in Ollama...")
    if not check_and_pull_ollama_model(model_name, base_url):
        return FALLBACK_MESSAGE, False

    # Use granite_docling preset with Ollama API runtime
    """
    vlm_options = VlmConvertOptions.from_preset(
    "granite_docling",
        engine_options=ApiVlmEngineOptions(
            runtime_type=VlmEngineType.API_OLLAMA,
            url=REMOTE_OLLAMA_URL,
            model_name=model_name,
            timeout=300,
        ),
    )
    """
    vlm_options = ApiVlmOptions(
        url=REMOTE_OLLAMA_URL,
        prompt="Convert this PDF document to markdown format...",  # Added
        params={
            "model": model_name,
            "temperature": 0.0,
            "max_tokens": 4096,
            "options": {"num_ctx": 8192},
        },
        response_format=ResponseFormat.MARKDOWN,
        timeout=300,  # Remote calls can take time depending on network/GPU
    )
    
    pipeline_options = VlmPipelineOptions(
        vlm_options=vlm_options,
        enable_remote_services=True,
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                pipeline_cls=VlmPipeline,
            )
        }
    )

    doc = doc_converter.convert(input_doc_path).document
    #return result, True
    OUTPUT_DIR = Path(__file__).parent / "output/test.md" 
    doc.save_as_markdown(OUTPUT_DIR)
    """
    md = result.document.export_to_markdown()
    with open(OUTPUT_DIR , 'w', encoding="utf-8") as f:
            f.write(md)
    """
    return OUTPUT_DIR, True
    
def main():

    INPUT_DIR = Path(__file__).parent / "data/input"
    #OUTPUT_DIR = Path(__file__).parent / "output"    
    #data_folder = Path(__file__).parent / "../../tests/data"
    input_doc_path = INPUT_DIR /"memoriu.pdf"
    if not input_doc_path.exists():
        logger.error(f"Input document not found at {input_doc_path}")
        return

    # Track which examples ran
    t, s = run_ollama_document_converter(input_doc_path)
    
    results = {
        "Ollama": s,
    }

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    ran = [name for name, success in results.items() if success]
    skipped = [name for name, success in results.items() if not success]

    if ran:
        print(f"\n✓ Examples that ran successfully ({len(ran)}):")
        for name in ran:
            print(f"  - {name}")
        print(f"\nOutput from Ollama example:\n{t}")
        
    if skipped:
        print(f"\n⊘ Examples that were skipped ({len(skipped)}):")
        for name in skipped:
            reason = "Server not running"
            print(f"  - {name}: {reason}")

    print()


if __name__ == "__main__":
    main()

# %% [markdown]
# ## Key Concepts
#
# ### Pre-configured API Types
# The new runtime system has pre-configured API types:
# - **API_OLLAMA**: Ollama server (port 11434)
# - **API_LMSTUDIO**: LM Studio server (port 1234)
# - **API_OPENAI**: OpenAI API
# - **API**: Generic API endpoint (you provide URL)
#
# Each preset knows the appropriate model names for these API types.
#
# ### Custom API Configuration
# For services like watsonx.ai that need custom configuration:
# - Use `VlmEngineType.API` (generic)
# - Provide custom `url`, `headers`, and `params`
# - The preset still provides the base model configuration (prompt, response format)
#
# ### Same Preset, Different Runtime
# You can use the same preset (e.g., "granite_docling") with:
# - Local Transformers runtime (see other examples)
# - Local MLX runtime (macOS)
# - LM Studio API runtime (this example)
# - Ollama API runtime (this example)
# - VLLM API runtime (this example)
# - watsonx.ai API runtime (this example)
# - Any other API endpoint
#
# This makes it easy to develop locally and deploy to production!
#
# ### Available Presets for VlmConvert
# - **granite_docling**: IBM Granite Docling 258M (DocTags format)
# - **smoldocling**: SmolDocling 256M (DocTags format)
# - **deepseek_ocr**: DeepSeek OCR (Markdown format)
# - **granite_vision**: IBM Granite Vision (Markdown format)
# - **pixtral**: Pixtral (Markdown format)
# - **got_ocr**: GOT-OCR (Markdown format)
# - **phi4**: Phi-4 (Markdown format)
# - **qwen**: Qwen (Markdown format)
# - **gemma_12b**: Gemma 12B (Markdown format)
# - **gemma_27b**: Gemma 27B (Markdown format)
# - **dolphin**: Dolphin (Markdown format)

# %%
