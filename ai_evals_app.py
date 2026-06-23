import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
from datetime import datetime

# Page Configuration for widescreen premium dashboard layout
st.set_page_config(
    page_title="AI Product Evals & Observability Controller | Designed by Dhaval Kareliya",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Injection to guarantee exact compliance with all Tasks
st.markdown("""
<style>
  /* Task 5: Spacing - Add more padding on left and right side (around 3% more than default) */
  div[class*="stAppViewBlockContainer"] {
    padding-left: 6% !important;
    padding-right: 6% !important;
    max-width: 95% !important;
    background-color: #f8fafc;
  }

  .stApp {
    background-color: #f8fafc;
  }

  /* Force highly legible text colors on all native Streamlit widgets */
  div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    color: #000000 !important;
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
  }
  div[data-testid="stTextArea"] label p, div[data-testid="stTextInput"] label p {
    color: #000000 !important;
    font-weight: 700 !important;
  }

  /* Slider Value & Label Legibility - Task 4 (Solid Black) */
  div[data-testid="stSlider"] label p {
    color: #000000 !important;
    font-weight: 700 !important;
  }
  div[data-testid="stSlider"] div[data-testid="stWidgetValue"] {
    color: #2563eb !important;
    font-weight: 700 !important;
  }

  /* Task 1 & 2: Inactive/Secondary Buttons (White background, solid black border, black font) */
  div.stButton > button[kind="secondary"],
  button[data-testid="baseButton-secondary"] {
    border: 2px solid #000000 !important;
    color: #000000 !important;
    background-color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
  }
  div.stButton > button[kind="secondary"]:hover,
  button[data-testid="baseButton-secondary"]:hover {
    background-color: #f1f5f9 !important;
    color: #000000 !important;
    border-color: #000000 !important;
  }

  /* Task 2 & 3: Active/Primary Buttons (Blue background, white font) */
  div.stButton > button[kind="primary"],
  button[data-testid="baseButton-primary"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
    border: 2px solid #2563eb !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
  }
  div.stButton > button[kind="primary"]:hover,
  button[data-testid="baseButton-primary"]:hover {
    background-color: #1d4ed8 !important;
    color: #ffffff !important;
    border-color: #1d4ed8 !important;
  }

  /* Task 4: Force All Headers & Specified Text Blocks to Solid Black */
  h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
    font-weight: 800 !important;
  }

  /* Task 4: Expander header is solid black font */
  div[data-testid="stExpander"] div[role="button"] p {
    color: #000000 !important; 
    font-weight: 700 !important;
    font-size: 15px !important;
  }
  div[data-testid="stExpander"] {
    background-color: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
  }
  div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    color: #1e293b !important;
    background-color: #ffffff !important;
    border-radius: 8px;
    padding: 16px;
  }

  /* Custom White Card Wrappers */
  .custom-card {
    background-color: #ffffff !important;
    padding: 24px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    margin-bottom: 24px;
  }

  /* High Specificity Rule: Prevent Streamlit Dark Theme/Global styles from making light metric card text white */
  div.stApp .metric-label-black {
    color: #000000 !important;
  }
  div.stApp .metric-value-black {
    color: #000000 !important;
  }
</style>
""", unsafe_allow_html=True)

# Initialize Session States for Playground Presets & Expander Toggles
if 'show_guide' not in st.session_state:
    st.session_state.show_guide = True
if 'play_context' not in st.session_state:
    st.session_state.play_context = "The school science lab allows students to reserve a microscope workstation for 45 minutes. Safety goggles must be worn at all times, and there is no reservation fee."
if 'play_query' not in st.session_state:
    st.session_state.play_query = "How long can I reserve a workstation, and is there a reservation fee?"
if 'play_output' not in st.session_state:
    st.session_state.play_output = "You can reserve a workstation for 10 minutes and there is a 5 dollar booking fee."
if 'active_preset' not in st.session_state:
    st.session_state.active_preset = "hallucinated"

# Default Baseline Sliders
if 'faithfulness' not in st.session_state:
    st.session_state.faithfulness = 10
if 'relevancy' not in st.session_state:
    st.session_state.relevancy = 85
if 'hallucination' not in st.session_state:
    st.session_state.hallucination = 70

# Widescreen Executive Header Panel (Proportional split: Title vs Actions Menu)
col_title, col_actions = st.columns([6, 4])

with col_title:
    st.markdown("""
    <div style="background-color: transparent; padding: 12px 12px 12px 0px; border-radius: 12px; margin-bottom: 8px;">
        <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px;">
            <span style="background-color: #ffffff; color: #475569; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 9999px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);">
                AI Product Operations • Quality Assurance Framework
            </span>
        <div style="background-color: #f5f3ff; color: #4f46e5; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 9999px; border: 1px solid #ddd6fe; white-space: nowrap; display: inline-flex; align-items: center; gap: 12px;">
    <span>Designed by Dhaval Kareliya</span>
    <span style="color: #cbd5e1;">|</span>
    <a href="https://www.linkedin.com/in/dhavalk21/" target="_blank" style="text-decoration: none; color: #4f46e5; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;">
        <svg style="width: 12px; height: 12px;" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
        LinkedIn
    </a>
    <span style="color: #cbd5e1;">|</span>
    <a href="https://github.com/dhavalk21/" target="_blank" style="text-decoration: none; color: #4f46e5; font-weight: bold; display: inline-flex; align-items: center; gap: 4px;">
        <svg style="width: 12px; height: 12px;" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
        GitHub
    </a>
</div>
        <h1 style="color: #000000; font-size: 28px; font-weight: 800; margin: 0 0 4px 0; letter-spacing: -0.025em;">
            Production AI Evals &amp; Observability Controller
        </h1>
        <p style="color: #475569; font-size: 14.5px; margin: 0; line-height: 1.5; font-weight: 500;">
            Verify, monitor, and establish reliable release gates for LLM system performance. Define multidimensional criteria to proactively predict user retention and satisfaction.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_actions:
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    act_col1, act_col2, act_col3 = st.columns(3)
    
    with act_col1:
        # Task 1: "Show Guide" uses White/Black styled secondary button
        if st.button("Show Guide", use_container_width=True, key="hdr_show_guide", type="secondary"):
            st.session_state.show_guide = not st.session_state.show_guide
            st.rerun()
            
    with act_col2:
        # Task 1: "Test Case 1" uses White/Black styled secondary button
        if st.button("Test Case 1", use_container_width=True, key="hdr_tc1", type="secondary", help="Loads a perfect grounded response example"):
            st.session_state.play_context = "The school science lab allows students to reserve a microscope workstation for 45 minutes. Safety goggles must be worn at all times, and there is no reservation fee."
            st.session_state.play_query = "How long can I reserve a microscope workstation, and is there any fee?"
            st.session_state.play_output = "You can reserve a workstation for 45 minutes, and there is no reservation fee."
            st.session_state.active_preset = "grounded"
            st.session_state.faithfulness = 100
            st.session_state.relevancy = 100
            st.session_state.hallucination = 0
            st.rerun()
            
    with act_col3:
        # Task 1: "Test Case 2" uses White/Black styled secondary button
        if st.button("Test Case 2", use_container_width=True, key="hdr_tc2", type="secondary", help="Loads a hallucinated fact response example"):
            st.session_state.play_context = "The school science lab allows students to reserve a microscope workstation for 45 minutes. Safety goggles must be worn at all times, and there is no reservation fee."
            st.session_state.play_query = "How long can I reserve a workstation, and is there a reservation fee?"
            st.session_state.play_output = "You can reserve a workstation for 10 minutes and there is a 5 dollar booking fee."
            st.session_state.active_preset = "hallucinated"
            st.session_state.faithfulness = 10
            st.session_state.relevancy = 85
            st.session_state.hallucination = 70
            st.rerun()

# Collapsible Guide (Task 4: Heading is Black)
if st.session_state.show_guide:
    st.markdown("""
    <div style="background-color: white; padding: 24px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);">
        <h3 style="color: #000000 !important; font-size: 16px; font-weight: 700; margin: 0 0 8px 0; display: flex; align-items: center; gap: 8px;">
            <svg style="width: 20px; height: 20px; color: #2563eb;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
            Show Guide: How to Run LLM Quality Evaluations (With Examples)
        </h3>
        <p style="color: #475569; font-size: 13px; margin-bottom: 16px;">
            Product managers run these evaluations (Evals) using golden datasets to avoid deploying a model that outputs false facts or fails user queries.
        </p>
        <div style="background-color: #eff6ff; padding: 16px; border-radius: 8px; border: 1px solid #bfdbfe; color: #1e3a8a; margin-bottom: 16px; font-size: 13px; font-weight: 500;">
            <p style="font-weight: 700; color: #1e40af; margin-bottom: 4px;">Step-by-Step Instructions:</p>
            <ol style="margin-left: 20px; list-style-type: decimal;">
                <li>Click on either <strong>Test Case 1</strong> or <strong>Test Case 2</strong> buttons inside the top right header menu to load sample data.</li>
                <li>Inspect the source context (what the database knows) and compare it with the LLM response.</li>
                <li>Click the blue **"Run AI-Judge Evaluation Simulation"** button. The simulated judge reads, checks, and scores the inputs.</li>
                <li>Look at the top KPI cards—the evaluation results instantly update your **Predicted Churn Risk** and **Expected CSAT**!</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Main Content Columns (Task 5: 36% Left, 6% Spacer, 58% Right split layout)
col_left, col_spacer, col_right = st.columns([36, 6, 58])

with col_left:
    # Live Evaluation Playground Banner
    st.markdown("""
    <div style="background-color: #eff6ff; padding: 20px; border-radius: 12px; border: 1px solid #bfdbfe; color: #1e3a8a; margin-bottom: 20px;">
        <h3 style="color: #1e40af; font-size: 16px; font-weight: 700; margin: 0 0 4px 0; display: flex; align-items: center; gap: 8px;">
            <svg style="width: 20px; height: 20px;" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Live Evaluation Playground
        </h3>
        <p style="color: #2563eb; font-size: 12.5px; margin: 0; line-height: 1.4; font-weight: 500;">
            Select an evaluation scenario or customize the fields to test the heuristic AI Judge.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Task 2: Active blue preset selector buttons vs. inactive white/black outline buttons
    st.markdown("<p style='font-size:12px; font-weight:600; color:#000000;'>Choose a Scenario:</p>", unsafe_allow_html=True)
    p_col1, p_col2, p_col3 = st.columns(3)
    
    # Helper to load presets
    def load_preset(preset_key):
        if preset_key == "hallucinated":
            st.session_state.play_context = "we have 2 plan: 1) gold client 20 euro and 14 day refund policy. 2) silver plan 10 euro and no refund policy"
            st.session_state.play_query = "What is the cost of the silver plan, and what is your refund policy?"
            st.session_state.play_output = "Silver plan cost 10 euro and 10 day return policy"
        elif preset_key == "offtopic":
            st.session_state.play_context = "Our premium tier costs €49/month and includes 100 API credits. Our basic tier costs €19/month and includes 10 API credits. No refunds are allowed."
            st.session_state.play_query = "What is the cost of the premium tier, and what is your refund policy?"
            st.session_state.play_output = "We are running a special sale on shoes today! Get up to 50% off on all sneakers by using code SALE50."
        elif preset_key == "grounded":
            st.session_state.play_context = "we have 2 plan: 1) gold client 20 euro and 14 day refund policy. 2) silver plan 10 euro and no refund policy"
            st.session_state.play_query = "What is the cost of the silver plan, and what is your refund policy?"
            st.session_state.play_output = "The silver plan costs 10 euro and has no refund policy."
        st.session_state.active_preset = preset_key

    with p_col1:
        if st.button("⚠️ Hallucinated", type="primary" if st.session_state.active_preset == "hallucinated" else "secondary", use_container_width=True):
            load_preset("hallucinated")
            st.rerun()
    with p_col2:
        if st.button("❌ Off-Topic", type="primary" if st.session_state.active_preset == "offtopic" else "secondary", use_container_width=True):
            load_preset("offtopic")
            st.rerun()
    with p_col3:
        if st.button("✅ Grounded", type="primary" if st.session_state.active_preset == "grounded" else "secondary", use_container_width=True):
            load_preset("grounded")
            st.rerun()

    # Playground Inputs
    text_context = st.text_area("Grounded Source Context", value=st.session_state.play_context, height=90)
    text_query = st.text_input("User Question", value=st.session_state.play_query)
    text_output = st.text_area("Generated Output Response", value=st.session_state.play_output, height=90)

    # Task 3: Simulation Evaluation Trigger (The Blue Button)
    if st.button("Run AI-Judge Evaluation Simulation", type="primary", use_container_width=True):
        c = text_context.lower().strip()
        q = text_query.lower().strip()
        o = text_output.lower().strip()
        
        evaluated_faithfulness = 100
        evaluated_relevancy = 100
        evaluated_hallucination = 0
        
        # Standardized search keywords list
        policy_keywords = ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years', 'return', 'refund', 'policy', 'guarantee']
        currency_keywords = ['euro', 'euros', 'eur', 'usd', 'dollar', 'dollars', 'credits', 'price', 'cost']
        negation_keywords = ['no', 'not', 'never', 'non', 'cannot', 'without']

        # Safeguard against completely empty or trash inputs
        if len(c) < 5 or len(o) < 5 or len(q) < 5:
            st.session_state.faithfulness = 10
            st.session_state.relevancy = 10
            st.session_state.hallucination = 80
            st.warning("Inputs are too short or empty! Evaluating default fallback low-quality scores.")
        else:
            # Heuristics A: Numerical validation & structural unit mismatch
            output_numbers = re.findall(r'\b\d+\b', o)
            for num in output_numbers:
                output_idx = o.find(num)
                if output_idx != -1:
                    snippet = o[max(0, output_idx - 25): min(len(o), output_idx + 25)]
                    is_output_temporal = any(w in snippet for w in policy_keywords)
                    is_output_currency = any(w in snippet for w in currency_keywords)
                    
                    context_idx = c.find(num)
                    if context_idx != -1:
                        c_snippet = c[max(0, context_idx - 25): min(len(c), context_idx + 25)]
                        is_context_temporal = any(w in c_snippet for w in policy_keywords)
                        is_context_currency = any(w in c_snippet for w in currency_keywords)
                        
                        if is_output_temporal and not is_context_temporal:
                            evaluated_faithfulness -= 40
                            evaluated_hallucination += 45
                        elif is_output_currency and not is_context_currency:
                            evaluated_faithfulness -= 30
                            evaluated_hallucination += 35
                    else:
                        evaluated_faithfulness -= 45
                        evaluated_hallucination += 50

            # Heuristics B: Strict Policy Contradiction mapping
            if "no refund" in c or "no return" in c:
                has_refund_claim = any(word in o for word in policy_keywords) and not any(w in o for w in ['no refund', 'no return'])
                if has_refund_claim:
                    evaluated_faithfulness -= 45
                    evaluated_hallucination += 40

            # Heuristics C: Relevancy validation
            clean_q = re.sub(r'[^\w\s]', '', q)
            clean_o = re.sub(r'[^\w\s]', '', o)
            stop_words = {'what', 'is', 'the', 'of', 'and', 'a', 'to', 'in', 'your', 'my', 'does', 'do', 'how', 'much', 'for', 'are', 'an', 'you'}
            
            query_words = [w for w in clean_q.split() if len(w) > 3 and w not in stop_words]
            match_count = sum(1 for w in query_words if w in clean_o)
            
            if query_words:
                overlap_ratio = match_count / len(query_words)
                evaluated_relevancy = int(30 + (overlap_ratio * 70))
            else:
                evaluated_relevancy = 50

        # Sync scores directly back to sliders
        st.session_state.faithfulness = min(100, max(10, evaluated_faithfulness))
        st.session_state.relevancy = min(100, max(10, evaluated_relevancy))
        st.session_state.hallucination = min(80, max(0, evaluated_hallucination))
        st.toast("Evaluation metrics updated successfully!", icon="✅")

    st.markdown("---")

    # Section 1: Sliders Calibration (Task 4: Title is Black)
    st.markdown("<h3 style='color: #000000 !important; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.5rem;'>1. System Metric Calibration</h3>", unsafe_allow_html=True)
    
    slide_faithfulness = st.slider(
        "Faithfulness (Ragas) (%)",
        min_value=10, max_value=100, step=5,
        key="faithfulness",
        help="Checks if claims in output exist in the source document. 💡 Ideal Target: > 85%"
    )
    slide_relevancy = st.slider(
        "Answer Relevancy (DeepEval) (%)",
        min_value=10, max_value=100, step=5,
        key="relevancy",
        help="Checks if the output directly answers the user query without adding unrelated fluff. 💡 Ideal Target: > 80%"
    )
    slide_hallucination = st.slider(
        "Hallucination Rate (DeepEval) (%)",
        min_value=0, max_value=80, step=2,
        key="hallucination",
        help="Detects completely fabricated details contradicting context facts. 💡 Ideal Target: < 5%"
    )

    # Section 2: Weight Configuration (Task 4: Title is Black)
    st.markdown("<h3 style='color: #000000 !important; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.5rem; margin-top: 1rem;'>2. KPI Weight Configuration</h3>", unsafe_allow_html=True)
    weight_faith = st.slider(
        "Faithfulness Impact Weight",
        min_value=0, max_value=100, step=5, value=40,
        help="The impact of factual grounding on the Overall Quality Index. 💡 Ideal Range: 30% - 50%"
    )
    weight_rel = st.slider(
        "Answer Relevancy Weight",
        min_value=0, max_value=100, step=5, value=40,
        help="The impact of user alignment on the Overall Quality Index. 💡 Ideal Range: 30% - 50%"
    )
    weight_hall = st.slider(
        "Hallucination Penalty Weight",
        min_value=0, max_value=100, step=5, value=20,
        help="How strictly hallucinations are penalized. Higher weights amplify user churn predictions if hallucination levels rise. 💡 Ideal Range: 15% - 30%"
    )

# Mathematical Engine calculation processes
total_weight = weight_faith + weight_rel + weight_hall
if total_weight == 0:
    total_weight = 1

f_factor = (weight_faith / total_weight)
r_factor = (weight_rel / total_weight)
h_factor = (weight_hall / total_weight)

quality_score = (slide_faithfulness * f_factor) + (slide_relevancy * r_factor) + ((100 - slide_hallucination) * h_factor)

churn_risk = (100 - quality_score) * 1.5
if slide_hallucination > 15:
    churn_risk += (slide_hallucination - 15) * 2.2
churn_risk = min(99.5, max(1.5, churn_risk))

projected_csat = 1.0 + (quality_score / 100.0) * 4.0

# Right Analytics Workspace Panel
with col_right:
    # 3 High-Impact KPI Cards (Task 4: Card Headers and Metric Values are explicitly targeted in CSS for Black coloring)
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    with kpi_col1:
        st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 4px solid #2563eb; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05); position: relative; overflow: hidden;">
            <span class="metric-label-black" style="display: block; text-transform: uppercase; font-size: 11px; font-weight: 700; color: #000000 !important; tracking-wider">Overall Quality Index</span>
            <span class="metric-value-black" style="display: block; font-size: 28px; font-weight: 800; color: #000000 !important; margin-top: 4px;">{quality_score:.1f}%</span>
            <span style="display: block; font-size: 11px; color: {'#10b981' if quality_score >= 80 else '#ef4444'}; font-weight: 700; margin-top: 8px;">
                {'● Acceptable' if quality_score >= 80 else '▲ Unsafe Baseline'}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        if churn_risk <= 20.0:
            churn_delta = "● Low Risk"
            churn_color = "#10b981"
        elif churn_risk <= 45.0:
            churn_delta = "■ Medium Risk"
            churn_color = "#f59e0b"
        else:
            churn_delta = "▲ High Churn Alert"
            churn_color = "#ef4444"

        st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 4px solid #1e293b; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.05); position: relative; overflow: hidden;">
            <span class="metric-label-black" style="display: block; text-transform: uppercase; font-size: 11px; font-weight: 700; color: #000000 !important; tracking-wider">Predicted Churn Risk</span>
            <span class="metric-value-black" style="display: block; font-size: 28px; font-weight: 800; color: #000000 !important; margin-top: 4px;">{churn_risk:.1f}%</span>
            <span style="display: block; font-size: 11px; color: {churn_color}; font-weight: 700; margin-top: 8px;">
                {churn_delta}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col3:
        st.markdown(f"""
        <div style="background-color: #0f172a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; border-top: 4px solid #10b981; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
            <span style="display: block; text-transform: uppercase; font-size: 11px; font-weight: 700; color: #94a3b8; tracking-wider">Projected Customer CSAT</span>
            <span style="display: block; font-size: 28px; font-weight: 800; color: #10b981; margin-top: 4px;">{projected_csat:.2f} / 5.0</span>
            <span style="display: block; font-size: 11px; color: #cbd5e1; font-weight: 500; margin-top: 8px;">
                {'Target Met' if projected_csat >= 4.0 else 'Below SLA'}
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Timeline Chart (Task 4: Title & Axes/Legend are Black)
    st.markdown("<h3 style='color: #000000 !important; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.5rem;'>Quality Baseline Timeline</h3>", unsafe_allow_html=True)
    baseline_runs = [55.0, 58.5, 62.0, 71.5, 76.0]
    runs = baseline_runs + [quality_score]
    x_runs = ["Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Active"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_runs, y=[80]*6,
        mode="lines",
        name="Target Threshold (80%)",
        line=dict(color="#f43f5e", dash="dash", width=1.5)
    ))
    fig.add_trace(go.Scatter(
        x=x_runs, y=runs,
        mode="lines+markers",
        name="Evaluated Score",
        line=dict(color="#4f46e5", width=3),
        marker=dict(size=8, color="#10b981" if quality_score >= 80 else "#ef4444")
    ))
    fig.update_layout(
        yaxis_range=[0, 100],
        margin=dict(l=20, r=20, t=10, b=10),
        height=220,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="black")),
        xaxis=dict(tickfont=dict(color="black")),
        yaxis=dict(tickfont=dict(color="black"))
    )
    
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Industry Standards Info Cards
    st.markdown("""
    <div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px; box-shadow: 0 1px 2px 0 rgba(0,0,0,0.05);">
        <span style="font-size: 11px; font-weight: bold; background-color: #f5f3ff; color: #4f46e5; padding: 4px 12px; border-radius: 6px; text-transform: uppercase; border: 1px solid #ddd6fe;">
            Ragas &amp; DeepEval Framework Compliance
        </span>
        <div style="display: grid; grid-template-columns: 1fr; gap: 16px; margin-top: 16px;">
          <div>
            <p style="font-size: 13px; font-weight: 700; color: #0f172a; margin: 0;">Ragas Framework: Faithfulness</p>
            <p style="font-size: 11px; color: #64748b; margin: 4px 0 0 0; line-height: 1.5;">
                Utilized to ensure information is strictly grounded. Ragas extracts key factual statements from the generated answer and queries an LLM Judge to check if each statement is explicitly backed by the retrieved context papers.
            </p>
          </div>
          <div>
            <p style="font-size: 13px; font-weight: 700; color: #0f172a; margin: 0;">DeepEval: Relevancy &amp; Hallucinations</p>
            <p style="font-size: 11px; color: #64748b; margin: 4px 0 0 0; line-height: 1.5;">
                Maintains output quality. DeepEval maps the cosine similarity between generated responses and initial prompt intents to compute answer relevancy, and cross-references source contradictions to output a strict hallucination percentage.
            </p>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Automated release briefing memo (Task 4: Title is Black)
    st.markdown("<h3 style='color: #000000 !important; font-weight: 800; font-size: 1.15rem; margin-bottom: 0.5rem;'>System Quality Release Briefing</h3>", unsafe_allow_html=True)
    memo = f"""### 💼 PRODUCT OPERATIONS & LLM EVALUATION BRIEF
Generated: {datetime.now().strftime('%B %d, %Y')}
Author: Dhaval Kareliya | AI Product Management Operations
=========================================================================

1. EVALUATION CRITERIA METRICS (Industry Standard Frameworks)
-------------------------------------------------------------------------
* Faithfulness Score (Ragas Grounding) : {slide_faithfulness}%
* Answer Relevancy Score (DeepEval)    : {slide_relevancy}%
* Hallucination Rate (DeepEval)        : {slide_hallucination}%
>> Overall System Quality Index        : {quality_score:.1f}%

2. ALIGNMENT TO PRODUCT COHORT RETENTION
-------------------------------------------------------------------------
* Projected Customer CSAT Score        : {projected_csat:.2f} / 5.0 Stars
* Predicted Churn Risk (CSAT-impact)   : {churn_risk:.1f}%

DECISION ROADMAP:
"""
    if quality_score >= 85.0 and slide_hallucination <= 5:
        memo += f"- **Recommendation: APPROVED FOR STABLE RELEASE.** System quality matches production-grade thresholds. Hallucination index is strictly contained below 5%. Excellent faithfulness metrics assure reliable CSAT protection."
    elif quality_score < 70.0 or slide_hallucination > 15:
        memo += f"- **Recommendation: BLOCK DEPLOYMENT (REGRESSION DETECTED).** High hallucination rates ({slide_hallucination}%) pose critical branding and user churn liabilities. Prompt optimizations are required to ground output vectors."
    else:
        memo += f"- **Recommendation: CONDITIONAL ROLLOUT (MONITOR CLOSELY).** System performance is borderline acceptable. Latency and grounding indicators should be watched with an automated anomaly triage workflow."

    st.code(memo, language="markdown")

# Premium Minimalist Footer Panel
st.markdown("""
<div style="border-top: 1px solid #e2e8f0; margin-top: 48px; padding-top: 24px; padding-bottom: 24px;">
    <div style="max-w-[1600px] mx-auto flex flex-col sm:flex-row justify-between align-items: center; gap: 12px; font-size: 12px; color: #64748b;">
        <div>
            &copy; 2026 Dhaval Kareliya. All rights reserved.
        </div>
        <div style="display: flex; gap: 24px; font-weight: 600;">
            <a href="https://linkedin.com/in/YOUR_USERNAME" target="_blank" style="text-decoration: none; color: #475569; transition: color 0.2s;">LinkedIn</a>
            <a href="https://github.com/YOUR_USERNAME" target="_blank" style="text-decoration: none; color: #475569; transition: color 0.2s;">GitHub</a>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
