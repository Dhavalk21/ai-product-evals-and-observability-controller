import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Set up page config
st.set_page_config(page_title="AI Product Quality Observability Framework", layout="wide")

# Load pre-computed data
with open("mock_data.json", "r") as f:
    data = json.load(f)

df_logs = pd.DataFrame(data["production_logs"])

# App Header
st.title("🔬 AI Product Quality Observability & Evals Framework")
st.markdown("""
Welcome to the interactive Product Operations portal. Use this framework to understand how engineering-level AI performance directly shifts business metrics.
""")

st.divider()

# Sidebar Interactive Guidance Controls
st.sidebar.header("🕹️ Simulation Controls")
st.sidebar.markdown("### Step 1: Set Quality Alert Gates")
groundedness_threshold = st.sidebar.slider("Minimum Groundedness Target (%)", 50, 100, 75, step=5) / 100.0
latency_threshold = st.sidebar.slider("Max Acceptable Latency (Seconds)", 1.0, 6.0, 3.0, step=0.5)

st.sidebar.divider()
st.sidebar.markdown("### 💡 Active PM Playbook")
pm_strategy = st.sidebar.selectbox(
    "Select a Guide Scenario:",
    ["1. Auditing a Hallucination Spike", "2. Optimizing API Unit Economics", "3. Guardrail Compliance Checklist"]
)

# Render explicit walkthrough guidance text based on PM strategy choice
st.info(f"**Current Walkthrough Guide: {pm_strategy}**")
if pm_strategy == "1. Auditing a Hallucination Spike":
    st.markdown("""
    👉 **How to use this view:** Look at the chart below. Notice the **Escalated to Human Support** events. 
    Go to **Tab 2 (Production Log Inspector)** to find the exact interaction where Groundedness hit 0.0 to diagnose why the system hallucinated.
    """)
elif pm_strategy == "2. Optimizing API Unit Economics":
    st.markdown("""
    👉 **How to use this view:** Adjust the **Max Acceptable Latency** slider on the left. 
    See how user drop-offs correlate with slower processing speeds. Use this data to negotiate SLA agreements with engineering.
    """)
else:
    st.markdown("""
    👉 **How to use this view:** Head directly over to **Tab 3 (Interactive Eval Sandbox)**. 
    Test how automated rules stop data breaches and protect customer data automatically before a customer sees it.
    """)

# Setup Tabs
tab1, tab2, tab3 = st.tabs(["📊 Executive ROI Dashboard", "🔍 Production Log Inspector", "🧪 Interactive Eval Sandbox"])

# ----------------------------------------------------
# TAB 1: EXECUTIVE ROI DASHBOARD
# ----------------------------------------------------
with tab1:
    st.header("Strategic Product Health")
    
    # High level KPI cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_grounded = df_logs["groundedness_score"].mean() * 100
        st.metric("Avg Groundedness (Truth)", f"{avg_grounded:.1f}%")
    with col2:
        avg_rel = df_logs["relevancy_score"].mean() * 100
        st.metric("Avg Answer Relevancy", f"{avg_rel:.1f}%")
    with col3:
        avg_lat = df_logs["latency_sec"].mean()
        st.metric("Avg User Latency", f"{avg_lat:.2f}s")
    with col4:
        escalation_rate = (df_logs["product_impact"] == "Escalated to Human Support").sum() / len(df_logs) * 100
        st.metric("Support Escalation Rate", f"{escalation_rate:.1f}%")

    st.subheader("📊 Operational Analytics Tracking")
    
    # Dynamic Alert Banner based on Sidebar selections
    flagged_logs = df_logs[(df_logs["groundedness_score"] < groundedness_threshold) | (df_logs["latency_sec"] > latency_threshold)]
    if not flagged_logs.empty:
        st.error(f"⚠️ **Product Ops Alert:** {len(flagged_logs)} production interactions have breached your custom quality alert thresholds!")
    else:
        st.success("✅ All system metrics are tracking cleanly within your product safety thresholds.")

    # Plotting Correlation
    fig = px.bar(df_logs, x="timestamp", y="latency_sec", color="product_impact",
                 title="System Latency vs Product Impact Event Mapping",
                 labels={"latency_sec": "Latency (Seconds)", "timestamp": "Interaction Time"})
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TAB 2: PRODUCTION LOG INSPECTOR
# ----------------------------------------------------
with tab2:
    st.header("Granular Production Trace Auditor")
    st.markdown("Use this tab to audit exact user interactions that triggered system alerts.")
    
    # Filter dropdown based on user selections
    selected_row = st.selectbox("Select a production log to audit:", df_logs.index, 
                                 format_func=lambda x: f"[{df_logs.loc[x, 'product_impact']}] - Query: {df_logs.loc[x, 'user_query'][:40]}...")
    
    log = df_logs.loc[selected_row]
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**User Prompt:**\n\n{log['user_query']}")
        st.success(f"**LLM Generated Response:**\n\n{log['llm_output']}")
    with c2:
        st.warning(f"**Retrieved Context provided to LLM:**\n\n{log['retrieval_context']}")
        
    st.markdown("### 👁️ DeepEval Judge Verdict")
    
    # Highlight failures clearly
    if log["groundedness_score"] < groundedness_threshold:
        st.error(f"❌ Groundedness Score ({log['groundedness_score']}) dropped below your configured safety gate ({groundedness_threshold})!")
    
    st.json({
        "Groundedness Score": log["groundedness_score"],
        "Relevancy Score": log["relevancy_score"],
        "Judge Reasoning": log["groundedness_reason"]
    })

