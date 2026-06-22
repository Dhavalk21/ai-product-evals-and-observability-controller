import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Set up page config
st.set_page_config(page_title="AI Product Observability & Evals Framework", layout="wide")

# Load pre-computed data
with open("mock_data.json", "r") as f:
    data = json.load(f)

df_logs = pd.DataFrame(data["production_logs"])

# App Header
st.title("🔬 AI Product Quality Observability & Evals Framework")
st.markdown("""
**Target Audience:** Hiring Managers, Product Directors, & AI Engineers.  
*This framework bridges the gap between engineering LLM performance (Evals) and business metrics (Product KPIs) using a simulated 'LLM-as-a-Judge' dataset.*
""")

st.divider()

# Sidebar Info
st.sidebar.header("🎯 System Overview")
st.sidebar.info("""
**Core Stack Monitored:** * **Model:** Claude 3.5 Sonnet  
* **Eval Engine:** DeepEval (Open-Source)  
* **Use Case:** B2B AI Support Assistant
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
        st.metric("Avg Groundedness (Truth)", f"{avg_grounded:.1f}%", delta="-4.2% (vs last week)", delta_color="inverse")
    with col2:
        avg_rel = df_logs["relevancy_score"].mean() * 100
        st.metric("Avg Answer Relevancy", f"{avg_rel:.1f}%")
    with col3:
        avg_lat = df_logs["latency_sec"].mean()
        st.metric("Avg User Latency", f"{avg_lat:.2f}s")
    with col4:
        escalation_rate = (df_logs["product_impact"] == "Escalated to Human Support").sum() / len(df_logs) * 100
        st.metric("Support Escalation Rate", f"{escalation_rate:.1f}%", delta="+12.0% (Spike)", delta_color="inverse")

    st.subheader("💡 The Product Management Link: Evals vs Business Outcomes")
    st.markdown("""
    > **Senior PM Insight:** Technical teams look at raw token counts. Product leaders care about business drag. 
    > Notice how dropping Groundedness immediately triggers **Support Escalations**, ruining features' unit economics.
    """)
    
    # Plotting Correlation
    fig = px.bar(df_logs, x="timestamp", y="latency_sec", color="product_impact",
                 title="System Latency vs Product Impact Event Mapping",
                 labels={"latency_sec": "Latency (Seconds)", "timestamp": "Interaction Time"})
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------
# TAB 2: PRODUCTION LOG INSPECTOR
# ----------------------------------------------------
with tab2:
    st.header("Granular Production Analysis")
    st.write("Drill down into individual AI traces to evaluate the exact failure mechanics behind poor scores.")
    
    # Simple dataframe selector
    selected_row = st.selectbox("Select a production log to audit:", df_logs.index, 
                                 format_func=lambda x: f"[{df_logs.loc[x, 'product_impact']}] - Query: {df_logs.loc[x, 'user_query'][:40]}...")
    
    log = df_logs.loc[selected_row]
    
    c1, c2 = st.columns(2)
    with c1:
        st.info(f"**User Prompt:**\n{log['user_query']}")
        st.success(f"**LLM Generated Response:**\n{log['llm_output']}")
    with c2:
        st.warning(f"**Retrieved Context provided to LLM:**\n{log['retrieval_context']}")
        
    st.markdown("### 👁️ DeepEval Judge Verdict")
    st.json({
        "Groundedness Score": log["groundedness_score"],
        "Relevancy Score": log["relevancy_score"],
        "Judge Reasoning": log["groundedness_reason"]
    })

# ----------------------------------------------------
# TAB 3: INTERACTIVE EVAL SANDBOX
# ----------------------------------------------------
with tab3:
    st.header("🧪 Automated Eval Sandbox Simulator")
    st.markdown("Select an industry scenario below to see how an automated **LLM-as-a-Judge** framework catches product regression instantly without human review.")
    
    scenario_choice = st.selectbox("Choose a scenario context:", list(data["sandbox_scenarios"].keys()))
    scenario = data["sandbox_scenarios"][scenario_choice]
    
    # Layout the editable fields
    ctx_input = st.text_area("1. Context (Knowledge Base Base/Data source)", scenario["context"], height=80)
    query_input = st.text_area("2. User Query", scenario["query"], height=70)
    output_input = st.text_area("3. System Live AI Response", scenario["output"], height=70)
    
    if st.button("🚀 Execute Automated Evaluation Pipeline", type="primary"):
        st.divider()
        st.subheader("📊 Evaluation Framework Evaluation Results")
        
        # Display scores cleanly
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            if scenario["groundedness_score"] >= 0.7:
                st.success(f"🟢 Groundedness Score: {scenario['groundedness_score']}")
            else:
                st.error(f"🔴 Groundedness Score: {scenario['groundedness_score']} (Hallucination Detected!)")
        with s_col2:
            st.info(f"🔵 Relevancy Score: {scenario['relevancy_score']}")
            
        st.markdown(f"**Chain-of-Thought Judge Explanation:**\n> _{scenario['groundedness_reason']}_")
