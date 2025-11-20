import streamlit as st
import json
import os
from utils import load_json_file, format_log_for_prompt
from log_analyzer import LogAnalyzer

# Page Configuration
st.set_page_config(
    page_title="Databricks PS AI Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Apple-style Minimalist Design
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F5F5F7;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headings */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E5E5;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #0071e3;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0077ED;
        box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3);
    }
    
    /* File Uploader */
    .stFileUploader {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border: 1px dashed #D1D1D6;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #1D1D1F;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E5E5;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=150)
    st.title("AI Automation")
    st.markdown("---")
    st.markdown("**Model Status**")
    
    # Initialize Model (Lazy loading)
    if 'analyzer' not in st.session_state:
        with st.spinner("Initializing AI Model..."):
            try:
                st.session_state.analyzer = LogAnalyzer()
                st.success("Model Loaded")
            except Exception as e:
                st.error(f"Model Failed: {e}")
    else:
        st.success("Model Ready")

    st.markdown("---")
    st.info("Upload a Databricks log file to begin automated root cause analysis.")

# Main Content
st.title("Databricks Diagnostic AI")
st.markdown("### Automated Root Cause Analysis & Remediation")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload Log File (JSON)", type=['json'])

    if uploaded_file is not None:
        log_data = json.load(uploaded_file)
        st.success(f"File uploaded: {uploaded_file.name}")
        
        with st.expander("View Raw Log Data"):
            st.json(log_data)
            
        if st.button("Analyze Log"):
            with st.spinner("Analyzing log patterns..."):
                log_text = format_log_for_prompt(log_data)
                analysis = st.session_state.analyzer.analyze_log(log_text)
                
                st.markdown("---")
                
                # Results Display
                st.subheader("Analysis Results")
                
                # Root Cause Card
                st.markdown("""
                <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #FF3B30; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h4 style="margin-top: 0; color: #1D1D1F;">🔴 Root Cause</h4>
                    <p style="color: #424245;">{}</p>
                </div>
                """.format(analysis.get('root_cause', 'N/A')), unsafe_allow_html=True)
                
                # Remediation Card
                st.markdown("""
                <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #34C759; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h4 style="margin-top: 0; color: #1D1D1F;">🟢 Recommended Remediation</h4>
                    <p style="color: #424245;">{}</p>
                </div>
                """.format(analysis.get('remediation', 'N/A')), unsafe_allow_html=True)
                
                # Insights Card
                st.markdown("""
                <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 5px solid #0071e3; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <h4 style="margin-top: 0; color: #1D1D1F;">🔵 Strategic Insights</h4>
                    <p style="color: #424245;">{}</p>
                </div>
                """.format(analysis.get('insights', 'N/A')), unsafe_allow_html=True)
                
                # Export
                report_text = f"Analysis Report\n\nRoot Cause: {analysis.get('root_cause')}\n\nRemediation: {analysis.get('remediation')}\n\nInsights: {analysis.get('insights')}"
                st.download_button(
                    label="Download Executive Summary",
                    data=report_text,
                    file_name="analysis_report.txt",
                    mime="text/plain"
                )

with col2:
    st.markdown("### Quick Actions")
    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 12px; margin-bottom: 10px;">
        <b>Load Sample: Cluster Failure</b><br>
        <span style="font-size: 12px; color: gray;">Simulate init script error</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Load Cluster Sample"):
        sample_path = os.path.join("src", "sample_data", "cluster_runtime_log.json")
        with open(sample_path) as f:
            st.session_state.sample_log = json.load(f)
        st.rerun()

    st.markdown("""
    <div style="background-color: white; padding: 15px; border-radius: 12px; margin-bottom: 10px;">
        <b>Load Sample: Job Failure</b><br>
        <span style="font-size: 12px; color: gray;">Simulate OOM / Shuffle error</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Load Job Sample"):
        sample_path = os.path.join("src", "sample_data", "job_run_sample.json")
        with open(sample_path) as f:
            st.session_state.sample_log = json.load(f)
        st.rerun()

# Handle Sample Load State
if 'sample_log' in st.session_state:
    st.markdown("---")
    st.subheader("Sample Data Loaded")
    log_data = st.session_state.sample_log
    
    # Reuse analysis logic (DRY principle would suggest a function here, keeping inline for demo simplicity)
    if st.button("Analyze Sample"):
        with st.spinner("Analyzing sample..."):
            log_text = format_log_for_prompt(log_data)
            analysis = st.session_state.analyzer.analyze_log(log_text)
            
            # Render results (duplicated for simplicity in this single file demo)
            st.markdown(f"**Root Cause:** {analysis.get('root_cause')}")
            st.markdown(f"**Remediation:** {analysis.get('remediation')}")
            st.markdown(f"**Insights:** {analysis.get('insights')}")
