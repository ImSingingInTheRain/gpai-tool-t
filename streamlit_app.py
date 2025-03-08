import streamlit as st
import pandas as pd
import io
 
# ===============================
#   Refined GPAI Assessment Tool
#   Implementing EU AI Act Criteria
# ===============================

# ----------------------------------------------------------------------------
# Intro & Context: Aligning with EU AI Act
# ----------------------------------------------------------------------------

st.title("Refined GPAI Assessment Tool (EU AI Act)")

st.markdown("""
This **Refined GPAI Assessment Tool** aligns with the draft EU AI Act’s provisions
for **General-Purpose AI (GPAI)**. Each step references specific **Articles** and
**Recitals** to ensure legal conformity and traceability.  

**Key References**:  
- **Article 51 & Recitals 98–99**: Defining GPAI criteria (≥1B parameters, broad task range).  
- **Article 53**: Baseline obligations for GPAI model providers.  
- **Article 55 & Recital 110**: Enhanced obligations for GPAI models with systemic risk.  
- **Recital 109**: Proportional obligations, especially for SMEs, non-commercial developers, or fine-tuning.  

Use this tool to (1) determine if your model qualifies as GPAI, (2) classify its risk level,
and (3) map relevant legal obligations.
""")

# ----------------------------------------------------------------------------
# Preliminary: Provider Context & Proportionality (Recital 109)
# ----------------------------------------------------------------------------

st.subheader("Provider Context (Recital 109)")
provider_type = st.radio(
    "Select your organizational context",
    options=[
        "Large commercial provider",
        "SME or startup",
        "Academic or non-commercial research entity",
        "Public sector / other"
    ],
    help="Per Recital 109, obligations can be proportionate to the provider’s context."
)

# Prompt user to justify if not 'Large commercial provider'
if provider_type != "Large commercial provider":
    st.info("""
    **Note**: Recital 109 acknowledges proportionate obligations for smaller
    or research-focused providers. However, you still must meet essential
    GPAI obligations if your model meets the criteria.
    """)

provider_context_justification = st.text_area(
    "If you plan to adjust or scale obligations, explain how your context justifies it (Recital 109)."
)

# ----------------------------------------------------------------------------
# Step 1: Specialized vs. Potentially General-Purpose
# ----------------------------------------------------------------------------

st.header("Step 1: Specialized vs. Potentially General-Purpose")

st.markdown("""
**Check if your model is exclusively specialized** (e.g., purely rule-based systems,
small classifiers, single-purpose anomaly detection, or traditional statistical models).
If so, it likely does **not** qualify as a General-Purpose AI (Recital 98).
""")

specialized_radio = st.radio(
    "Does your model appear entirely specialized (no broad or flexible capabilities)?",
    ["Yes (Specialized/Narrow)", "No (Potentially General-Purpose)"],
    key="specialized_radio"
)

if specialized_radio == "Yes (Specialized/Narrow)":
    st.error("**Conclusion**: The model is specialized and falls outside the GPAI scope.")
    st.stop()

# ----------------------------------------------------------------------------
# Step 2: Is the organization considered a 'Provider' under the AI Act?
# ----------------------------------------------------------------------------

st.subheader("Step 2: Provider Determination (Article 3 & 53)")

developed_internally = st.radio(
    "Did you develop the model internally, or is it from a third party?",
    ["Internally Developed", "Third Party"],
    help="Per Article 3, the 'provider' is the entity that develops or substantially modifies the model."
)

if developed_internally == "Third Party":
    st.markdown("""
    **If no substantial modifications have been made** to the third-party model, you are generally **not**
    considered the provider. However, if you **substantially modify** it, you **become the provider** and
    must comply with the corresponding obligations (Article 53 & Recital 109).
    """)

    st.info("Assess potential substantial modifications (Recital 109)")

    substantial_mod_questions = {
        "param_change": ("Have you changed >10% of parameters or model architecture?", "Yes", "No"),
        "purpose_change": ("Is the intended purpose or functionality significantly changed?", "Yes", "No"),
        "data_change": ("Have you retrained on distinctly different data (extensive fine-tuning)?", "Yes", "No"),
        "integration_change": ("Does modification significantly alter downstream integration?", "Yes", "No")
    }

    substantial_mod = False
    for key, (question, yes_label, no_label) in substantial_mod_questions.items():
        answer = st.radio(question, [yes_label, no_label], key=f"mod_{key}")
        if answer == "Yes":
            substantial_mod = True

    if not substantial_mod:
        st.success("""
        **No substantial modifications** – You are likely **not** the provider under Article 3.
        No further GPAI obligations generally apply.
        """)
        st.stop()
    else:
        st.warning("""
        **Substantial modification** – You are considered the provider (Article 3).
        Proceed with full GPAI assessment.
        """)

# ----------------------------------------------------------------------------
# Step 3: GPAI Definition Checks (Recitals 98 & 99)
# ----------------------------------------------------------------------------

