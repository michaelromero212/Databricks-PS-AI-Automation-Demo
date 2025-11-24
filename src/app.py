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

# Custom CSS for Accessible, Professional Design
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #F5F5F7;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headings - WCAG AA compliant */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
        line-height: 1.4;
    }
    
    /* Improved paragraph spacing */
    p {
        line-height: 1.6;
        margin-bottom: 1em;
    }
    
    /* Cards */
    .css-1r6slb0 {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E5E5;
    }
    
    /* Buttons - Accessible purple with good contrast */
    .stButton>button {
        background-color: #7209B7;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 12px 28px;
        font-weight: 500;
        transition: all 0.2s ease;
        font-size: 14px;
    }
    .stButton>button:hover {
        background-color: #5A0896;
        box-shadow: 0 2px 8px rgba(114, 9, 183, 0.3);
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
    
    /* Sidebar - Fix for unreadable text in Dark Mode */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E5E5;
    }
    
    /* Force all text in sidebar to be dark to contrast with white background */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] > p {
        color: #1D1D1F !important;
    }
    
    /* Success messages - High contrast, professional */
    .stSuccess {
        background-color: #FFFFFF !important;
        border: 2px solid #006D77 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: #1D1D1F !important;
        font-weight: 500 !important;
    }
    
    /* Info messages - High contrast, professional */
    .stInfo {
        background-color: #FFFFFF !important;
        border: 2px solid #7209B7 !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: #1D1D1F !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
    }
    
    /* Error messages - High contrast, professional */
    .stError {
        background-color: #FFFFFF !important;
        border: 2px solid #D32F2F !important;
        border-radius: 8px !important;
        padding: 16px !important;
        color: #1D1D1F !important;
        font-weight: 500 !important;
    }

    /* Responsive Design Improvements */
    @media (max-width: 768px) {
        /* Adjust headings for smaller screens */
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
        h3 { font-size: 18px !important; }
        
        /* Make buttons full width on mobile for better touch targets */
        .stButton>button {
            width: 100%;
            margin-bottom: 8px;
        }
        
        /* Adjust card padding */
        div[style*="border-radius: 12px"] {
            padding: 16px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/63/Databricks_Logo.png", width=140)
    st.markdown("### AI Automation")
    
    st.markdown("---")
    
    # 1. System Status Section
    st.markdown("#### 🟢 System Status")
    if 'analyzer' not in st.session_state:
        with st.spinner("Initializing Model..."):
            try:
                st.session_state.analyzer = LogAnalyzer()
                st.success("Model Ready")
            except Exception as e:
                st.error(f"Initialization Failed: {e}")
    else:
        # Determine device for display
        device_name = "CPU"
        if hasattr(st.session_state.analyzer, 'pipeline') and st.session_state.analyzer.pipeline:
            device = st.session_state.analyzer.pipeline.device
            device_name = str(device).upper()
            if "MPS" in device_name or "METAL" in device_name: device_name = "Apple Neural Engine (MPS)"
            elif "CUDA" in device_name: device_name = "NVIDIA GPU (CUDA)"
        
        st.markdown(f"""
        <div style="background-color: #F5F5F7; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #E5E5E5;">
            <small style="color: #6E6E73;">Active Inference Engine</small><br>
            <strong style="color: #1D1D1F;">{device_name}</strong>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Analysis Configuration
    st.markdown("#### ⚙️ Configuration")
    
    with st.expander("Model Settings", expanded=True):
        temperature = st.slider(
            "Creativity (Temperature)",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            help="Higher values make the output more creative but less deterministic."
        )
        
        max_tokens = st.slider(
            "Max Response Length",
            min_value=256,
            max_value=1024,
            value=512,
            step=128,
            help="Maximum number of tokens to generate."
        )

    # 3. Resources Section
    st.markdown("#### 📚 Resources")
    st.markdown("""
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <a href="https://docs.databricks.com/" target="_blank" style="text-decoration: none; color: #006D77; font-weight: 500;">📄 Databricks Documentation</a>
        <a href="https://kb.databricks.com/" target="_blank" style="text-decoration: none; color: #006D77; font-weight: 500;">🧠 Knowledge Base</a>
        <a href="https://status.databricks.com/" target="_blank" style="text-decoration: none; color: #006D77; font-weight: 500;">🚦 System Status</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #86868B; font-size: 11px;">
        Databricks Diagnostic AI v1.2.0<br>
        &copy; 2025 Databricks PS
    </div>
    """, unsafe_allow_html=True)

# Main Content
st.title("Databricks Diagnostic AI")
st.markdown("### Automated Root Cause Analysis & Remediation")

col1, col2 = st.columns([2, 1])

# Helper function to display analysis results - DRY principle
def display_analysis_results(analysis):
    """Display analysis results with accessible, colorblind-safe design"""
    st.markdown("---")
    st.subheader("Analysis Results")
    
    # Critical/Root Cause Card - Orange (visible to all colorblind types)
    # Using solid border and "CRITICAL" label
    st.markdown(f"""
    <div style="background-color: white; padding: 24px; border-radius: 12px; 
                border-left: 6px solid #FF6B00; margin-bottom: 24px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="margin: 0 0 16px 0; color: #1D1D1F; font-size: 18px;">CRITICAL - Root Cause</h4>
        <p style="color: #1D1D1F; margin: 0; font-size: 15px; line-height: 1.7;">{analysis.get('root_cause', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Success/Remediation Card - Teal (colorblind-safe alternative to green)
    # Using dashed border and "ACTION" label
    st.markdown(f"""
    <div style="background-color: white; padding: 24px; border-radius: 12px; 
                border-left: 6px dashed #006D77; margin-bottom: 24px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="margin: 0 0 16px 0; color: #1D1D1F; font-size: 18px;">ACTION REQUIRED - Recommended Remediation</h4>
        <p style="color: #1D1D1F; margin: 0; font-size: 15px; line-height: 1.7;">{analysis.get('remediation', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Information/Insights Card - Purple (colorblind-safe alternative to blue)
    # Using dotted border and "INSIGHTS" label
    st.markdown(f"""
    <div style="background-color: white; padding: 24px; border-radius: 12px; 
                border-left: 6px dotted #7209B7; margin-bottom: 24px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <h4 style="margin: 0 0 16px 0; color: #1D1D1F; font-size: 18px;">INSIGHTS - Strategic Context</h4>
        <p style="color: #1D1D1F; margin: 0; font-size: 15px; line-height: 1.7;">{analysis.get('insights', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Export
    report_text = f"""Analysis Report
    
Root Cause: {analysis.get('root_cause')}

Remediation: {analysis.get('remediation')}

Insights: {analysis.get('insights')}"""
    
    st.download_button(
        label="Download Executive Summary",
        data=report_text,
        file_name="analysis_report.txt",
        mime="text/plain"
    )

with col1:
    # Check if we have sample data loaded
    if 'sample_log' in st.session_state and 'sample_name' in st.session_state:
        st.success(f"Sample loaded: {st.session_state.sample_name}")
        
        col_clear, col_show = st.columns([1, 3])
        with col_clear:
            if st.button("Clear Sample"):
                del st.session_state.sample_log
                del st.session_state.sample_name
                st.rerun()
        
        with st.expander("View Sample Data", expanded=False):
            st.json(st.session_state.sample_log)
        
        if st.button("Analyze Sample", type="primary"):
            if 'analyzer' in st.session_state:
                with st.spinner("Analyzing log patterns..."):
                    try:
                        log_text = format_log_for_prompt(st.session_state.sample_log)
                        analysis = st.session_state.analyzer.analyze_log(
                            log_text, 
                            temperature=temperature, 
                            max_new_tokens=max_tokens
                        )
                        display_analysis_results(analysis)
                    except Exception as e:
                        st.error(f"Analysis failed: {str(e)}")
            else:
                st.error("Model not initialized. Please check sidebar status.")
    else:
        # File uploader (only show when no sample loaded)
        uploaded_file = st.file_uploader("Upload Log File (JSON)", type=['json'])
        
        if uploaded_file is not None:
            try:
                log_data = json.load(uploaded_file)
                st.success(f"File uploaded: {uploaded_file.name}")
                
                with st.expander("View Raw Log Data"):
                    st.json(log_data)
                    
                if st.button("Analyze Log", type="primary"):
                    if 'analyzer' in st.session_state:
                        with st.spinner("Analyzing log patterns..."):
                            try:
                                log_text = format_log_for_prompt(log_data)
                                analysis = st.session_state.analyzer.analyze_log(
                                    log_text,
                                    temperature=temperature,
                                    max_new_tokens=max_tokens
                                )
                                display_analysis_results(analysis)
                            except Exception as e:
                                st.error(f"Analysis failed: {str(e)}")
                    else:
                        st.error("Model not initialized. Please check sidebar status.")
            except json.JSONDecodeError:
                st.error("Invalid JSON file. Please upload a valid JSON log file.")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")

with col2:
    st.markdown("### Quick Actions")
    
    # Cluster Sample Card
    st.markdown("""
    <div style="background-color: white; padding: 18px; border-radius: 12px; 
                margin-bottom: 16px; border: 1px solid #E5E5E5;">
        <b style="color: #1D1D1F; font-size: 15px;">Load Sample: Cluster Failure</b><br>
        <span style="font-size: 13px; color: #6E6E73; line-height: 1.6;">Simulate init script error</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Load Cluster Sample", key="cluster_sample"):
        try:
            sample_path = os.path.join("src", "sample_data", "cluster_runtime_log.json")
            with open(sample_path) as f:
                st.session_state.sample_log = json.load(f)
                st.session_state.sample_name = "Cluster Runtime Failure"
            st.rerun()
        except FileNotFoundError:
            st.error("Sample file not found. Please check the file path.")
        except Exception as e:
            st.error(f"Error loading sample: {str(e)}")

    # Job Sample Card
    st.markdown("""
    <div style="background-color: white; padding: 18px; border-radius: 12px; 
                margin-bottom: 16px; border: 1px solid #E5E5E5;">
        <b style="color: #1D1D1F; font-size: 15px;">Load Sample: Job Failure</b><br>
        <span style="font-size: 13px; color: #6E6E73; line-height: 1.6;">Simulate OOM / Shuffle error</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Load Job Sample", key="job_sample"):
        try:
            sample_path = os.path.join("src", "sample_data", "job_run_sample.json")
            with open(sample_path) as f:
                st.session_state.sample_log = json.load(f)
                st.session_state.sample_name = "Job Run Failure"
            st.rerun()
        except FileNotFoundError:
            st.error("Sample file not found. Please check the file path.")
        except Exception as e:
            st.error(f"Error loading sample: {str(e)}")

# Footer with accessibility information
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6E6E73; font-size: 12px; padding: 20px; line-height: 1.8;">
    <p style="margin-bottom: 8px;">This application is designed with accessibility in mind, including WCAG AA compliance and colorblind-safe design.</p>
    <p style="margin: 0;">Color scheme: Orange (Critical), Teal (Action), Purple (Info) - visible to all types of color vision deficiency.</p>
</div>
""", unsafe_allow_html=True)
