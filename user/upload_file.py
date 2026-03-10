import streamlit as st
import os
import sys
import logging

# Add project root to path so we can import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.formatter.formatter_agent import FormatterAgent
from agents.differ.differ_agent import DifferAgent
from agents.summarizer.summarizer_agent import SummarizerAgent
from agents.analyser.analyser_agent import AnalyserAgent
from agents.reporter.reporter_agent import ReporterAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INPUT_DIR = "data/input"
OUTPUT_DIR = "output"

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

st.set_page_config(page_title="Multi-Agent PDF Digest", page_icon="📝", layout="wide")

st.title("🛸 Multi-Agent PDF Digest System")
st.markdown("Upload the required PDFs to analyze and generate a final report.")

st.sidebar.header("Required Files")
st.sidebar.markdown("- `memoriu.pdf`\n- `formular_initial.pdf`\n- `formular_modificat.pdf`")

uploaded_memoriu = st.file_uploader("Upload memoriu.pdf", type="pdf")
uploaded_initial = st.file_uploader("Upload formular_initial.pdf", type="pdf")
uploaded_modified = st.file_uploader("Upload formular_modificat.pdf", type="pdf")

if st.button("Run Multi-Agent Pipeline"):
    if not (uploaded_memoriu and uploaded_initial and uploaded_modified):
        st.error("Please upload all 3 required files.")
    else:
        with st.spinner("Saving uploaded files..."):
            for f, n in [(uploaded_memoriu, "memoriu.pdf"), (uploaded_initial, "formular_initial.pdf"), (uploaded_modified, "formular_modificat.pdf")]:
                with open(os.path.join(INPUT_DIR, n), "wb") as out:
                    out.write(f.getbuffer())

        st.success("Files saved. Executing Agent Pipeline...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # 1. Formatter Agent
            status_text.text("Agent 1: Formatter Agent is converting PDFs to Markdown...")
            formatter = FormatterAgent(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR)
            formatter.process(["memoriu.pdf", "formular_initial.pdf", "formular_modificat.pdf"])
            progress_bar.progress(20)

            # 2. Differ Agent
            status_text.text("Agent 2: Differ Agent is comparing forms...")
            differ = DifferAgent(output_dir=OUTPUT_DIR)
            differ.process("formular_initial.md", "formular_modificat.md", "differs.md")
            progress_bar.progress(40)

            # 3. Summarizer Agent
            status_text.text("Agent 3: Summarizer Agent is summarizing memoriu.md...")
            summarizer = SummarizerAgent(output_dir=OUTPUT_DIR)
            summarizer.process("memoriu.md", "summary.md")
            progress_bar.progress(60)

            # 4. Analyser Agent
            status_text.text("Agent 4: Analyser Agent is verifying requirements against diffs...")
            analyser = AnalyserAgent(output_dir=OUTPUT_DIR)
            analyser.process("summary.md", "differs.md", "raport.md")
            progress_bar.progress(80)

            # 5. Reporter Agent
            status_text.text("Agent 5: Reporter Agent is generating the final PDF...")
            reporter = ReporterAgent(output_dir=OUTPUT_DIR)
            final_report_path = reporter.process("raport.md", "raport_final.pdf")
            progress_bar.progress(100)
            
            status_text.text("Pipeline Completed Successfully!")
            st.balloons()
            
            if final_report_path and os.path.exists(final_report_path):
                with open(final_report_path, "rb") as f:
                    st.download_button("Download Final Report", f, file_name=os.path.basename(final_report_path), type="primary")

            # Display the comparison report if it exists
            html_report_path = os.path.join(OUTPUT_DIR, "comparison_report.html")
            if os.path.exists(html_report_path):
                st.markdown("---")
                st.subheader("📑 Visual Comparison Report")
                with open(html_report_path, "r", encoding="utf-8") as f:
                    html_data = f.read()
                import streamlit.components.v1 as components
                components.html(html_data, height=800, scrolling=True)

        except Exception as e:
            st.error(f"Pipeline failed: {str(e)}")