st.subheader("Step 3: Preliminary GPAI Checks")

st.markdown("""
Recital 98 states that models with **≥1B parameters** and **trained via large-scale self-supervision** 
are likely to exhibit "significant generality."  
Recital 99 further highlights **generative** large language models as typical GPAI examples.
""")

preliminary_questions = {
    "param_scale": (
        "Approximate parameter count (Recital 98, threshold ~1B)?",
        ["< 1B", "1B–10B", "> 10B"]
    ),
    "training_scope": (
        "Was the model trained on large, diverse datasets using self-supervised or unsupervised methods?",
        ["No", "Partly", "Yes"]
    ),
    "broad_ability": (
        "Does it perform competently on multiple distinct tasks or domains?",
        ["No", "Partly", "Yes"]
    ),
    "generative_cap": (
        "Does it generate adaptable content (text, images, code) across tasks?",
        ["No", "Partly", "Yes"]
    )
}

prelim_score = 0
param_scale_score_map = {"< 1B": 0, "1B–10B": 1, "> 10B": 2}
yes_partly_no_map = {"No": 0, "Partly": 1, "Yes": 2}

responses_step3 = {}
for key, (question, options) in preliminary_questions.items():
    user_choice = st.radio(question, options, key=f"prelim_{key}")
    responses_step3[key] = user_choice
    
    # Assign points based on empirical thresholds (e.g., ≥1B parameters)
    if key == "param_scale":
        prelim_score += param_scale_score_map[user_choice]
    else:
        prelim_score += yes_partly_no_map[user_choice]

# If the preliminary score is too low, the model may be too small or specialized
if prelim_score < 3:
    st.error("""
    **Below threshold**: The model does not meet the basic criteria for GPAI 
    (Recitals 98 & 99). It may be specialized or too small in scale.
    """)
    st.stop()
else:
    st.success("Preliminary checks suggest possible GPAI characteristics. Proceed.")

# ----------------------------------------------------------------------------
# Step 4: Detailed Obligations & Further Scoring
# ----------------------------------------------------------------------------

st.subheader("Step 4: Detailed GPAI Compliance Checks (Article 53)")

st.markdown("""
Article 53(1) lists baseline requirements for providers of GPAI, including:
- **(a)** Technical documentation of training, testing, and evaluation  
- **(b)** Clear instructions for downstream users  
- **(c)** Copyright compliance policy  
- **(d)** Public summary of training data  

Please indicate the **level of compliance** for each baseline item:
""")

baseline_obligations = {
    "tech_doc": (
        "Technical documentation (Article 53(1)(a)): Do you have detailed documentation of training and evaluation?",
        ["Not in place (0)", "Partially in place (1)", "Fully in place (2)"]
    ),
    "instructions": (
        "Downstream usage instructions and disclosures (Article 53(1)(b)): Provided to end-users?",
        ["0 - None", "1 - Some partial instructions", "2 - Comprehensive guidelines"]
    ),
    "copyright": (
        "Copyright compliance policy (Article 53(1)(c)): Ensuring lawful use of data, references, etc.?",
        ["0 - None", "1 - Partial policy", "2 - Fully documented policy"]
    ),
    "data_summary": (
        "Public summary of training data (Article 53(1)(d)): Published or available?",
        ["0 - Not published", "1 - Partially available", "2 - Comprehensive summary"]
    )
}

baseline_score = 0
obligation_responses = {}
for key, (question, options) in baseline_obligations.items():
    user_choice = st.radio(question, options, key=f"obligation_{key}")
    obligation_responses[key] = user_choice

    # Extract numeric score from the answer (e.g., value in parentheses)
    numeric_val = int(user_choice.split("(")[-1].split(")")[0])
    baseline_score += numeric_val

# ----------------------------------------------------------------------------
# Step 5: Systemic Risk Classification (Articles 51, 55 & Recital 110)
# ----------------------------------------------------------------------------

st.subheader("Step 5: Systemic Risk Assessment")

st.markdown("""
**Article 51(1)** identifies models with “equivalent impact” as potential systemic-risk GPAI.  
- **Article 51(2)**: A training compute threshold of **≥10^25 FLOPs** is noted as an indicator.
- **Recital 110**: Points to large-scale harms (e.g., infrastructure disruptions, disinformation).
- **Article 55**: Imposes additional obligations for systemic-risk models (e.g., adversarial testing).

Answer the following to assess whether the model might be **GPAI with systemic risk**:
""")

systemic_questions = {
    "flop_threshold": (
        "Did training exceed ~10^25 FLOPs? (Article 51(2))",
        ["No", "Yes"]
    ),
    "sota_advancement": (
        "Is the model near state-of-the-art or has an equivalent high impact? (Article 51(1))",
        ["No", "Yes"]
    ),
    "mass_deployment": (
        "Is/will the model be widely deployed or integrated, potentially influencing large-scale users?",
        ["No", "Yes"]
    ),
    "harmful_scaffolding": (
        "Could the model significantly enable harmful applications via generative or scaffolding features?",
        ["No", "Yes"]
    )
}

