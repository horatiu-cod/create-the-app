# 🛸 Multi-Agent PDF Digest
A multi-agent system that processes PDF documents uploaded by the user, verifies the accuracy of the information, and generates a report.

## Overview
This system processes 3 required PDF files using a sequential pipeline of 5 specialized agents:
1. **Formatter Agent**: Converts PDFs to Markdown.
2. **Differ Agent**: Compares initial and modified forms to highlight changes.
3. **Summarizer Agent**: Summarizes the requirements from the memorandum.
4. **Analyser Agent**: Cross-references the summary requirements to the actual diffs.
5. **Reporter Agent**: Generates a final PDF report detailing the analysis.

## Prerequisites
- Python 3.10+
- `wkhtmltopdf` (required by `pdfkit` to generate the final PDF report. Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/) and add it to your system PATH).

## Installation

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd c:\AntiGravSpace\create-the-app
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the environment**:
   Edit the `.env` file in the root directory and add your API credentials:
   ```env
   OPENAI_API_KEY=your_openai_or_vllm_api_key_here
   OPENAI_BASE_URL=https://api.openai.com/v1 # or your kaggle url e.g. http://localhost:8000/v1
   ```

## Running the Application

This project includes a Web Interface built with Streamlit.

1. Start the Streamlit app:
   ```bash
   streamlit run user/upload_file.py
   ```

2. Open the URL provided in your terminal (usually `http://localhost:8501`).

3. Upload the 3 required PDF files using the UI:
   - `memoriu.pdf` (The memorandum containing requirements)
   - `formular_initial.pdf` (The initial state document)
   - `formular_modificat.pdf` (The modified state document)

4. Click **Run Multi-Agent Pipeline** and wait for the agents to process the files. You will see progress updates. Once complete, you can download the final generated `raport_final.pdf`.

## Running Tests

To verify the agents and tools structure with mocked LLM calls, run:
```bash
pytest tests/
```
