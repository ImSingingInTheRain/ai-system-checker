import json
import datetime as dt
import streamlit as st

st.set_page_config(page_title="AI System Classifier (EU AI Act-aligned)", page_icon="🤖", layout="centered")

# -------- Helpers
def decision_badge(label, verdict):
    if verdict == "AI system":
        st.success(f"✅ {label}: **{verdict}**")
    elif verdict == "Likely not an AI system":
        st.info(f"ℹ️ {label}: **{verdict}**")
    else:
        st.warning(f"⚠️ {label}: **{verdict}**")


def section_header(title, help_text=None):
    st.markdown(f"### {title}")
    if help_text:
        with st.expander("What this means"):
            st.write(help_text)


def export_json(assessment):
    payload = {
        "app": "AI System Classifier (EU AI Act-aligned)",
        "version": "1.0.0",
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "assessment": assessment,
    }
    st.download_button(
        "⬇️ Download assessment (JSON)",
        data=json.dumps(payload, indent=2),
        file_name="ai_system_classification.json",
        mime="application/json",
        use_container_width=True,
    )


# -------- App header
st.title("What is an AI system? — Interactive Classifier")
with st.expander("EU AI Act definition (for reference)"):
    st.write(
        "‘AI system’ means a machine-based system that is designed to operate with varying levels of autonomy "
        "and that may exhibit adaptiveness after deployment, and that, for explicit or implicit objectives, "
        "infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, "
        "or decisions that can influence physical or virtual environments."
    )

# -------- Wizard state
if "answers" not in st.session_state:
    st.session_state.answers = {}

answers = st.session_state.answers

# -------- Step 1 — Negative scope check (non‑AI categories)
section_header(
    "Step 1 — Does your solution fall into any of these categories?",
)

col1, col2 = st.columns(2)
with col1:
    c_none = st.checkbox("None applies", help="Select if none of the categories below are relevant.")
    c_basic = st.checkbox(
        "Basic data processing tools",
        help="Operate on predefined human instructions; repetitive or rule-based; exactly as programmed.",
    )
    c_heur = st.checkbox(
        "Classical heuristic‑based systems",
        help="Solve problems without learning; rely on human-programmed rules/strategies only.",
    )
    c_simple_pred = st.checkbox(
        "Simple prediction systems",
        help="Basic statistics (e.g., averages, fixed formulas) without learned models.",
    )

answers["non_ai_categories"] = {
    "none_applies": c_none,
    "basic_data_processing_tools": c_basic,
    "classical_heuristic_based": c_heur,
    "simple_prediction_systems": c_simple_pred,
}

non_ai_selected = any([c_basic, c_heur, c_simple_pred])


# Early exit option
if non_ai_selected:
    decision_badge("Result", "Likely not an AI system")
    st.markdown(
        "- You indicated at least one NON‑AI category from your guidance.\n"
        "- These solutions follow predefined human rules and do not infer outputs using AI models."
    )
    export_json({"result": "Likely not an AI system", "reason": "Selected NON-AI category", "answers": answers})
    st.stop()

if not c_none:
    st.info("Select an option to continue the assessment.")
    st.stop()

st.divider()

# -------- Step 2 — AI model development using AI techniques
section_header(
    "Step 2 — Was any component of your solution developed using **AI Techniques**?",
    "This step allows you to confirm if your system uses AI Models, by checking if any of its components was developed using machine learning or logic-and knowledge based techniques.",
)

tech_ml_selected = st.checkbox("Machine Learning techniques")
selected_ml = []
if tech_ml_selected:
    selected_ml = st.multiselect(
        "Select the machine learning techniques used",
        options=[
            "Supervised Learning",
            "Unsupervised Learning",
            "Self‑Supervised Learning",
            "Reinforcement Learning",
            "Deep Learning",
        ],
    )

tech_logic = st.checkbox("Logic‑ and Knowledge‑Based Techniques")
none_selected = st.checkbox("None of these techniques is used")

if none_selected and (tech_ml_selected or tech_logic or selected_ml):
    st.warning("Remove other selections if you choose 'None of these techniques is used'.")

if tech_ml_selected and not selected_ml and not none_selected:
    st.info("Select at least one machine learning technique or uncheck the option to continue.")
    st.stop()

answers["ai_techniques"] = {
    "ml_selected": tech_ml_selected,
    "ml_techniques": selected_ml,
    "logic_knowledge_based": tech_logic,
    "none_selected": none_selected,
}

