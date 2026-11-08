
import os
import streamlit as st

from engine import evaluate, calculate, FACTS


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SIP Performance Explainer",
    page_icon="📖",
    layout="centered",
)

st.title("SIP Performance Explainer")

st.caption(
    "A student PM prototype · Not affiliated with Groww · "
    "For education, not investment advice"
)

st.write(
    "Confused by the returns on your SIP? "
    "Try a hypothetical example to understand what the numbers mean. "
    "No login, portfolio upload or personal information needed."
)


# --------------------------------------------------
# OPENROUTER CONFIGURATION
# --------------------------------------------------

api_key = os.environ.get("OPENROUTER_API_KEY", "")
model = os.environ.get("OPENROUTER_MODEL", "openrouter/free")

try:
    api_key = st.secrets.get("OPENROUTER_API_KEY", api_key)
    model = st.secrets.get("OPENROUTER_MODEL", model)
except Exception:
    pass


# --------------------------------------------------
# QUESTION FORM
# --------------------------------------------------

with st.form("question"):

    question = st.text_area(
        "What would you like to understand?",
        value=(
            "My 1D return is -₹450 but my total return "
            "is positive. Was ₹450 deducted as a charge?"
        ),
        height=110,
    )

    col1, col2 = st.columns(2)

    with col1:
        invested = st.number_input(
            "Example amount invested (₹)",
            min_value=0.0,
            value=18000.0,
            step=500.0,
        )

    with col2:
        current = st.number_input(
            "Example current value (₹)",
            min_value=0.0,
            value=19200.0,
            step=500.0,
        )

    submitted = st.form_submit_button(
        "Explain these numbers",
        type="primary",
        use_container_width=True,
    )


# --------------------------------------------------
# EXAMPLE CALCULATION
# --------------------------------------------------

numbers = calculate(invested, current)

if numbers is not None:

    difference = numbers["difference"]
    percentage = numbers["simple_pct"]

    if difference > 0:
        st.caption(
            f"Overall gain in this example: "
            f"+₹{difference:,.2f} ({percentage:+.2f}%)"
        )

    elif difference < 0:
        st.caption(
            f"Overall loss in this example: "
            f"-₹{abs(difference):,.2f} ({percentage:+.2f}%)"
        )

    else:
        st.caption(
            "Overall gain/loss in this example: ₹0 (0.00%)"
        )


# --------------------------------------------------
# AI EXPLANATION
# --------------------------------------------------

if submitted:

    with st.spinner("Checking the explanation..."):

        result = evaluate(
            question=question,
            invested=invested,
            current=current,
            api_key=api_key,
            model=model,
        )

    if result.gate == "Pass":

        st.success("Explanation checked")

    else:

        st.warning(
            "We couldn't confidently explain this question. "
            "You can still use the glossary below."
        )

    st.write(result.explanation)

    # Plain-language explanation of the quality gate.
    # The actual checks remain enforced in engine.py.

    with st.expander("How was this explanation checked?"):

        if result.gate == "Pass":

            st.write(
                "We identified the topic of your question, "
                "checked the classification, and matched it "
                "to a reviewed educational explanation. "
                "The example calculations were checked separately."
            )

        else:

            st.write(
                "We couldn't verify the explanation confidently, "
                "so we did not release an AI-selected answer. "
                "You can still read the glossary below."
            )

        # Retain diagnostic information for testing.
        with st.expander("Technical details"):

            st.write(f"Topic: {result.topic}")
            st.write(f"Check: {result.reason}")
            st.write(f"Source: {result.source}")


# --------------------------------------------------
# NON-AI GLOSSARY
# --------------------------------------------------

st.divider()

st.subheader("Explore the SIP metrics")

st.write(
    "These explanations are available without AI. "
    "Use them to understand the terms at your own pace."
)

for title, body in FACTS.values():

    with st.expander(title):
        st.write(body)


# --------------------------------------------------
# LIMITATIONS
# --------------------------------------------------

st.divider()

with st.expander("What this prototype can and cannot do"):

    st.markdown(
        """
        **What it can do**

        - Explain common SIP performance terms.
        - Interpret hypothetical invested and current values.
        - Help distinguish daily changes from overall returns.
        - Provide a non-AI glossary.

        **What it cannot do**

        - Access your Groww account or transactions.
        - Verify whether a real charge or withdrawal occurred.
        - Calculate XIRR without dated cash flows.
        - Recommend funds, predict returns or execute transactions.
        """
    )

st.caption(
    "All calculations use hypothetical values. "
    "A market-value change alone does not establish a cash "
    "withdrawal or charge. Verify account-specific information "
    "with the official platform. "
    "Questions submitted for AI classification are sent through "
    "OpenRouter to the selected model provider. "
    "Do not enter personal or identifying financial information."
)
