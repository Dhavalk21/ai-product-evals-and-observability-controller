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

# Custom CSS to style elements and highlight the active scenario button
st.markdown("""
<style>
  /* Styling custom buttons and tooltips */
  .stButton > button {
    transition: all 0.2s ease-in-out;
  }
  .active-btn {
    background-color: #4f46e5 !important;
    color: white !important;
    border-color: #4338ca !important;
  }
</style>
""", unsafe_allow_html=True)

# Initialize Session States for Playground Presets
if 'play_context' not in st.session_state:
    st.session_state.play_context = "we have 2 plan: 1) gold client 20 euro and 14 day refund policy. 2) silver plan 10 euro and no refund policy"
if 'play_query' not in st.session_state:
    st.session_state.play_query = "What is the cost of the silver plan, and what is your refund policy?"
if 'play_output' not in st.session_state:
    st.session_state.play_output = "Silver plan cost 10 euro and 10 day return policy"
if 'active_preset' not in st.session_state:
    st.session_state.active_preset = "hallucinated"

# Default Baseline Sliders
if 'faithfulness' not in st.session_state:
    st.session_state.faithfulness = 80
if 'relevancy' not in st.session_state:
    st.session_state.relevancy = 85
if 'hallucination' not in st.session_state:
    st.session_state.hallucination = 12

# Header Branding & Badges
st.markdown("""
<div style="background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 24px;">
    <div style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px;">
        <span style="background-color: #f1f5f9; color: #475569; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 9999px; border: 1px solid #cbd5e1;">
            AI Product Operations • Quality Assurance Framework
        </span>
        <span style="background-color: #e0e7ff; color: #4338ca; font-size: 11px; font-weight: 600; padding: 4px 12px; border-radius: 9999px; border: 1px solid #c7d2fe;">
            Designed by Dhaval Kareliya | 
            <a href="https://linkedin.com/in/YOUR_USERNAME" target="_blank" style="text-decoration: none; color: #3730a3; font-weight: bold;">LinkedIn</a> • 
            <a href="https://github.com/YOUR_USERNAME" target="_blank" style="text-decoration: none; color: #3730a3; font-weight: bold;">GitHub</a>
        </span>
    </div>
    <h1 style="color: #0f172a; font-size: 26px; font-weight: 800; margin: 0 0 4px 0; tracking: -0.025em;">
        Production AI Evals &amp; Observability Controller
    </h1>
    <p style="color: #64748b; font-size: 14px; margin: 0; line-height: 1.5;">
        Verify and monitor LLM system performance. Define multi-dimensional criteria (Faithfulness, Relevancy, Hallucinations) to dynamically predict customer churn, CSAT, and system reliability.
    </p>
</div>
""", unsafe_allow_html=True)

# Collapsible Guide (Replaced with Custom "How to Run LLM Quality Evaluations" block)
with st.expander("📖 Show Guide: How to Run LLM Quality Evaluations (With Examples)", expanded=True):
    st.markdown("""
    Product managers run these evaluations (Evals) using golden datasets to avoid deploying a model that outputs false facts or fails user queries.
    
    #### 📋 Step-by-Step Instructions:
    1. Click on any of the scenario buttons inside the **Live Evaluation Playground** panel (e.g. *⚠️ Hallucinated Fact*).
    2. Inspect the source context (what the database knows) and compare it with the LLM response.
    3. Click the blue **"Run AI-Judge Evaluation Simulation"** button. The simulated judge reads, checks, and scores the inputs.
    4. Look at the top KPI cards—the evaluation results instantly update your **Predicted Churn Risk** and **Expected CSAT**!
    """)
    
    g_col1, g_col2, g_col3 = st.columns(3)
    with g_col1:
        st.info("**Scenario A: Hallucinated Fact**\nThe model promised a '10-day return policy' when the source context states 'no refund policy'.\n\n*Expected: Faithfulness ~60%, Hallucinations ~45%*")
    with g_col2:
        st.warning("**Scenario B: Off-Topic Answer**\nThe model ignored the pricing question and began advertising shoe deals instead.\n\n*Expected: Relevancy ~30%, CSAT decreases severely.*")
    with g_col3:
        st.success("**Scenario C: Perfect Grounding**\nThe model correctly extracted details and complied strictly with the strict refund policy context.\n\n*Expected: Quality >90%, Churn Risk minimized.*")