uses_ai_techniques = (len(selected_ml) > 0) or tech_logic

if none_selected:
    decision_badge("Result", "Likely not an AI system")
    st.markdown(
        "- You selected **None of these techniques is used**.\n"
        "- Without components developed using AI techniques, the solution is generally **not** an AI system."
    )
    if selected_ml or tech_logic:
        st.markdown(
            "- Remove any other technique selections to avoid conflicting inputs."
        )
    export_json({"result": "Likely not an AI system", "reason": "Explicitly selected no AI techniques", "answers": answers})
    st.stop()

if not uses_ai_techniques:
    # If no AI techniques are used, then not an AI system (per slide flow)
    decision_badge("Result", "Likely not an AI system")
    st.markdown(
        "- You did **not** select any AI techniques.\n"
        "- Without components developed using AI techniques, the solution is generally **not** an AI system."
    )
    export_json({"result": "Likely not an AI system", "reason": "No AI techniques selected", "answers": answers})
    st.stop()

st.divider()

# -------- Step 3 — Optimization-only carve-out
section_header(
    "Step 3 — Are AI models used **only for mathematical optimization / speed‑up**?",
    "Mathematical optimization refers to the process of finding the best solution from a set of possible options by maximizing or minimizing a specific objective function, typically under defined constraints.",
)

opt_only = st.radio("Optimization-only usage?", options=["Yes", "No"], index=1, horizontal=True)
answers["optimization_only"] = opt_only == "Yes"

conditions = {}
if opt_only == "Yes":
    st.markdown("Select **all** that apply:")
    conditions["supporting_role_only"] = st.checkbox(
        "The model plays a supporting role only",
        help="Trained and used to support one narrowly defined engineering/operational domain. No new reasoning capabilities introduced.",
    )
    conditions["fixed_after_deployment"] = st.checkbox(
        "The model is fixed after deployment",
        help="No retraining, self‑adaptation, or dynamic updates during operation.",
    )
    conditions["no_influence_objectives"] = st.checkbox(
        "The model does not influence or redefine the system’s objectives",
        help="Goals/decision criteria remain fully human‑defined and rule‑based.",
    )
    conditions["outputs_narrowly_scoped"] = st.checkbox(
        "The outputs are narrowly scoped",
        help="No direct triggering of actions in physical/virtual environments; outputs feed deterministic optimisation routines.",
    )
    conditions["performance_is_efficiency"] = st.checkbox(
        "Performance metric is computational efficiency",
        help="Measured by speed, memory, numerical stability—not prediction accuracy/recommendation/decision quality.",
    )

answers["optimization_conditions"] = conditions

all_conditions_true = all(conditions.values()) if opt_only == "Yes" else False

st.divider()

# -------- Optional confirmation: inference & autonomy (informational)
with st.expander("Optional confirmation: inference & autonomy (informational)"):
    infers_outputs = st.checkbox(
        "The solution infers how to generate outputs from inputs (predictions/content/recommendations/decisions).",
        value=False,
    )
    varying_autonomy = st.checkbox(
        "The solution operates with varying levels of autonomy (may require human in the loop).",
        value=False,
    )
    answers["inference_autonomy"] = {
        "infers_outputs": infers_outputs,
        "varying_autonomy": varying_autonomy,
    }

# -------- Final decision logic
rationale = []
if opt_only == "Yes" and all_conditions_true:
    verdict = "Likely not an AI system"
    rationale.append("Optimization‑only usage and **all** optimization carve‑out conditions satisfied.")
elif opt_only == "Yes" and not all_conditions_true:
    verdict = "AI system"
    rationale.append("Optimization‑only usage **but** not all carve‑out conditions satisfied.")
else:
    verdict = "AI system"
    rationale.append("Uses AI techniques and not limited to optimization‑only carve‑out.")

# Enrich rationale with optional info
if answers["inference_autonomy"]["infers_outputs"]:
    rationale.append("Confirms inference from inputs to outputs.")
if answers["inference_autonomy"]["varying_autonomy"]:
    rationale.append("Operates with varying levels of autonomy (may still be human‑in-the-loop).")

# -------- Display result
decision_badge("Result", verdict)
st.markdown("**Rationale**")
for r in rationale:
    st.markdown(f"- {r}")

# -------- Export
assessment = {"result": verdict, "rationale": rationale, "answers": answers}
export_json(assessment)

st.caption(
    "This tool reflects the decision structure in your illustration. For borderline cases, escalate for expert review and document assumptions."
)
