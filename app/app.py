import sys
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# Project path
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# Project imports
# ---------------------------------------------------------

from data import load_accounts
from src.signals.account_evidence import build_account_evidence
from src.llm.prompt_runner import (
    render_account_prompt,
    render_outreach_prompt,
)
from src.llm.client import generate_account_intelligence

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="CyberSignal",
    page_icon="🛡️",
    layout="wide",
)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

@st.cache_data
def get_accounts():
    return load_accounts()


accounts = get_accounts()


# ---------------------------------------------------------
# Helper functions
# ---------------------------------------------------------

def format_number(value):
    return f"{int(value):,}"


def get_signal_rows(account):
    signals = [
        ("Web", "web_ip_count"),
        ("Remote Access", "remote_access_ip_count"),
        ("Email", "email_ip_count"),
        ("Proxy", "proxy_ip_count"),
        ("Network", "network_ip_count"),
        ("Database", "database_ip_count"),
        ("IoT", "iot_ip_count"),
        ("Container", "container_ip_count"),
        ("Security Network", "security_network_ip_count"),
        ("File Transfer", "file_transfer_ip_count"),
    ]

    return [
        (label, int(account[column]))
        for label, column in signals
        if int(account[column]) > 0
    ]


# ---------------------------------------------------------
# Application header
# ---------------------------------------------------------

st.title("🛡️ CyberSignal")

st.subheader("AI-native cybersecurity sales intelligence")

st.write(
    "Discover organizations, understand their observed technology "
    "environment, and generate evidence-grounded sales intelligence."
)


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Accounts",
        f"{len(accounts):,}",
    )

with col2:
    st.metric(
        "Technology Signals",
        f"{int(accounts['exposure_signal_count'].sum()):,}",
    )

with col3:
    st.metric(
        "Average ICP Score",
        f"{accounts['icp_fit_score'].mean():.1f}",
    )


# ---------------------------------------------------------
# Account Discovery
# ---------------------------------------------------------

st.divider()

st.subheader("Account Discovery")

search_col, type_col, score_col = st.columns([2, 1, 1])

with search_col:
    search_term = st.text_input(
        "Search accounts",
        placeholder="Search by organization name...",
    )