# Main Content Columns (Layout proportion: 38.3% Left, 61.7% Right)
col_left, col_right = st.columns([38, 62])

with col_left:
    st.subheader("Live Evaluation Playground")
    
    # Presets Selection buttons
    st.markdown("<p style='font-size:12px; font-weight:600; color:#475569;'>Choose a Scenario:</p>", unsafe_allow_html=True)
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

    # Active dynamic coloring for button presets
    with p_col1:
        if st.button("⚠️ Hallucinated Fact", type="primary" if st.session_state.active_preset == "hallucinated" else "secondary", use_container_width=True):
            load_preset("hallucinated")
    with p_col2:
        if st.button("❌ Off-Topic Answer", type="primary" if st.session_state.active_preset == "offtopic" else "secondary", use_container_width=True):
            load_preset("offtopic")
    with p_col3:
        if st.button("✅ Perfect Compliance", type="primary" if st.session_state.active_preset == "grounded" else "secondary", use_container_width=True):
            load_preset("grounded")

    # Playground Inputs
    text_context = st.text_area("Grounded Source Context", value=st.session_state.play_context, height=90)
    text_query = st.text_input("User Question", value=st.session_state.play_query)
    text_output = st.text_area("Generated Output Response", value=st.session_state.play_output, height=90)

    # Simulation Evaluation Trigger (The Blue Button)
    if st.button("Run AI-Judge Evaluation Simulation", type="primary", use_container_width=True):
        c = text_context.lower().strip()
        q = text_query.lower().strip()
        o = text_output.lower().strip()
        
        evaluated_faithfulness = 100
        evaluated_relevancy = 100
        evaluated_hallucination = 0
        
        # Standardized search keywords list
        policy_keywords = ['day', 'days', 'week', 'weeks', 'month', 'months', 'year', 'years', 'return', 'refund', 'policy', 'guarantee']
        
        # Heuristics A: Numerical validation & structural mismatch
        output_numbers = re.findall(r'\b\d+\b', o)
        for num in output_numbers:
            output_idx = o.find(num)
            if output_idx != -1:
                snippet = o[max(0, output_idx - 25): min(len(o), output_idx + 25)]
                is_output_temporal = any(w in snippet for w in policy_keywords)
                
                context_idx = c.find(num)
                if context_idx != -1:
                    c_snippet = c[max(0, context_idx - 25): min(len(c), context_idx + 25)]
                    is_context_temporal = any(w in c_snippet for w in policy_keywords)
                    
                    if is_output_temporal and not is_context_temporal:
                        evaluated_faithfulness -= 40
                        evaluated_hallucination += 45
                else:
                    evaluated_faithfulness -= 30
                    evaluated_hallucination += 30

        # Heuristics B: Strict Policy Contradiction mapping
        if "no refund" in c or "no return" in c:
            has_refund_claim = any(word in o for word in policy_keywords) and not any(w in o for w in ['no refund', 'no return'])
            if has_refund_claim:
                evaluated_faithfulness -= 45
                evaluated_hallucination += 40

        # Heuristics C: Relevancy validation
        clean_q = re.sub(r'[^\w\s]', '', q)
        clean_o = re.sub(r'[^\w\s]', '', o)
        query_words = [w for w in clean_q.split() if len(w) > 3]
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

    # Section 1: Sliders Calibration
    st.subheader("1. System Metric Calibration")
    
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

    st.subheader("2. KPI Weight Configuration")
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
f_factor = (weight_faith / total_weight) if total_weight > 0 else 0
r_factor = (weight_rel / total_weight) if total_weight > 0 else 0
h_factor = (weight_hall / total_weight) if total_weight > 0 else 0

