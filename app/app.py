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
# Custom styling
# ---------------------------------------------------------

st.markdown(
    """
    <style>
        /* Main page */
        .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        /* Header */
        .cybersignal-eyebrow {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }

        .cybersignal-title {
            font-size: 2.4rem;
            font-weight: 750;
            line-height: 1.1;
            margin-bottom: 0.45rem;
        }

        .cybersignal-subtitle {
            font-size: 1.05rem;
            color: #6b7280;
            max-width: 850px;
            margin-bottom: 1.5rem;
        }

        /* Metric cards */
        div[data-testid="stMetric"] {
            background: #f8fafc;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem 1.1rem;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.82rem;
            color: #6b7280;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.7rem;
            font-weight: 700;
        }

        /* Section headings */
        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .section-description {
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        /* Discovery result count */
        .result-count {
            color: #6b7280;
            font-size: 0.88rem;
            margin: 0.7rem 0 0.4rem 0;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
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

st.markdown(
    '<div class="cybersignal-eyebrow">SALES INTELLIGENCE PLATFORM</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cybersignal-title">🛡️ CyberSignal</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cybersignal-subtitle">'
    'AI-native cybersecurity sales intelligence for discovering '
    'accounts, understanding observed technology environments, '
    'and generating evidence-grounded sales insights.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Summary metrics
# ---------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Accounts",
        f"{len(accounts):,}",
        help="Organizations represented in the application-ready dataset.",
    )

with col2:
    st.metric(
        "Technology Signals",
        f"{int(accounts['exposure_signal_count'].sum()):,}",
        help="Observed technology exposure signals across accounts.",
    )

with col3:
    st.metric(
        "Average ICP Fit",
        f"{accounts['icp_fit_score'].mean():.1f}",
        help="Average deterministic ICP-fit heuristic score.",
    )

# ---------------------------------------------------------
# Account Discovery
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">Account Discovery</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Search and filter organizations using observed infrastructure signals '
    'and the transparent ICP-fit heuristic.'
    '</div>',
    unsafe_allow_html=True,
)

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
# Account discovery results
# ---------------------------------------------------------

st.markdown(
    f'<div class="result-count">'
    f'Found <strong>{len(filtered_accounts):,}</strong> matching accounts'
    f'</div>',
    unsafe_allow_html=True,
)

if filtered_accounts.empty:
    st.warning("No accounts match the selected filters.")
    st.stop()


# Show the highest-ranked accounts before selection
display_accounts = filtered_accounts.head(10).copy()

display_accounts["ICP Fit"] = display_accounts[
    "icp_fit_score"
].map(lambda x: f"{x:.0f}")

display_accounts["IPs"] = display_accounts[
    "unique_ips"
].map(format_number)

display_accounts["Products"] = display_accounts[
    "unique_products"
].map(format_number)

display_accounts["Signals"] = display_accounts[
    "exposure_signal_count"
].map(format_number)

display_accounts["Organization"] = display_accounts[
    "normalized_organization"
].str.title()

st.dataframe(
    display_accounts[
        [
            "Organization",
            "organization_type",
            "ICP Fit",
            "IPs",
            "Products",
            "Signals",
        ]
    ].rename(
        columns={
            "organization_type": "Organization Type",
        }
    ),
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# Account selection
# ---------------------------------------------------------

st.markdown(
    '<div class="section-description">'
    'Select an account to view detailed intelligence and evidence.'
    '</div>',
    unsafe_allow_html=True,
)

account_options = filtered_accounts[
    "normalized_organization"
].tolist()

selected_account_name = st.selectbox(
    "Account",
    account_options,
)


selected_account = filtered_accounts[
    filtered_accounts["normalized_organization"]
    == selected_account_name
].iloc[0]


# ---------------------------------------------------------
# Selected Account Header
# ---------------------------------------------------------

st.divider()

account_display_name = selected_account[
    "normalized_organization"
].title()

st.markdown(
    f'<div class="section-title">{account_display_name}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="section-description">'
    f'{selected_account["organization_type"]} · '
    f'Deterministic ICP-fit heuristic'
    f'</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Account Overview
# ---------------------------------------------------------

st.markdown(
    '<div class="section-title">Account Overview</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'A compact view of the observed infrastructure footprint '
    'used by CyberSignal for account intelligence.'
    '</div>',
    unsafe_allow_html=True,
)


overview_col1, overview_col2, overview_col3, overview_col4 = st.columns(4)

with overview_col1:
    st.metric(
        "ICP Fit",
        f"{selected_account['icp_fit_score']:.0f}",
        help="Deterministic heuristic score based on observed account characteristics.",
    )

with overview_col2:
    st.metric(
        "Unique IPs",
        format_number(selected_account["unique_ips"]),
    )

with overview_col3:
    st.metric(
        "Products",
        format_number(selected_account["unique_products"]),
    )

with overview_col4:
    st.metric(
        "Countries",
        format_number(selected_account["countries_observed"]),
    )


# ---------------------------------------------------------
# Additional Account Metrics
# ---------------------------------------------------------

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:
    st.caption("Organization Type")
    st.write(selected_account["organization_type"])

with info_col2:
    st.caption("Observed Ports")
    st.write(
        format_number(
            selected_account["unique_ports"]
        )
    )

with info_col3:
    st.caption("Total Observations")
    st.write(
        format_number(
            selected_account["observation_count"]
        )
    )


# ---------------------------------------------------------
# Observed Technology Signals
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">Observed Technology Signals</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Technology categories derived from the observed infrastructure data. '
    'These are observations, not claims of vulnerabilities or incidents.'
    '</div>',
    unsafe_allow_html=True,
)

signal_rows = get_signal_rows(selected_account)

if signal_rows:

    signal_col1, signal_col2 = st.columns(2)

    midpoint = (len(signal_rows) + 1) // 2

    with signal_col1:

        for label, count in signal_rows[:midpoint]:

            st.write(
                f"**{label}**"
            )

            st.progress(
                min(
                    count
                    / max(
                        selected_account["unique_ips"],
                        1,
                    ),
                    1.0,
                )
            )

            st.caption(
                f"{count:,} observed IPs"
            )

    with signal_col2:

        for label, count in signal_rows[midpoint:]:

            st.write(
                f"**{label}**"
            )

            st.progress(
                min(
                    count
                    / max(
                        selected_account["unique_ips"],
                        1,
                    ),
                    1.0,
                )
            )

            st.caption(
                f"{count:,} observed IPs"
            )

else:

    st.info(
        "No classified technology signals were observed."
    )


# ---------------------------------------------------------
# Observation Window
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">Observation Window</div>',
    unsafe_allow_html=True,
)

window_col1, window_col2 = st.columns(2)

with window_col1:

    st.caption("First Seen")

    st.write(
        str(
            selected_account["first_seen"]
        )
    )

with window_col2:

    st.caption("Last Seen")

    st.write(
        str(
            selected_account["last_seen"]
        )
    )


# ---------------------------------------------------------
# Account Evidence
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">Account Evidence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Structured evidence passed to the AI layer. '
    'This keeps generated analysis grounded in observed data.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Build account evidence
# ---------------------------------------------------------

account_evidence = build_account_evidence(
    selected_account
)


with st.expander(
    "View structured account evidence"
):

    st.json(
        account_evidence
    )


# ---------------------------------------------------------
# AI Account Intelligence
# ---------------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">AI Account Intelligence</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Generate evidence-grounded intelligence using the '
    'structured account signals above.'
    '</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Generate AI Account Intelligence
# ---------------------------------------------------------

if st.button(
    "Generate AI Analysis",
    type="primary",
    use_container_width=True,
    key="generate_ai_analysis",
):

    with st.spinner(
        "Analyzing account evidence..."
    ):

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
    "account_intelligence"
    in st.session_state
    and st.session_state.get(
        "account_intelligence_account"
    ) == current_account
)


if has_current_intelligence:

    result = st.session_state[
        "account_intelligence"
    ]

    intelligence = result[
        "parsed"
    ]


    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    st.markdown(
        "### Summary"
    )

    st.write(
        intelligence.get(
            "summary",
            "",
        )
    )


    # -----------------------------------------------------
    # Why Relevant
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

    st.markdown(
        "### Evidence"
    )

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
    # Security Conversation
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
    # Recommended Angle
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

    st.markdown(
        "### Confidence"
    )

    st.info(
        confidence
    )


    # -----------------------------------------------------
    # LLM Metadata
    # -----------------------------------------------------

    with st.expander(
        "LLM Metadata"
    ):

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

    st.markdown(
        '<div class="section-title">Generate Outreach</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Generate concise prospect outreach grounded in '
        'the account evidence and AI analysis.'
        '</div>',
        unsafe_allow_html=True,
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
        "outreach_result"
        in st.session_state
        and st.session_state.get(
            "outreach_account"
        ) == current_account
    )


    if has_current_outreach:

        outreach_result = st.session_state[
            "outreach_result"
        ]

        outreach = outreach_result[
            "parsed"
        ]


        st.markdown(
            "### Sales Outreach"
        )


        # -------------------------------------------------
        # Subject
        # -------------------------------------------------

        st.markdown(
            "#### Subject"
        )

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

        st.markdown(
            "#### Opening"
        )

        st.write(
            outreach.get(
                "opening",
                "",
            )
        )


        # -------------------------------------------------
        # Body
        # -------------------------------------------------

        st.markdown(
            "#### Body"
        )

        st.write(
            outreach.get(
                "body",
                "",
            )
        )


        # -------------------------------------------------
        # Call to Action
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
        # Evidence Used
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