with type_col:
    organization_types = ["All"] + sorted(
        accounts["organization_type"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_type = st.selectbox(
        "Organization type",
        organization_types,
    )

with score_col:
    minimum_score = st.slider(
        "Minimum ICP score",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
    )


# ---------------------------------------------------------
# Apply filters
# ---------------------------------------------------------

filtered_accounts = accounts.copy()

if search_term:
    search_term = search_term.strip().lower()

    filtered_accounts = filtered_accounts[
        filtered_accounts["normalized_organization"]
        .str.lower()
        .str.contains(search_term, na=False)
    ]

if selected_type != "All":
    filtered_accounts = filtered_accounts[
        filtered_accounts["organization_type"] == selected_type
    ]

filtered_accounts = filtered_accounts[
    filtered_accounts["icp_fit_score"] >= minimum_score
]


# ---------------------------------------------------------
# Sort accounts
# ---------------------------------------------------------

filtered_accounts = filtered_accounts.sort_values(
    by=[
        "icp_fit_score",
        "exposure_signal_count",
        "unique_products",
        "unique_ips",
    ],
    ascending=[False, False, False, False],
)


# ---------------------------------------------------------
# Account selection
# ---------------------------------------------------------

st.write(
    f"Found **{len(filtered_accounts):,}** matching accounts"
)

if filtered_accounts.empty:
    st.warning("No accounts match the selected filters.")
    st.stop()


account_options = filtered_accounts[
    "normalized_organization"
].tolist()

selected_account_name = st.selectbox(
    "Select an account",
    account_options,
)


selected_account = filtered_accounts[
    filtered_accounts["normalized_organization"]
    == selected_account_name
].iloc[0]


# ---------------------------------------------------------
# AI Account Intelligence
# ---------------------------------------------------------

st.divider()

st.subheader("AI Account Intelligence")

st.write(
    "Generate evidence-grounded account intelligence using "
    "the structured account signals."
)


# ---------------------------------------------------------
# Build account evidence
# ---------------------------------------------------------

account_evidence = build_account_evidence(selected_account)


# ---------------------------------------------------------
# Show account evidence
# ---------------------------------------------------------

with st.expander("View account evidence sent to AI"):

    st.json(account_evidence)


# ---------------------------------------------------------
# Generate AI Account Intelligence
# ---------------------------------------------------------

if st.button(
    "Generate AI Analysis",
    type="primary",
    use_container_width=True,
    key="generate_ai_analysis",
):

    with st.spinner("Analyzing account evidence..."):

        try:

            prompt = render_account_prompt(
                evidence=account_evidence,
                version="account_intelligence_v2",
            )

            result = generate_account_intelligence(
                prompt=prompt,
                account=selected_account[
                    "normalized_organization"
                ],
                prompt_version="account_intelligence_v2",
            )

            st.session_state[
                "account_intelligence"
            ] = result

            st.session_state[
                "account_intelligence_account"
            ] = selected_account[
                "normalized_organization"
            ]

            # Clear previous outreach when
            # generating new account intelligence.
            st.session_state.pop(
                "outreach_result",
                None,
            )

            st.session_state.pop(
                "outreach_account",
                None,
            )

        except Exception as e:

            st.error(
                f"Unable to generate AI analysis: {e}"
            )


# ---------------------------------------------------------
# Display AI Account Intelligence
# ---------------------------------------------------------

current_account = selected_account[
    "normalized_organization"
]

has_current_intelligence = (
    "account_intelligence" in st.session_state
    and st.session_state.get(
        "account_intelligence_account"
    ) == current_account
)


if has_current_intelligence:

    result = st.session_state[
        "account_intelligence"
    ]

    intelligence = result["parsed"]


    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    st.markdown("### Summary")

    st.write(
        intelligence.get(
            "summary",
            "",
        )
    )


    # -----------------------------------------------------
    # Why relevant
    # -----------------------------------------------------

    st.markdown(
        "### Why This Account May Be Relevant"
    )

    st.write(
        intelligence.get(
            "why_relevant",
            "",
        )
    )


    # -----------------------------------------------------
    # Evidence
    # -----------------------------------------------------

    st.markdown("### Evidence")

    evidence_items = intelligence.get(
        "evidence",
        [],
    )

    for item in evidence_items:

        signal = item.get(
            "signal",
            "",
        )

        observation = item.get(
            "observation",
            "",
        )

        st.write(
            f"**{signal.replace('_', ' ').title()}** — "
            f"{observation}"
        )


    # -----------------------------------------------------
    # Security conversation
    # -----------------------------------------------------

    st.markdown(
        "### Security Conversation"
    )

    st.write(
        intelligence.get(
            "security_conversation",
            "",
        )
    )


    # -----------------------------------------------------
    # Recommended angle
    # -----------------------------------------------------

    st.markdown(
        "### Recommended Angle"
    )

    st.write(
        intelligence.get(
            "recommended_angle",
            "",
        )
    )


    # -----------------------------------------------------
    # Confidence
    # -----------------------------------------------------

    confidence = intelligence.get(
        "confidence",
        "UNKNOWN",
    )

    st.markdown("### Confidence")

    st.info(confidence)


    # -----------------------------------------------------
    # LLM Metadata
    # -----------------------------------------------------

    with st.expander("LLM Metadata"):

        st.json(
            result.get(
                "metadata",
                {},
            )
        )


    # =====================================================
    # OUTREACH GENERATION
    # =====================================================

    st.divider()

    st.subheader("Generate Outreach")

    st.write(
        "Generate a concise, evidence-grounded sales "
        "message based on the account intelligence."
    )


    if st.button(
    "Generate Outreach",
    type="primary",
    use_container_width=True,
    key="generate_outreach",
):

        with st.spinner(
            "Generating outreach..."
        ):

            try:

                outreach_prompt = (
                    render_outreach_prompt(
                        evidence=account_evidence,
                        intelligence=intelligence,
                        version="outreach_v1",
                    )
                )

                outreach_result = (
                    generate_account_intelligence(
                        prompt=outreach_prompt,
                        account=current_account,
                        prompt_version="outreach_v1",
                    )
                )

                st.session_state[
                    "outreach_result"
                ] = outreach_result

                st.session_state[
                    "outreach_account"
                ] = current_account

            except Exception as e:

                st.error(
                    f"Unable to generate outreach: {e}"
                )


    # -----------------------------------------------------
    # Display Outreach
    # -----------------------------------------------------

    has_current_outreach = (
        "outreach_result" in st.session_state
        and st.session_state.get(
            "outreach_account"
        ) == current_account
    )


    if has_current_outreach:

        outreach_result = st.session_state[
            "outreach_result"
        ]

        outreach = outreach_result["parsed"]


        st.markdown("### Sales Outreach")


        # -------------------------------------------------
        # Subject
        # -------------------------------------------------

        st.markdown("#### Subject")

        st.code(
            outreach.get(
                "subject",
                "",
            ),
            language=None,
        )


        # -------------------------------------------------
        # Opening
        # -------------------------------------------------

        st.markdown("#### Opening")

        st.write(
            outreach.get(
                "opening",
                "",
            )
        )


        # -------------------------------------------------
        # Body
        # -------------------------------------------------

        st.markdown("#### Body")

        st.write(
            outreach.get(
                "body",
                "",
            )
        )


        # -------------------------------------------------
        # Call to action
        # -------------------------------------------------

        st.markdown(
            "#### Call to Action"
        )

        st.write(
            outreach.get(
                "call_to_action",
                "",
            )
        )


        # -------------------------------------------------
        # Evidence used
        # -------------------------------------------------

        st.markdown(
            "#### Evidence Used"
        )

        outreach_evidence = outreach.get(
            "evidence_used",
            [],
        )

        for item in outreach_evidence:

            signal = item.get(
                "signal",
                "",
            )

            observation = item.get(
                "observation",
                "",
            )

            st.write(
                f"**{signal.replace('_', ' ').title()}** — "
                f"{observation}"
            )


        # -------------------------------------------------
        # Outreach LLM Metadata
        # -------------------------------------------------

        with st.expander(
            "Outreach LLM Metadata"
        ):

            st.json(
                outreach_result.get(
                    "metadata",
                    {},
                )
            )

# ---------------------------------------------------------
# Account overview
# ---------------------------------------------------------

st.subheader("Account Overview")

overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    st.metric(
        "ICP Fit Score",
        f"{selected_account['icp_fit_score']:.1f}",
    )

with overview_col2:
    st.metric(
        "Unique IPs",
        format_number(selected_account["unique_ips"]),
    )

with overview_col3:
    st.metric(
        "Unique Products",
        format_number(selected_account["unique_products"]),
    )

with overview_col4:
    st.metric(
        "Countries",
        format_number(selected_account["countries_observed"]),
    )


# ---------------------------------------------------------
# Organization information
# ---------------------------------------------------------

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.write("**Organization Type**")
    st.write(selected_account["organization_type"])

with info_col2:
    st.write("**Observed Ports**")
    st.write(format_number(selected_account["unique_ports"]))

with info_col3:
    st.write("**Observations**")
    st.write(format_number(selected_account["observation_count"]))


# ---------------------------------------------------------
# Technology Signals
# ---------------------------------------------------------

st.divider()

st.subheader("Observed Technology Signals")

signal_rows = get_signal_rows(selected_account)

if signal_rows:

    signal_col1, signal_col2 = st.columns(2)

    midpoint = (len(signal_rows) + 1) // 2

    with signal_col1:
        for label, count in signal_rows[:midpoint]:
            st.write(f"**{label}**")
            st.progress(
                min(count / max(
                    selected_account["unique_ips"],
                    1
                ), 1.0)
            )
            st.caption(f"{count:,} observed IPs")

    with signal_col2:
        for label, count in signal_rows[midpoint:]:
            st.write(f"**{label}**")
            st.progress(
                min(count / max(
                    selected_account["unique_ips"],
                    1
                ), 1.0)
            )
            st.caption(f"{count:,} observed IPs")

else:
    st.info("No classified technology signals were observed.")


# ---------------------------------------------------------
# Observation Window
# ---------------------------------------------------------

st.divider()

st.subheader("Observation Window")

window_col1, window_col2 = st.columns(2)

with window_col1:
    st.write("**First Seen**")
    st.write(str(selected_account["first_seen"]))

with window_col2:
    st.write("**Last Seen**")
    st.write(str(selected_account["last_seen"]))


