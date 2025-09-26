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
st.caption("This interactive checklist follows the structure of your slide and aligns with the EU AI Act definition and decision logic.")

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
    "Step 1 — Does your solution fall into any NON‑AI categories?",
    "If any of these are selected, the solution is generally **not** an AI system per your guidance.",
)

col1, col2 = st.columns(2)
with col1:
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
with col2:
    st.markdown("> If you select any of the above, you are **not providing an AI system**.")

answers["non_ai_categories"] = {
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

st.divider()

# -------- Step 2 — AI model development using AI techniques
section_header(
    "Step 2 — Was any component developed using **AI Techniques**?",
    "Select any techniques used to develop the model components within your solution.",
)

none_option = "None of these techniques is used"
tech_ml = st.multiselect(
    "Machine Learning techniques",
    options=[
        "Supervised Learning",
        "Unsupervised Learning",
        "Self‑Supervised Learning",
        "Reinforcement Learning",
        "Deep Learning",
        none_option,
    ],
)

none_selected = none_option in tech_ml
selected_ml = [tech for tech in tech_ml if tech != none_option]

if none_selected and selected_ml:
    st.warning("Remove other selections if you choose 'None of these techniques is used'.")

tech_logic = st.checkbox("Logic‑ and Knowledge‑Based Techniques")

answers["ai_techniques"] = {
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
    "If yes, all the conditions below must hold to consider it likely **not** an AI system.",
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