quality_score = (slide_faithfulness * f_factor) + (slide_relevancy * r_factor) + ((100 - slide_hallucination) * h_factor)

churn_risk = (100 - quality_score) * 1.5
if slide_hallucination > 15:
    churn_risk += (slide_hallucination - 15) * 2.2
churn_risk = min(99.5, max(1.5, churn_risk))

projected_csat = 1.0 + (quality_score / 100.0) * 4.0

# Right Analytics Workspace Panel
with col_right:
    # 3 High-Impact KPI Cards
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="Overall Quality Index",
            value=f"{quality_score:.1f}%",
            delta="Acceptable" if quality_score >= 80 else "Unsafe",
            delta_color="normal" if quality_score >= 80 else "inverse"
        )
    with kpi_col2:
        st.metric(
            label="Predicted Churn Risk",
            value=f"{churn_risk:.1f}%",
            delta="Low Risk" if churn_risk <= 15 else "High Churn Alert",
            delta_color="inverse" if churn_risk > 15 else "normal"
        )
    with kpi_col3:
        st.metric(
            label="Projected Customer CSAT",
            value=f"{projected_csat:.2f} / 5.0",
            delta="Target Met" if projected_csat >= 4.0 else "Below SLA",
            delta_color="normal" if projected_csat >= 4.0 else "inverse"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Timeline Chart
    st.subheader("Quality Baseline Timeline")
    baseline_runs = [55.0, 58.5, 62.0, 71.5, 76.0]
    runs = baseline_runs + [quality_score]
    x_runs = ["Run 1", "Run 2", "Run 3", "Run 4", "Run 5", "Active"]

    fig = go.Figure()
    # Safe Target Line
    fig.add_trace(go.Scatter(
        x=x_runs, y=[80]*6,
        mode="lines",
        name="Target Threshold (80%)",
        line=dict(color="red", dash="dash", width=1.5)
    ))
    # Active timeline curve
    fig.add_trace(go.Scatter(
        x=x_runs, y=runs,
        mode="lines+markers",
        name="Evaluated Score",
        line=dict(color="#4f46e5", width=3),
        marker=dict(size=8, color="#10b981" if quality_score >= 80 else "#ef4444")
    ))
    fig.update_layout(
        yaxis_range=[0, 100],
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        paper_bgcolor="#f8fafc",
        plot_bgcolor="#f8fafc",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Industry Standards Info Cards
    st.markdown("""
    <div style="background-color: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-bottom: 24px;">
        <span style="font-size: 11px; font-weight: bold; background-color: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
            Ragas &amp; DeepEval Framework Compliance
        </span>
        <div style="display: grid; grid-template-columns: 1fr; gap: 12px; margin-top: 12px;">
          <div>
            <p style="text-size: 13px; font-weight: 700; color: #1e293b; margin: 0;">Ragas Framework: Faithfulness</p>
            <p style="font-size: 11px; color: #64748b; margin: 4px 0 0 0; line-height: 1.4;">
                Utilized to ensure information is strictly grounded. Ragas extracts key factual statements from the generated answer and queries an LLM Judge to check if each statement is explicitly backed by the retrieved context papers.
            </p>
          </div>
          <div>
            <p style="text-size: 13px; font-weight: 700; color: #1e293b; margin: 0;">DeepEval: Relevancy &amp; Hallucinations</p>
            <p style="font-size: 11px; color: #64748b; margin: 4px 0 0 0; line-height: 1.4;">
                Maintains output quality. DeepEval maps the cosine similarity between generated responses and initial prompt intents to compute answer relevancy, and cross-references source contradictions to output a strict hallucination percentage.
            </p>
          </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Automated release briefing memo
    st.subheader("System Quality Release Briefing")
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
