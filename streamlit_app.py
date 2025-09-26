import json
import datetime as dt
import streamlit as st

st.set_page_config(page_title="AI System Classifier (EU AI Act-aligned)", page_icon="🤖", layout="centered")


def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --primary-bg: #f5f7fb;
            --primary-text: #1f2933;
            --accent: #2563eb;
            --muted-text: #4b5563;
            --card-bg: #ffffff;
            --divider: #e5e7eb;
        }

        .stApp {
            background-color: var(--primary-bg);
            color: var(--primary-text);
            font-family: 'Inter', sans-serif;
        }

        section.main > div {
            padding: 1.5rem 2.5rem 4rem;
            background: linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(245,247,251,0.9) 100%);
            border-radius: 24px;
            box-shadow: 0 20px 45px rgba(15, 23, 42, 0.05);
            border: 1px solid rgba(226, 232, 240, 0.9);
        }

        h1, h2, h3 {
            font-weight: 700 !important;
            letter-spacing: -0.01em;
            color: var(--primary-text);
        }

        .stMarkdown p, .stMarkdown li {
            font-size: 1rem;
            line-height: 1.6;
            color: var(--muted-text);
        }

        .st-expander {
            border: 1px solid rgba(37, 99, 235, 0.15) !important;
            border-radius: 16px !important;
            background: rgba(37, 99, 235, 0.05) !important;
        }

        .stExpanderHeader {
            font-weight: 600;
            color: var(--accent);
        }

        .stRadio > div, .stCheckbox > label {
            font-size: 0.98rem;
            font-weight: 500;
        }

        .stCheckbox:hover, .stRadio:hover {
            background: rgba(37, 99, 235, 0.04);
            border-radius: 12px;
            transition: background 0.2s ease;
        }

        .stDownloadButton button {
            background: var(--accent);
            color: #fff;
            font-weight: 600;
            border-radius: 999px;
            padding: 0.75rem 1.5rem;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.25);
        }

        .stDownloadButton button:hover {
            background: #1d4ed8;
        }

        .stSuccess, .stInfo, .stWarning {
            border-radius: 16px;
            border: none;
            box-shadow: 0 12px 25px rgba(15, 23, 42, 0.08);
        }

        .stDivider, hr {
            border: none;
            height: 1px;
            background: var(--divider);
            margin: 2.5rem 0;
        }

        .small-muted {
            color: var(--muted-text);
            font-size: 0.9rem;
        }

        .summary-hint {
            margin-top: 1rem;
            padding: 0.85rem 1rem;
            border-radius: 14px;
            background: rgba(37, 99, 235, 0.08);
            border: 1px solid rgba(37, 99, 235, 0.18);
            color: var(--primary-text);
            font-weight: 500;
        }

        .stDownloadButton, .stButton button {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .stDownloadButton button:active, .stButton button:active {
            transform: translateY(1px);
            box-shadow: 0 6px 10px rgba(37, 99, 235, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()

st.session_state.setdefault("decision_log_entries", [])
st.session_state["decision_log_entries"].clear()
decision_log = st.session_state["decision_log_entries"]

# -------- Helpers
def record_decision(step, outcome, notes=None):
    entry = {
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "step": step,
        "outcome": outcome,
        "notes": notes or [],
    }
    decision_log.append(entry)
    return entry


def render_decision_log():
    if not decision_log:
        return

    st.markdown("### Decision log")
    for entry in decision_log:
        notes_markup = "".join(
            f"<li style='margin-left: 1.25rem; color: var(--muted-text); line-height: 1.5;'>{note}</li>"
            for note in entry["notes"]
        ) or "<li style='margin-left: 1.25rem; color: var(--muted-text); line-height: 1.5;'>No additional notes recorded.</li>"

        st.markdown(
            """
            <div style="margin-bottom: 1rem;">
                <p style="font-weight: 600; margin-bottom: 0.25rem;">{step} — {outcome}</p>
                <ul style="margin: 0.25rem 0 0; padding-left: 1rem;">{notes}</ul>
                <p class="small-muted" style="margin-top: 0.35rem;">Recorded at {timestamp}</p>
            </div>
            """.format(
                step=entry["step"],
                outcome=entry["outcome"],
                notes=notes_markup,
                timestamp=entry["timestamp"],
            ),
            unsafe_allow_html=True,
        )


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


def export_assessment(assessment):
    payload = {
        "app": "AI System Classifier (EU AI Act-aligned)",
        "version": "1.0.0",
        "timestamp": dt.datetime.utcnow().isoformat() + "Z",
        "assessment": assessment,
    }
    markdown_lines = [
        "# AI System Classification Summary",
        "",
        f"**Result:** {assessment['result']}",
        "",
        "## Rationale",
    ]
    markdown_lines.extend(f"- {item}" for item in assessment.get("rationale", []))
    markdown_lines.append("")
    markdown_lines.append("## Decision log")
    for entry in assessment.get("decision_log", []):
        markdown_lines.append(f"### {entry['step']}")
        markdown_lines.append(f"- **Outcome:** {entry['outcome']}")
        markdown_lines.append(f"- **Recorded at:** {entry['timestamp']}")
        notes = entry.get("notes") or ["No additional notes recorded."]
        markdown_lines.append("- **Notes:**")
        markdown_lines.extend(f"  - {note}" for note in notes)
        markdown_lines.append("")

    markdown_payload = "\n".join(markdown_lines)

    with st.container():
        col_json, col_md = st.columns(2)
        with col_json:
            st.download_button(
                "⬇️ Download assessment (JSON)",
                data=json.dumps(payload, indent=2),
                file_name="ai_system_classification.json",
                mime="application/json",
                use_container_width=True,
                key="download-json",
            )
        with col_md:
            st.download_button(
                "📝 Download decision log (Markdown)",
                data=markdown_payload,
                file_name="ai_system_decision_log.md",
                mime="text/markdown",
                use_container_width=True,
                key="download-markdown",
            )


# -------- App header
st.markdown(
    """
    <div style="padding: 1.5rem 1rem 1rem;">
        <p style="text-transform: uppercase; letter-spacing: 0.18em; color: #2563eb; font-weight: 600; margin-bottom: 0.25rem;">
            EU AI Act Readiness
        </p>
        <h1 style="margin-bottom: 0.75rem;">Is your solution an AI system?</h1>
        <p class="small-muted" style="max-width: 640px;">
            Work through a guided checklist aligned with the EU AI Act definition to understand whether your
            product is considered an AI system. Each step clarifies the rationale behind the classification and is captured for export.
        </p>
        <div class="summary-hint">
            Every decision you confirm will appear in the log below and can be downloaded as JSON or Markdown for your compliance records.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
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

non_ai_labels = {
    "basic_data_processing_tools": "Basic data processing tools",
    "classical_heuristic_based": "Classical heuristic-based systems",
    "simple_prediction_systems": "Simple prediction systems",
}

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

st.markdown("---")
step1_unable_to_verify = st.checkbox("I am not able to verify this", key="step1_unable_to_verify")

answers["non_ai_categories"] = {
    "none_applies": c_none,
    "basic_data_processing_tools": c_basic,
    "classical_heuristic_based": c_heur,
    "simple_prediction_systems": c_simple_pred,
    "unable_to_verify": step1_unable_to_verify,
}

non_ai_selected = any([c_basic, c_heur, c_simple_pred])
selected_non_ai_labels = [
    label
    for key, label in non_ai_labels.items()
    if answers["non_ai_categories"].get(key)
]


# Early exit option
if step1_unable_to_verify:
    notes = ["Unable to verify whether the solution fits a non-AI exclusion."]
    if selected_non_ai_labels:
        notes.append("Selections captured for transparency: " + ", ".join(selected_non_ai_labels))
    record_decision("Step 1 — Negative scope check", "Unable to verify", notes)
else:
    if non_ai_selected:
        notes = ["Selected NON-AI categories: " + ", ".join(selected_non_ai_labels)]
        record_decision("Step 1 — Negative scope check", "Non-AI category selected", notes)
        decision_badge("Result", "Likely not an AI system")
        st.markdown(
            "- You indicated at least one NON‑AI category.\n"
            "- These solutions follow predefined human rules and do not infer outputs using AI models."
        )
        record_decision("Final verdict", "Likely not an AI system", ["Classification completed at Step 1."])
        render_decision_log()
        export_assessment(
            {
                "result": "Likely not an AI system",
                "rationale": [
                    "Selected NON-AI category during Step 1.",
                    "These solutions follow predefined human rules and do not infer outputs using AI models.",
                ],
                "answers": answers,
                "decision_log": decision_log,
            }
        )
        st.stop()

    if not c_none:
        st.info("Select an option to continue the assessment.")
        st.stop()

    record_decision(
        "Step 1 — Negative scope check",
        "No non-AI categories apply",
        ["Confirmed none of the exclusion categories matched."],
    )

st.divider()

# -------- Step 2 — AI model development using AI techniques
section_header(
    "Step 2 — Was any component of your solution developed using **AI Techniques**?",
    "This step allows you to confirm if your system uses AI Models, by checking if any of its components was developed using machine learning or logic-and knowledge based techniques.",
)

generation_labels = {
    "complex_predictions": "Complex predictions",
    "recommendations": "Recommendations",
    "content": "Generative content",
    "decisions": "Automated decisions",
}

tech_ml_selected = st.checkbox("Yes, using Machine Learning techniques")
selected_ml = []
if tech_ml_selected:
    selected_ml = st.multiselect(
        "Select the machine learning techniques used (optional)",
        options=[
            "Supervised Learning",
            "Unsupervised Learning",
            "Self‑Supervised Learning",
            "Reinforcement Learning",
            "Deep Learning",
        ],
    )

tech_logic = st.checkbox("Yes, using Logic‑ and Knowledge‑Based Techniques")
none_selected = st.checkbox("No, None of these techniques was used")

st.markdown("---")
step2_unable_to_verify = st.checkbox("I am not able to verify this", key="step2_unable_to_verify")

if step2_unable_to_verify and (tech_ml_selected or tech_logic or none_selected or selected_ml):
    st.warning("Remove other selections to continue with the 'I am not able to verify this' option.")

answers.setdefault("ai_techniques", {})

if none_selected and (tech_ml_selected or tech_logic or selected_ml):
    st.warning("Remove other selections if you choose 'None of these techniques is used'.")

answers["ai_techniques"] = {
    "ml_selected": tech_ml_selected,
    "ml_techniques": selected_ml,
    "logic_knowledge_based": tech_logic,
    "none_selected": none_selected,
    "unable_to_verify": step2_unable_to_verify,
}

selected_tech_notes = []
if tech_ml_selected:
    if selected_ml:
        selected_tech_notes.append("Machine learning techniques identified: " + ", ".join(selected_ml))
    else:
        selected_tech_notes.append("Machine learning techniques identified (details not specified).")
if tech_logic:
    selected_tech_notes.append("Logic- and knowledge-based techniques identified.")

if step2_unable_to_verify:
    ai_model_knowledge = st.radio(
        "Do you know if the solution use AI Models?",
        options=[
            "Yes it use an AI Model",
            "No it does not",
            "I am not sure",
        ],
        index=None,
    )
    answers["ai_techniques"]["ai_model_knowledge"] = ai_model_knowledge

    if ai_model_knowledge is None:
        st.info("Select an option to continue the assessment.")
        st.stop()

    if ai_model_knowledge == "Yes it use an AI Model":
        rationale = [
            "User confirmed the solution uses an AI Model while unable to verify supporting techniques.",
            "Seek legal consultation to validate the declaration.",
        ]
        record_decision(
            "Step 2 — AI techniques",
            "Confirmed AI Model usage",
            [
                "Unable to verify specific AI techniques.",
                "User stated explicitly that an AI Model is used.",
            ],
        )
        decision_badge("Result", "AI system")
        st.markdown(
            "- You indicated the solution uses an AI Model.\n"
            "- It is advisable to seek legal consultation to confirm this assessment."
        )
        record_decision("Final verdict", "AI system", rationale)
        render_decision_log()
        export_assessment({"result": "AI system", "rationale": rationale, "answers": answers, "decision_log": decision_log})
        st.stop()

    if ai_model_knowledge == "No it does not":
        rationale = [
            "User indicated the solution does not use an AI Model while unable to verify techniques.",
            "Seek legal consultation to confirm the declaration.",
        ]
        record_decision(
            "Step 2 — AI techniques",
            "User denied AI Model usage",
            [
                "Unable to verify specific AI techniques.",
                "User stated the solution does not use an AI Model.",
            ],
        )
        decision_badge("Result", "Likely not an AI system")
        st.markdown(
            "- You indicated the solution does **not** use an AI Model.\n"
            "- It is advisable to seek legal consultation to confirm this assessment."
        )
        record_decision("Final verdict", "Likely not an AI system", rationale)
        render_decision_log()
        export_assessment(
            {
                "result": "Likely not an AI system",
                "rationale": rationale,
                "answers": answers,
                "decision_log": decision_log,
            }
        )
        st.stop()

    st.markdown("Is the solution generating any of the following?")
    g_complex_predictions = st.checkbox(
        "Complex Predictions\nThe system generates estimates about an unknown value (the output) from known values supplied to the system (the input). It uncovers complex correlations between variables to make accurate predictions.",
        key="g_complex_predictions",
    )
    g_recommendations = st.checkbox(
        "Recommendations\nThe system generates suggestions for specific actions, products, or services to users based on their preferences, behaviors, or other data inputs.",
        key="g_recommendations",
    )
    g_content = st.checkbox(
        "Content\nThe system generates new material such as text, images, videos, and audio, using Generative Pre-trained Transformer (GPT) technologies, or other generative models, typically Large Language Models.",
        key="g_content",
    )
    g_decisions = st.checkbox(
        "Decisions\nThe system generates conclusions or choices that fully automate processes that are traditionally handled by human judgement. The decision is produced in the environment surrounding the system without any human intervention.",
        key="g_decisions",
    )
    g_none = st.checkbox("None applies", key="g_none")

    generation_flags = {
        "complex_predictions": g_complex_predictions,
        "recommendations": g_recommendations,
        "content": g_content,
        "decisions": g_decisions,
        "none_applies": g_none,
    }
    answers["ai_techniques"]["generation_indicators"] = generation_flags

    if g_none and any([g_complex_predictions, g_recommendations, g_content, g_decisions]):
        st.warning("'None applies' cannot be selected together with other options.")
        st.stop()

    if not g_none and not any([g_complex_predictions, g_recommendations, g_content, g_decisions]):
        st.info("Select at least one option to continue the assessment.")
        st.stop()

    if any([g_complex_predictions, g_recommendations, g_content, g_decisions]):
        selected_generations = [
            label for key, label in generation_labels.items() if generation_flags.get(key)
        ]
        rationale = [
            "Unable to verify AI techniques but unsure about AI Model usage.",
            "Generation indicators selected: " + ", ".join(selected_generations),
            "Seek legal consultation to confirm this assessment.",
        ]
        record_decision(
            "Step 2 — AI techniques",
            "Generation behaviours observed",
            [
                "Unable to verify specific AI techniques or confirm AI Model usage.",
                "Indicators selected: " + ", ".join(selected_generations),
            ],
        )
        decision_badge("Result", "Likely an AI system")
        st.markdown(
            "- Based on your inputs, the solution is **likely an AI system**.\n"
            "- It is advisable to seek legal consultation to confirm this assessment."
        )
        record_decision("Final verdict", "Likely an AI system", rationale)
        render_decision_log()
        export_assessment(
            {
                "result": "Likely an AI system",
                "rationale": rationale,
                "answers": answers,
                "decision_log": decision_log,
            }
        )
        st.stop()

    if g_none:
        rationale = [
            "Unable to verify AI techniques and unsure about AI Model usage.",
            "No generation indicators were selected.",
            "Seek legal consultation to confirm this assessment.",
        ]
        record_decision(
            "Step 2 — AI techniques",
            "No generation indicators",
            [
                "Unable to verify specific AI techniques or confirm AI Model usage.",
                "User indicated none of the generation behaviours apply.",
            ],
        )
        decision_badge("Result", "Likely not an AI system")
        st.markdown(
            "- None of the listed generation indicators apply.\n"
            "- It is advisable to seek legal consultation to confirm this assessment."
        )
        record_decision("Final verdict", "Likely not an AI system", rationale)
        render_decision_log()
        export_assessment(
            {
                "result": "Likely not an AI system",
                "rationale": rationale,
                "answers": answers,
                "decision_log": decision_log,
            }
        )
        st.stop()

has_any_selection = tech_ml_selected or tech_logic or none_selected
uses_ai_techniques = tech_ml_selected or tech_logic

if none_selected:
    rationale = [
        "User selected 'None of these techniques is used'.",
        "Without AI techniques, the solution is generally not considered an AI system.",
    ]
    record_decision(
        "Step 2 — AI techniques",
        "No AI techniques declared",
        ["User confirmed that none of the listed AI techniques are used."],
    )
    decision_badge("Result", "Likely not an AI system")
    st.markdown(
        "- You selected **None of these techniques is used**.\n"
        "- Without components developed using AI techniques, a solution is generally **not considered** an AI system."
    )
    if selected_ml or tech_logic:
        st.markdown(
            "- Remove any other technique selections to avoid conflicting inputs."
        )
    record_decision("Final verdict", "Likely not an AI system", rationale)
    render_decision_log()
    export_assessment(
        {"result": "Likely not an AI system", "rationale": rationale, "answers": answers, "decision_log": decision_log}
    )
    st.stop()

if not has_any_selection:
    st.info("Select an option to continue the assessment.")
    st.stop()

if not uses_ai_techniques:
    # If no AI techniques are used, then not an AI system (per slide flow)
    rationale = [
        "No AI techniques were selected after Step 2 validation.",
        "Without components developed using AI techniques, the solution is generally not an AI system.",
    ]
    record_decision(
        "Step 2 — AI techniques",
        "No AI techniques selected",
        ["Confirmed absence of AI techniques after validation."],
    )
    decision_badge("Result", "Likely not an AI system")
    st.markdown(
        "- You did **not** select any AI techniques.\n"
        "- Without components developed using AI techniques, the solution is generally **not** an AI system."
    )
    record_decision("Final verdict", "Likely not an AI system", rationale)
    render_decision_log()
    export_assessment(
        {"result": "Likely not an AI system", "rationale": rationale, "answers": answers, "decision_log": decision_log}
    )
    st.stop()

record_decision(
    "Step 2 — AI techniques",
    "AI techniques identified",
    selected_tech_notes or ["At least one AI technique checkbox was selected."],
)

st.divider()

# -------- Step 3 — Optimization-only carve-out
section_header(
    "Step 3 — Are AI models used **only for mathematical optimization / speed‑up**?",
    "Mathematical optimization refers to the process of finding the best solution from a set of possible options by maximizing or minimizing a specific objective function, typically under defined constraints.",
)

opt_only = st.radio("Optimization-only usage?", options=["Yes", "No"], index=1, horizontal=True)
answers["optimization_only"] = opt_only == "Yes"

condition_labels = {
    "supporting_role_only": "Model plays a supporting role only",
    "fixed_after_deployment": "Model is fixed after deployment",
    "no_influence_objectives": "Model does not influence system objectives",
    "outputs_narrowly_scoped": "Outputs remain narrowly scoped",
    "performance_is_efficiency": "Performance is measured as efficiency gains",
}

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

selected_condition_labels = [
    condition_labels[key]
    for key, value in conditions.items()
    if value
]
missing_condition_labels = [
    condition_labels[key]
    for key in condition_labels
    if not conditions.get(key, False)
]

if opt_only == "Yes":
    step3_outcome = "Optimization carve-out evaluated"
    step3_notes = ["User indicated AI models are used for optimization-only purposes."]
    if selected_condition_labels:
        step3_notes.append("Conditions satisfied: " + ", ".join(selected_condition_labels))
    if not all_conditions_true and missing_condition_labels:
        step3_notes.append("Conditions not selected: " + ", ".join(missing_condition_labels))
else:
    step3_outcome = "Optimization carve-out not claimed"
    step3_notes = ["User selected 'No' for optimization-only usage."]

record_decision("Step 3 — Optimization carve-out", step3_outcome, step3_notes)

st.divider()

# -------- Final decision logic
rationale = []
if opt_only == "Yes" and all_conditions_true:
    verdict = (
        "Your solution is a borderline case. It likely falls outside the definition of AI system, "
        "but it is advisable to seek legal advice to confirm this."
    )
    rationale.append(
        "Optimization‑only usage and **all** optimization carve‑out conditions satisfied. Borderline case—seek legal advice."
    )
elif opt_only == "Yes" and not all_conditions_true:
    verdict = "AI system"
    rationale.append("Optimization‑only usage **but** not all carve‑out conditions satisfied.")
else:
    verdict = "AI system"
    rationale.append("Uses AI techniques and not limited to optimization‑only carve‑out.")

# Enrich rationale with optional info
inference_autonomy = answers.get("inference_autonomy", {})
if inference_autonomy.get("infers_outputs"):
    rationale.append("Confirms inference from inputs to outputs.")
if inference_autonomy.get("varying_autonomy"):
    rationale.append("Operates with varying levels of autonomy (may still be human‑in-the-loop).")

# -------- Display result
decision_badge("Result", verdict)
st.markdown("**Rationale**")
for r in rationale:
    st.markdown(f"- {r}")

# -------- Export
record_decision("Final verdict", verdict, rationale)
render_decision_log()
assessment = {"result": verdict, "rationale": rationale, "answers": answers, "decision_log": decision_log}
export_assessment(assessment)

st.caption(
    "This tool reflects the decision structure in your illustration. For borderline cases, escalate for expert review and document assumptions."
)