# ----------------------------------------------------
# TAB 3: INTERACTIVE EVAL SANDBOX
# ----------------------------------------------------
with tab3:
    st.header("🧪 Interactive Eval Sandbox Simulator")
    st.markdown("Simulate an automated quality loop. Edit the text boxes below to see how changes to the AI's response alter the evaluation scores instantly.")
    
    scenario_choice = st.radio("Choose a base scenario archetype to load:", list(data["sandbox_scenarios"].keys()))
    scenario = data["sandbox_scenarios"][scenario_choice]
    
    # Layout the editable fields
    ctx_input = st.text_area("Step 1: Context (Knowledge Base reference rules)", scenario["context"], height=90)
    query_input = st.text_area("Step 2: Enter the User Query", scenario["query"], height=70)
    output_input = st.text_area("Step 3: Modify the AI Generated Output (Try adding a lie or changing the answer!)", scenario["output"], height=70)
    
    if st.button("🚀 Run Live Evaluation Mock Pipeline", type="primary"):
        st.divider()
        st.subheader("🎯 Automated Evaluation Pipeline Results")
        
        # Check if the user modified the text
        is_modified = (output_input.strip() != scenario["output"].strip())
        
        # DYNAMIC HEURISTICS CLASSIFIER (Simulating the Judge locally)
        # Catch common words users type when testing a failure
        fail_keywords = ["yes", "refund", "free", "money back", "can return", "hallucination", "fake", "wrong"]
        contains_fail_move = any(word in output_input.lower() for word in fail_keywords) if is_modified else False

        # Determine dynamic scores
        if not is_modified:
            calculated_groundedness = scenario["groundedness_score"]
            reasoning = scenario["groundedness_reason"]
        elif scenario_choice == "Scenario A: High Quality Run" and contains_fail_move:
            # User edited the good response to make it incorrectly say "Yes"
            calculated_groundedness = 0.0
            reasoning = "⚠️ **Dynamic Rule Catch:** The user modified the output to promise a refund, which directly violates the non-refundable digital download context rule!"
        elif scenario_choice == "Scenario B: Severe Hallucination" and ("no" in output_input.lower() or "cannot" in output_input.lower()):
            # User fixed the bad response to make it correct
            calculated_groundedness = 1.0
            reasoning = "✅ **Dynamic Rule Catch:** Excellent! You corrected the hallucination. The response now accurately reflects the system constraints."
        else:
            # General modification fallback
            calculated_groundedness = 0.5
            reasoning = "ℹ️ **Dynamic Rule Catch:** Output text modification detected. The mock engine adjusted the Groundedness index to a neutral baseline score."

        # Display UI elements dynamically
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            if calculated_groundedness >= groundedness_threshold:
                st.success(f"🟢 Groundedness Score: {calculated_groundedness}")
            else:
                st.error(f"🔴 Groundedness Score: {calculated_groundedness} (Hallucination Tracked)")
        with s_col2:
            st.info(f"🔵 Relevancy Score: {scenario['relevancy_score']}")
            
        st.markdown(f"**Automated Evaluation Logic Analysis:**\n\n{reasoning}")
