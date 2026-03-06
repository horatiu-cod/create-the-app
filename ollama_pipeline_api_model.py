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
    ApiVlmOptions
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fallback string
FALLBACK_MESSAGE = "Agent execution failed due to API error or empty input. Downstream tasks might be impacted."

def check_and_pull_ollama_model(model_name: str, base_url: str ) -> bool:
    """Check if model exists in Ollama and attempt to pull if not.

    Args:
        model_name: The model name to check/pull

    Returns:
        True if model exists or successfully pulled, False otherwise
    """
    try:
        # Check if model exists
        response = requests.get(f"{base_url}/tags", timeout=2)
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
                f"{base_url}/pull",
                json={"name": model_name},
                stream=True,
                timeout=300,
            )

            if pull_response.status_code == 200:
                # Stream the response to show progress
                for line in pull_response.iter_lines():
                    if line:
                        import json

                        try:
                            data = json.loads(line)
                            status = data.get("status", "")
                            if status:
                                logger.info(f"  {status}", end="\r")
                        except json.JSONDecodeError:
                            pass
                logger.info()  # New line after progress
                logger.info(f"✓ Successfully pulled model '{model_name}'")
                return True
            else:
                logger.error(f"✗ Failed to pull model: HTTP {pull_response.status_code}")
                return False
        return False
    except requests.exceptions.Timeout:
        logger.error("✗ Timeout while trying to pull model (this can take a while)")
        logger.error("Please try pulling manually: ollama pull", model_name)
        return False
    except Exception as e:
        logger.error(f"✗ Error checking/pulling model: {e}")
        return False


def run_ollama_document_converter(input_doc_path: Path, model_name: str = "ibm/granite-docling:258m") -> str:
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    REMOTE_OLLAMA_URL = f"{base_url}/v1/chat/completions"   
    """Example 2: Using Granite-Docling preset with Ollama.

    Returns:
        True if example ran successfully, False if skipped
    """
    print("\n" + "=" * 70)
    print("Example: Granite-Docling with Ollama (pre-configured API type)")
    print("=" * 70)
    print("\nPrerequisites:")
    print("- Install Ollama: https://ollama.ai")
    print("- Pull model: ollama pull ibm/granite-docling:258m")
    print()

    # Check if Ollama is running
    try:
        response = requests.get(f"{base_url}/tags", timeout=2)
        if response.status_code != 200:
            logger.warning("WARNING: Ollama server not responding correctly")
            logger.warning("Skipping Ollama example.\n")
            return FALLBACK_MESSAGE
    except requests.exceptions.RequestException:
        logger.warning("WARNING: Ollama server not running at http://localhost:11434")
        logger.warning("Skipping Ollama example.\n")
        return FALLBACK_MESSAGE

    # Check and pull the model
    #model_name = "ibm/granite-docling:258m"
    if not check_and_pull_ollama_model(model_name, base_url):
        logger.warning("Skipping Ollama example.\n")
        return FALLBACK_MESSAGE

    # Use granite_docling preset with Ollama API runtime
    """
    vlm_options = VlmConvertOptions.from_preset(
        "granite_docling",
        engine_options=ApiVlmEngineOptions(
            runtime_type=VlmEngineType.API_OLLAMA,
            # url is pre-configured for Ollama (http://localhost:11434/v1/chat/completions)
            # model name is pre-configured from the preset
            timeout=90,
        ),
    )
    """
    vlm_options = ApiVlmOptions(
        url=REMOTE_OLLAMA_URL,
        params={
            "model": model_name,
            "temperature": 0.0,
            "max_tokens": 4096,
            # Ollama-specific: to increase context, use 'options' nesting
            "options": {"num_ctx": 8192} 
        },
        #response_format=ResponseFormat.MARKDOWN,
        timeout=300 # Remote calls can take time depending on network/GPU
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

    result = doc_converter.convert(input_doc_path)
    return str(result.document.export_to_markdown())



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