systemic_score = 0
systemic_responses = {}
yes_no_map = {"No": 0, "Yes": 1}

for key, (question, options) in systemic_questions.items():
    user_choice = st.radio(question, options, key=f"sys_{key}")
    systemic_responses[key] = user_choice
    systemic_score += yes_no_map[user_choice]

# Basic logic for systemic risk classification
systemic_classification = "No"
if systemic_responses["flop_threshold"] == "Yes" or systemic_responses["sota_advancement"] == "Yes":
    systemic_classification = "Yes"
elif systemic_score > 1:
    st.warning("""
    **Borderline scenario**: Multiple indicators of systemic impact exist,
    but thresholds (Article 51 & Recital 110) are not conclusively met.
    """)
    final_risk_decision = st.radio(
        "Make a final classification on systemic risk (Article 51):",
        ["Yes - High Impact/Systemic", "No - Not Systemic"],
        key="borderline_sysrisk"
    )
    if final_risk_decision == "Yes - High Impact/Systemic":
        systemic_classification = "Yes"

# ----------------------------------------------------------------------------
# Step 6: Aggregated Scoring & Final Outcome
# ----------------------------------------------------------------------------

st.subheader("Step 6: Scoring & Outcome")

# Combine preliminary and baseline scores; note that systemic risk may impose additional obligations.
overall_score = prelim_score + baseline_score
# Maximum preliminary score: 8; Maximum baseline score: 8; Total max = 16.

st.write(f"**Preliminary Score** (Recitals 98/99) = {prelim_score}/8")
st.write(f"**Baseline Compliance Score** (Article 53) = {baseline_score}/8")

if systemic_classification == "Yes":
    st.error("""
    **Systemic Risk Detected** (Article 51) – Additional obligations under
    **Article 55** (e.g., adversarial testing, stricter documentation, incident reporting).
    """)
else:
    st.success("No conclusive systemic risk identified (Article 51).")

# Overall classification based on weighted scores
if overall_score >= 12:
    compliance_status = "Compliant or Mostly Compliant with Baseline GPAI Obligations"
elif overall_score >= 8:
    compliance_status = "Provisionally Compliant (Some Gaps)"
else:
    compliance_status = "Non-Compliant / High Risk (Insufficient Baseline) - Remediation Needed"

st.write(f"**Compliance Summary**: {compliance_status}")

if compliance_status in ["Provisionally Compliant (Some Gaps)", "Non-Compliant / High Risk (Insufficient Baseline) - Remediation Needed"]:
    st.info("Please provide any justification or next steps for remediation.")
    user_remediation = st.text_area("Justification / Remediation Plan:")

# ----------------------------------------------------------------------------
# Step 7: Obligations Mapping & Downloadable Report
# ----------------------------------------------------------------------------

st.subheader("Step 7: Obligations Mapping & Report Generation")

st.markdown("""
Below is a summary mapping each compliance item to the relevant **EU AI Act Articles**:
- **Article 53(1)(a)**: Technical documentation  
- **Article 53(1)(b)**: Downstream instructions  
- **Article 53(1)(c)**: Copyright policy  
- **Article 53(1)(d)**: Public data summary  
- **Article 55**: Additional obligations for Systemic Risk AI  
""")

# Compile the final report data for export
report_data = {
    "Provider Type (Recital 109)": provider_type,
    "Provider Justification": provider_context_justification,
    "Specialized Model Step1": specialized_radio,
    "Preliminary Score": prelim_score,
    "Baseline Score": baseline_score,
    "Systemic Risk? (Article 51)": systemic_classification,
    "Overall Compliance Status": compliance_status
}

# Merge additional details from Steps 3, 4, and 5
for k, v in responses_step3.items():
    report_data[f"Step3_{k}"] = v
for k, v in obligation_responses.items():
    report_data[f"Step4_{k}"] = v
for k, v in systemic_responses.items():
    report_data[f"Step5_{k}"] = v

# Additional documentation fields
model_name = st.text_input("Model Name/Identifier")
report_data["Model Name"] = model_name

provider_name = st.text_input("Provider Name/Entity")
report_data["Provider Name"] = provider_name

# Button to generate and download CSV report
if st.button("Generate & Download Report"):
    buffer = io.StringIO()
    df_report = pd.DataFrame([report_data])
    df_report.to_csv(buffer, index=False)
    
    st.download_button(
        label="Download Assessment CSV",
        data=buffer.getvalue(),
        file_name=f"GPAI_Assessment_{model_name}.csv",
        mime="text/csv"
    )

st.success("Assessment Complete. Review obligations and consider any next steps to ensure compliance.")