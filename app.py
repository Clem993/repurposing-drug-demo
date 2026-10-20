"""Interactive drug repurposing demonstration using an included synthetic dataset."""

from copy import deepcopy
from html import escape
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


APP_TITLE = "Indication Expansion & Drug Repurposing Demo"
NAVY = "#243447"
BLUE = "#3B82A0"
AMBER = "#B87818"
SLATE = "#64748B"
PALE_BLUE = "#EAF2F6"
PALE_AMBER = "#FFF5DF"
LIGHT = "#F3F5F7"
BORDER = "#DCE3EA"
INK = "#1F2937"
WHITE = "#FFFFFF"
SYSTEM_FONT = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
TIER_COLOURS = {"I": BLUE, "II": AMBER, "III": SLATE}
SYNTHETIC_NOTICE = (
    "Synthetic demonstration. All compounds, targets, evidence flags and rankings are fictional. "
    "Disease names provide example context only. No live databases are queried, and the results "
    "do not establish efficacy, safety or clinical suitability."
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Icons are small inline vectors. The interface has no image-file or font downloads.
ICON_PATHS = {
    "home": '<path d="M3 11 12 3l9 8M5 10v11h5v-7h4v7h5V10"/>',
    "compound": '<path d="M9 3v6L4 18a2 2 0 0 0 2 3h12a2 2 0 0 0 2-3l-5-9V3M8 3h8M7 15h10"/>',
    "data": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
    "network": '<circle cx="12" cy="5" r="3"/><circle cx="5" cy="19" r="3"/><circle cx="19" cy="19" r="3"/><path d="m10 8-4 8m8-8 4 8M8 19h8"/>',
    "chart": '<path d="M3 3v18h18M7 17v-5m5 5V7m5 10V4"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    "clinical": '<path d="M9 3h6v6h6v6h-6v6H9v-6H3V9h6Z"/>',
    "safety": '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6Z"/><path d="M12 8v5m0 3v1"/>',
    "book": '<path d="M3 4h6a3 3 0 0 1 3 3v14a4 4 0 0 0-4-2H3Zm18 0h-6a3 3 0 0 0-3 3v14a4 4 0 0 1 4-2h5Z"/>',
    "search": '<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',
    "start": '<circle cx="12" cy="12" r="9"/><path d="m10 8 6 4-6 4Z"/>',
    "matrix": '<path d="M3 3h18v18H3ZM3 9h18M3 15h18M9 3v18m6-18v18"/>',
}


def icon_html(name, size=28):
    """Decorative vectors accompany visible text labels."""
    paths = ICON_PATHS.get(name, ICON_PATHS["compound"])
    return (
        f'<svg width="{int(size)}" height="{int(size)}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{BLUE}" stroke-width="1.6" stroke-linecap="round" '
        f'stroke-linejoin="round" aria-hidden="true" focusable="false" '
        f'style="vertical-align:middle;flex-shrink:0">{paths}</svg>'
    )


st.markdown(
    f"""
<style>
    .stApp {{ background: {WHITE}; color: {INK}; }}
    .stApp, .stApp input, .stApp button, .stApp textarea, .stApp select {{
        font-family: {SYSTEM_FONT};
    }}
    section[data-testid="stSidebar"] {{
        background: {LIGHT}; border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] .stButton > button {{
        width: 100%; text-align: left; border-color: {BORDER};
    }}
    h1, h2, h3, h4 {{ color: {NAVY}; }}
    .page-header {{
        background: {PALE_BLUE}; border: 1px solid {BORDER};
        border-left: 5px solid {BLUE}; padding: 1.5rem 1.75rem;
        border-radius: 12px; margin-bottom: 1rem;
    }}
    .page-header h1 {{
        color: {NAVY}; font-size: 1.65rem; font-weight: 650;
        margin: 0; display: flex; align-items: center; gap: 14px;
    }}
    .page-header p {{ color: {SLATE}; margin: 0.5rem 0 0; }}
    .metric-card {{
        border: 1px solid {BORDER}; border-left: 4px solid {BLUE};
        border-radius: 10px; padding: 1.1rem; min-height: 140px;
        background: {WHITE}; margin-bottom: 0.75rem;
    }}
    .metric-card h3 {{ font-size: 0.78rem; margin: 0 0 0.6rem; }}
    .metric-card .value {{ font-size: 1.35rem; font-weight: 650; color: {NAVY}; margin: 0; }}
    .metric-card .subtext {{ font-size: 0.78rem; color: {SLATE}; margin: 0.4rem 0 0; }}
    .section-header {{
        display: flex; align-items: center; gap: 10px; color: {NAVY};
        font-size: 1.15rem; font-weight: 650; margin: 1.4rem 0 1rem;
        padding-bottom: 0.5rem; border-bottom: 2px solid {BORDER};
    }}
    .workflow-step {{
        text-align: center; padding: 1rem 0.65rem; border-radius: 10px;
        border: 1px solid {BORDER}; border-top: 4px solid {BORDER}; min-height: 172px;
    }}
    .workflow-step.active {{ border-top-color: {BLUE}; background: {PALE_BLUE}; }}
    .workflow-step.complete {{ border-top-color: {AMBER}; background: {PALE_AMBER}; }}
    .step-title {{ font-weight: 650; color: {NAVY}; margin: 0.6rem 0 0.3rem; font-size: 0.86rem; }}
    .step-desc {{ color: {SLATE}; font-size: 0.77rem; }}
    .info-box {{
        background: {LIGHT}; border: 1px solid {BORDER}; border-radius: 10px;
        padding: 1.2rem 1.4rem; margin: 0.8rem 0;
    }}
    .info-box p:last-child {{ margin-bottom: 0; }}
    .detail-card {{ background: {LIGHT}; border: 1px solid {BORDER}; padding: 1.2rem; border-radius: 10px; }}
    .tier-badge {{ display: inline-block; padding: 0.35rem 0.8rem; border-radius: 20px; font-weight: 650; font-size: 0.8rem; }}
    .tier-i {{ background: {PALE_BLUE}; color: {BLUE}; }}
    .tier-ii {{ background: {PALE_AMBER}; color: {AMBER}; }}
    .tier-iii {{ background: {LIGHT}; color: {SLATE}; border: 1px solid {BORDER}; }}
    .score-box {{ color: {WHITE}; padding: 0.55rem; border-radius: 8px; text-align: center; font-weight: 650; }}
    .evidence-card {{ text-align: center; border: 1px solid {BORDER}; border-radius: 8px; padding: 1rem 0.5rem; min-height: 140px; }}
    .evidence-card p {{ font-size: 0.78rem; margin: 0.5rem 0 0; }}
    .stButton > button[kind="primary"] {{ background: {BLUE}; border-color: {BLUE}; color: {WHITE}; }}
    .stButton > button:hover {{ border-color: {BLUE}; }}
</style>
""",
    unsafe_allow_html=True,
)

# The same ten-row fixture is intentionally shared by all three fictional compounds.
COMPOUNDS = {
    "DEMO-001": {"target": "TGT-001", "original_indication": "Sleep disorder example"},
    "DEMO-002": {"target": "TGT-002", "original_indication": "Cardiovascular example"},
    "DEMO-003": {"target": "TGT-003", "original_indication": "Neurological example"},
}
EVIDENCE = [
    ("clinical_trials", "Clinical trials", "clinical", "A simulated clinical record flag; no trial outcomes or patient records are included."),
    ("adverse_events", "Adverse events", "safety", "A simulated safety-report flag; its presence does not imply benefit, acceptable risk or causality."),
    ("literature", "Literature", "book", "A simulated publication flag; no referenced publications have been retrieved or assessed."),
    ("pathways", "Pathways", "network", "A simulated pathway association; direction, tissue relevance and mechanism require verification."),
    ("omics", "Omics", "data", "A simulated molecular-data flag; no raw measurements, statistical tests or experimental results are included."),
    ("interactome", "Interactome", "network", "A simulated interaction flag; no binding or functional interaction has been established."),
]
EVIDENCE_COLUMNS = [item[0] for item in EVIDENCE]
EVIDENCE_LABELS = [item[1] for item in EVIDENCE]
DATA_OPTIONS = {
    "lipidomics": "Lipidomic example flags",
    "metabolomics": "Metabolomic example flags",
    "knockdown": "Gene knockdown example flags",
    "clinical": "Clinical trial example flags",
}
STRATEGIES = ["Drug-centric", "Target-centric", "Disease-centric", "Combined review"]
THERAPEUTIC_AREAS = [
    "All therapeutic areas", "Oncology", "CNS / Neurology", "Metabolic / Endocrine",
    "Cardiovascular", "Rare disease", "Autoimmune / Inflammation", "Ophthalmology",
    "Respiratory", "Digestive / Liver", "Renal / Urology",
]
DEFAULT_CONFIG = {
    "compound": "DEMO-001",
    "strategy": STRATEGIES[0],
    "therapeutic_areas": [THERAPEUTIC_AREAS[0]],
    "evidence_threshold": 3,
    "data_options": {key: True for key in DATA_OPTIONS},
    "include_rare": True,
    "review_paediatric": False,
    "review_competition": False,
}
WORKFLOW_STEPS = [
    ("compound", "Data ingestion", "Load the selected fictional asset"),
    ("data", "Evidence review", "Inspect six included evidence categories"),
    ("network", "Association mapping", "Apply the example indication filters"),
    ("chart", "Frequency scoring", "Count available evidence categories"),
    ("data", "Omics integration", "Review the selected example flags"),
    ("target", "Prioritisation", "Rank the simulated evidence coverage"),
]


@st.cache_data
def load_sample_data():
    """Return explicitly synthetic flags and hypothetical review questions."""
    # Disease names are example labels, not claims of compound-disease associations.
    rows = [
        ("Retinal Degeneration", "Eye diseases", "Ophthalmology", False, [1, 1, 1, 1, 1, 1],
         "Review whether a hypothetical change in retinal cell survival could provide a repurposing hypothesis. The six flags illustrate broad evidence coverage only.",
         "Establish target expression in the relevant retinal cell types, exposure at the site of action and a reproducible functional endpoint."),
        ("Cystic Fibrosis", "Respiratory diseases", "Respiratory", True, [1, 1, 1, 1, 1, 0],
         "Explore an illustrative link between altered molecular profiles and disease biology. No rescue of the disease mechanism is demonstrated.",
         "Distinguish a disease-relevant effect from secondary metabolic changes, then assess it in a suitable experimental model."),
        ("Insulin Resistance", "Metabolic diseases", "Metabolic / Endocrine", False, [1, 1, 1, 1, 1, 0],
         "Consider a hypothetical overlap between molecular profiles and insulin-response pathways. The example contains no measured change in insulin sensitivity.",
         "Define the tissue, direction of effect and functional assay needed to test the proposed metabolic relationship."),
        ("Atherosclerosis", "Cardiovascular diseases", "Cardiovascular", False, [0, 1, 1, 1, 1, 0],
         "Use the example flags to frame a question about lipid handling and inflammatory signalling. A therapeutic relationship has not been established.",
         "Separate effects on lipid markers from effects on disease progression and assess relevant cardiovascular safety endpoints."),
        ("Non-Alcoholic Fatty Liver Disease", "Digestive diseases", "Digestive / Liver", False, [0, 1, 1, 1, 1, 0],
         "Examine a hypothetical relationship between molecular profiles and hepatic lipid accumulation. The demonstration includes no liver efficacy data.",
         "Specify a relevant disease model, exposure requirements and endpoints that distinguish lipid accumulation from tissue injury."),
        ("HIV-Associated Lipodystrophy", "Immune diseases", "Autoimmune / Inflammation", False, [0, 1, 1, 1, 0, 1],
         "Review whether an illustrative interaction pattern could justify studying adipose biology. The flags do not establish a disease mechanism or treatment effect.",
         "Check the biological context, potential confounding by concomitant treatment and the availability of appropriate functional measurements."),
        ("Schizophrenia", "Mental disorders", "CNS / Neurology", False, [0, 1, 1, 1, 1, 0],
         "Frame a hypothetical question about a central nervous system pathway. Neither brain exposure nor a psychiatric treatment effect is established.",
         "Verify target engagement, relevant cellular effects, exposure and a defensible link between the model and clinical endpoints."),
        ("Parkinson's Disease", "Neurodegenerative diseases", "CNS / Neurology", False, [0, 1, 1, 1, 0, 0],
         "Use the limited example coverage to identify gaps in a hypothetical neurodegeneration programme. The fixture contains no evidence of neuroprotection.",
         "Separate symptomatic hypotheses from disease-modification hypotheses and identify the experiments needed for each."),
        ("Chronic Kidney Disease", "Urological diseases", "Renal / Urology", False, [0, 1, 1, 0, 1, 0],
         "Consider an illustrative molecular-profile association with renal biology. The missing pathway and interaction flags identify unresolved questions.",
         "Assess renal exposure, relevant cell types and the relationship between molecular measurements and functional kidney endpoints."),
        ("Type 2 Diabetes", "Metabolic diseases", "Metabolic / Endocrine", False, [0, 0, 1, 1, 1, 0],
         "Review a hypothetical metabolic pathway overlap. The three example flags do not establish glucose control or a clinical development rationale.",
         "Define the mechanism, separate primary from secondary metabolic effects and identify efficacy and safety measurements for further study."),
    ]
    records = []
    for name, category, area, rare, flags, rationale, validation in rows:
        record = {
            "indication": name, "disease_category": category, "therapeutic_area": area,
            "rare_example": rare, "rationale": rationale, "validation_focus": validation,
        }
        record.update(dict(zip(EVIDENCE_COLUMNS, map(bool, flags))))
        records.append(record)
    return pd.DataFrame(records)


def configured_evidence(config):
    """Apply availability switches and recalculate category counts on a copy."""
    frame = load_sample_data().copy(deep=True)
    if not config["data_options"]["clinical"]:
        frame["clinical_trials"] = False
    if not any(config["data_options"][key] for key in ("lipidomics", "metabolomics", "knockdown")):
        frame["omics"] = False
    frame["score"] = frame[EVIDENCE_COLUMNS].sum(axis=1).astype(int)
    frame["tier"] = frame["score"].map(lambda score: "I" if score >= 5 else "II" if score == 4 else "III")
    frame["coverage"] = frame["tier"].map({"I": "5-6 categories", "II": "4 categories", "III": "0-3 categories"})
    frame["evidence_status"] = frame.apply(
        lambda row: "Simulated clinical + preclinical" if row["clinical_trials"]
        else "Simulated preclinical" if any(row[col] for col in ("pathways", "omics", "interactome"))
        else "Simulated literature", axis=1,
    )
    return frame


def filter_indications(frame, config, apply_threshold=True):
    """Filter the fixture by selected areas, rare examples and category count."""
    selected_areas = config["therapeutic_areas"]
    if "All therapeutic areas" not in selected_areas:
        area_mask = frame["therapeutic_area"].isin(selected_areas)
        if "Rare disease" in selected_areas:
            area_mask = area_mask | frame["rare_example"]
        frame = frame.loc[area_mask]
    if not config["include_rare"]:
        frame = frame.loc[~frame["rare_example"]]
    if apply_threshold:
        frame = frame.loc[frame["score"] >= config["evidence_threshold"]]
    return frame.sort_values("score", ascending=False, kind="stable").reset_index(drop=True)


def get_results(config):
    return filter_indications(configured_evidence(config), config)


def evidence_matrix(indications):
    return indications[["indication"] + EVIDENCE_COLUMNS].rename(
        columns={"indication": "Indication", **dict(zip(EVIDENCE_COLUMNS, EVIDENCE_LABELS))}
    )


def render_header(title, subtitle, icon="compound"):
    st.markdown(
        f'<div class="page-header"><h1>{icon_html(icon, 42)} {escape(title)}</h1>'
        f'<p>{escape(subtitle)}</p></div>', unsafe_allow_html=True,
    )
    st.caption(SYNTHETIC_NOTICE)


def section_header(title, icon="data"):
    st.markdown(f'<div class="section-header">{icon_html(icon)} {escape(title)}</div>', unsafe_allow_html=True)


def render_metric_card(title, value, subtext="", icon="chart"):
    return (
        f'<div class="metric-card"><h3>{icon_html(icon, 23)} {escape(title)}</h3>'
        f'<p class="value">{escape(str(value))}</p><p class="subtext">{escape(subtext)}</p></div>'
    )


def render_tier_badge(tier):
    return f'<span class="tier-badge tier-{tier.lower()}">Tier {escape(tier)}</span>'


def render_workflow_step(icon, title, description, status="pending"):
    status_class = status if status in ("active", "complete") else ""
    return (
        f'<div class="workflow-step {status_class}">{icon_html(icon, 34)}'
        f'<div class="step-title">{escape(title)}</div><div class="step-desc">'
        f'{escape(description)}</div></div>'
    )


def render_asset_details(compound):
    asset = COMPOUNDS[compound]
    st.markdown(
        f'<div class="detail-card"><p><strong>Compound:</strong> {escape(compound)} (fictional)</p>'
        f'<p><strong>Target:</strong> {escape(asset["target"])} (fictional)</p>'
        '<p><strong>Modality:</strong> Small molecule example</p>'
        f'<p><strong>Original indication:</strong> {escape(asset["original_indication"])}</p>'
        '<p><strong>Programme context:</strong> Hypothetical discontinued development programme</p></div>',
        unsafe_allow_html=True,
    )


def chart_layout(figure, height):
    figure.update_layout(
        height=height, margin=dict(l=10, r=10, t=35, b=20),
        font=dict(family=SYSTEM_FONT, color=NAVY, size=12),
        paper_bgcolor=WHITE, plot_bgcolor=WHITE,
    )
    return figure


def create_evidence_heatmap(frame):
    values = frame[EVIDENCE_LABELS].astype(int).values
    figure = go.Figure(go.Heatmap(
        z=values, x=EVIDENCE_LABELS, y=frame["Indication"].tolist(),
        zmin=0, zmax=1, colorscale=[[0, LIGHT], [1, PALE_BLUE]],
        showscale=False, xgap=3, ygap=3,
        hovertemplate="%{y}<br>%{x}: %{z} (synthetic flag)<extra></extra>",
    ))
    for row_number, row in enumerate(values):
        for column_number, value in enumerate(row):
            figure.add_annotation(
                x=EVIDENCE_LABELS[column_number], y=frame["Indication"].iloc[row_number],
                text="●" if value else "○", showarrow=False,
                font=dict(size=17, color=BLUE if value else SLATE, family=SYSTEM_FONT),
            )
    figure.update_xaxes(side="top")
    figure.update_yaxes(autorange="reversed")
    return chart_layout(figure, max(300, len(frame) * 33 + 100))


def create_sankey_diagram(indications):
    sources, targets, values = [], [], []
    for number, (_, row) in enumerate(indications.iterrows()):
        for source, column in enumerate(EVIDENCE_COLUMNS):
            if row[column]:
                sources.append(source)
                targets.append(len(EVIDENCE_COLUMNS) + number)
                values.append(1)
    figure = go.Figure(go.Sankey(
        node=dict(
            pad=20, thickness=22, line=dict(color=WHITE, width=1),
            label=EVIDENCE_LABELS + indications["indication"].tolist(),
            color=[SLATE] * len(EVIDENCE_COLUMNS) + [TIER_COLOURS[tier] for tier in indications["tier"]],
        ),
        link=dict(source=sources, target=targets, value=values, color="rgba(59,130,160,0.22)"),
    ))
    return chart_layout(figure, max(440, len(indications) * 45))


def create_tier_distribution_chart(indications):
    counts = indications["tier"].value_counts().reindex(["I", "II", "III"], fill_value=0)
    figure = go.Figure(go.Pie(
        labels=[f"Tier {tier}" for tier in counts.index], values=counts.tolist(), hole=0.6,
        marker=dict(colors=[TIER_COLOURS[tier] for tier in counts.index]),
        textinfo="label+value", textposition="outside",
    ))
    figure.update_layout(
        showlegend=False,
        annotations=[dict(text=f"<b>{len(indications)}</b><br>Indications", x=0.5, y=0.5, showarrow=False)],
    )
    return chart_layout(figure, 320)


def page_overview():
    config = st.session_state.config
    render_header(APP_TITLE, "Explore an illustrative repurposing workflow using included example data.")
    left, right = st.columns([2, 1])
    with left:
        section_header("Fictional development scenario", "compound")
        st.markdown(
            "A hypothetical development team is reviewing a discontinued small molecule programme "
            "and considering alternative indications. The demonstration shows how evidence availability "
            "could be organised into a shortlist and a set of questions for further research."
        )
        render_asset_details(config["compound"])
        st.caption(
            "DEMO-001, DEMO-002 and DEMO-003 share the same ten-row evidence fixture. "
            "Changing the compound changes the scenario label, not the underlying example associations."
        )
    with right:
        section_header("Included example data", "data")
        for label in DATA_OPTIONS.values():
            st.markdown(f"- {label}")
        st.markdown(
            "These are availability switches for the included synthetic flags. "
            "The application contains no patient data, raw omics files or clinical study results."
        )
    section_header("Demonstration workflow", "network")
    overview_steps = [
        ("compound", "1. Configure asset", "Choose a fictional compound and evidence filters"),
        ("data", "2. Run analysis", "Step through six simulated analysis stages"),
        ("chart", "3. View ranked results", "Compare the included evidence categories"),
        ("search", "4. Explore deep-dive", "Inspect coverage, gaps and validation questions"),
    ]
    for column, step in zip(st.columns(4), overview_steps):
        with column:
            st.markdown(render_workflow_step(*step), unsafe_allow_html=True)
    st.markdown("### How the example score works")
    st.markdown(
        "Each available evidence category contributes one point, up to six points per indication. "
        "Tier I contains five or six categories, Tier II contains four, and Tier III contains three or fewer. "
        "Category counts do not measure evidence quality, independence, effect direction or the probability "
        "of clinical success. The minimum category threshold and selected filters determine the displayed shortlist."
    )
    if st.button("Configure Asset", type="primary"):
        st.session_state.page = "asset"
        st.rerun()


def page_asset_input():
    current = deepcopy(st.session_state.config)
    render_header("Asset Configuration", "Configure the fictional programme and the included evidence flags.", "compound")
    left, right = st.columns(2)
    with left:
        section_header("Compound information", "compound")
        compound = st.selectbox(
            "Select Compound", list(COMPOUNDS), index=list(COMPOUNDS).index(current["compound"]),
            key="input_compound", help="All three fictional compounds use the same illustrative evidence fixture.",
        )
        render_asset_details(compound)
        section_header("Available example data", "data")
        selected_data = {}
        data_columns = st.columns(2)
        for index, (key, label) in enumerate(DATA_OPTIONS.items()):
            with data_columns[index % 2]:
                selected_data[key] = st.checkbox(label, value=current["data_options"][key], key=f"input_{key}")
        st.caption(
            "At least one molecular data option enables the shared omics category. "
            "The clinical option enables clinical trial flags. These switches do not load or process raw data."
        )
    with right:
        section_header("Analysis parameters", "network")
        strategy = st.selectbox(
            "Review perspective", STRATEGIES, index=STRATEGIES.index(current["strategy"]),
            key="input_strategy", help="Changes the review questions. All perspectives use the same category-count scoring rule.",
        )
        areas = st.multiselect(
            "Therapeutic Area Focus", THERAPEUTIC_AREAS, default=current["therapeutic_areas"], key="input_areas",
            help="All therapeutic areas overrides individual selections. Areas with no example rows return an empty shortlist.",
        )
        threshold = st.selectbox(
            "Minimum Evidence Categories", [2, 3, 4, 5], index=[2, 3, 4, 5].index(current["evidence_threshold"]),
            format_func=lambda number: f"At least {number} categories", key="input_threshold",
            help="The score counts available synthetic categories, without assessing evidence quality or clinical confidence.",
        )
        include_rare = st.checkbox("Include rare disease examples", value=current["include_rare"], key="input_rare")
        st.markdown("**Additional review questions**")
        review_paediatric = st.checkbox("Include a paediatric development review", value=current["review_paediatric"], key="input_paediatric")
        review_competition = st.checkbox("Include a competitive landscape review", value=current["review_competition"], key="input_competition")
        st.caption("These two review options add questions to the deep-dive. No paediatric or competitor datasets are included.")
    st.session_state.config = {
        "compound": compound, "strategy": strategy, "therapeutic_areas": areas,
        "evidence_threshold": threshold, "data_options": selected_data, "include_rare": include_rare,
        "review_paediatric": review_paediatric, "review_competition": review_competition,
    }
    preview = get_results(st.session_state.config)
    st.markdown(
        f'<div class="info-box"><strong>Configuration:</strong> {escape(compound)} | '
        f'{escape(strategy)} | minimum {threshold} categories | {sum(selected_data.values())} data options | '
        f'{len(preview)} example indications meet the filters.</div>', unsafe_allow_html=True,
    )
    if not areas:
        st.info("Select at least one therapeutic area to include example indications.")
    if st.button("Run Analysis", type="primary"):
        st.session_state.analysis_step = 0
        st.session_state.page = "analysis"
        st.rerun()


def page_analysis():
    config = st.session_state.config
    compound = config["compound"]
    asset = COMPOUNDS[compound]
    configured = configured_evidence(config)
    candidates = filter_indications(configured, config, apply_threshold=False)
    results = get_results(config)
    step = st.session_state.analysis_step
    render_header("Simulated Analysis", f"Six-stage walkthrough for {compound}; all counts come from the included fixture.", "data")
    for number, (column, definition) in enumerate(zip(st.columns(6), WORKFLOW_STEPS)):
        with column:
            status = "complete" if number < step else "active" if number == step else "pending"
            st.markdown(render_workflow_step(*definition, status), unsafe_allow_html=True)
    st.progress((step + 1) / len(WORKFLOW_STEPS), text=f"Stage {step + 1} of {len(WORKFLOW_STEPS)}")
    section_header(WORKFLOW_STEPS[step][1], WORKFLOW_STEPS[step][0])
    if step == 0:
        values = [("Compound", compound), ("Fictional target", asset["target"]),
                  ("Data options", sum(config["data_options"].values())), ("Example indications", len(configured))]
        for column, (label, value) in zip(st.columns(4), values):
            column.metric(label, value)
        st.write("The selected compound identifies the scenario. The same synthetic evidence matrix is used for all three compounds.")
    elif step == 1:
        st.write("The fixture covers six evidence categories. Each flag represents the presence of an illustrative record.")
        columns = st.columns(3)
        for number, (key, label, icon, description) in enumerate(EVIDENCE):
            with columns[number % 3]:
                st.markdown(render_metric_card(label, int(configured[key].sum()), "Included indication flags", icon), unsafe_allow_html=True)
                st.caption(description)
    elif step == 2:
        values = [("Included indications", len(configured)), ("After area and rare filters", len(candidates)),
                  ("Meeting category threshold", len(results))]
        for column, (label, value) in zip(st.columns(3), values):
            column.metric(label, value)
        st.write("The shortlist applies the selected therapeutic areas, rare disease option and minimum category count to the fixture.")
    elif step == 3:
        for column, score in zip(st.columns(3), [6, 5, 4]):
            column.metric(f"{score}-category examples", int((candidates["score"] == score).sum()))
        score_counts = candidates["score"].value_counts().reindex(range(6, -1, -1), fill_value=0)
        st.dataframe(pd.DataFrame({"Available categories": score_counts.index, "Example indications": score_counts.values}), hide_index=True)
        st.caption("Each available category contributes one point. Correlation between categories and the direction or quality of evidence are not assessed.")
    elif step == 4:
        for column, (key, label) in zip(st.columns(4), DATA_OPTIONS.items()):
            column.metric(label, "Included" if config["data_options"][key] else "Excluded")
        st.write(
            f"{int(configured['omics'].sum())} of {len(configured)} included indications retain an omics flag; "
            f"{int(results['omics'].sum())} appear in the filtered shortlist. "
            "The molecular options share one category and are not counted as independent sources."
        )
        st.caption("This stage illustrates data availability. It performs no molecular feature extraction, enrichment analysis or patient-data processing.")
    elif step == 5:
        for column, tier in zip(st.columns(3), ["I", "II", "III"]):
            with column:
                st.markdown(render_tier_badge(tier), unsafe_allow_html=True)
                st.metric("Example indications", int((results["tier"] == tier).sum()))
        st.write(f"{len(results)} indications meet the current configuration for {compound}.")
        st.caption("The tiers describe synthetic category coverage. Every hypothetical programme requires evidence assessment and experimental validation.")
    left, _, right = st.columns(3)
    with left:
        if step > 0 and st.button("Previous Step", use_container_width=True):
            st.session_state.analysis_step -= 1
            st.rerun()
    with right:
        if step < len(WORKFLOW_STEPS) - 1:
            if st.button("Next Step", type="primary", use_container_width=True):
                st.session_state.analysis_step += 1
                st.rerun()
        elif st.button("View Results", type="primary", use_container_width=True):
            st.session_state.page = "results"
            st.rerun()


def review_questions(config, row):
    perspective_questions = {
        "Drug-centric": "Review compound exposure, selectivity and the reasons the hypothetical original programme was discontinued.",
        "Target-centric": "Verify target expression, disease relevance and the direction of modulation needed for the proposed indication.",
        "Disease-centric": "Define the unmet need, patient population and endpoints against which the hypothesis would be assessed.",
        "Combined review": "Compare compound properties, target biology and disease requirements before proposing a development path.",
    }
    questions = [
        perspective_questions[config["strategy"]], row["validation_focus"],
        "Retrieve and assess primary evidence, including contradictory results and potential overlap between sources.",
        "Design a proof-of-concept study with an appropriate disease model, controls and predefined decision criteria.",
        "Assess intellectual property, freedom to operate and regulatory requirements with the relevant specialists.",
    ]
    if config["review_paediatric"]:
        questions.append("Assess whether a paediatric programme is justified, including age-specific biology, exposure and ethical requirements.")
    if config["review_competition"]:
        questions.append("Review current treatment options and competing programmes, using verified sources beyond this demonstration.")
    return questions


def render_deep_dive(indications, config):
    section_header("Indication Deep-Dive", "search")
    selected = st.selectbox("Select indication for detailed view", indications["indication"].tolist(), key="detail_indication")
    row = indications.loc[indications["indication"] == selected].iloc[0]
    left, right = st.columns([2, 1])
    with left:
        st.markdown(
            f'<div class="detail-card"><h3>{escape(selected)}</h3>'
            f'<p><strong>Disease category:</strong> {escape(row["disease_category"])}</p>'
            f'<p><strong>Evidence status:</strong> {escape(row["evidence_status"])}</p>'
            f'<p><strong>Category coverage:</strong> {escape(row["coverage"])}</p>'
            f'<h4>Hypothetical scientific rationale</h4><p>{escape(row["rationale"])}</p></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(render_tier_badge(row["tier"]), unsafe_allow_html=True)
        st.markdown(render_metric_card("Available categories", f"{row['score']}/6", "Synthetic flags; no clinical confidence estimate", "chart"), unsafe_allow_html=True)
        st.caption(f"Scenario: {config['compound']} | {config['strategy']}")
    section_header("Evidence breakdown", "matrix")
    for column, (key, label, icon, _) in zip(st.columns(6), EVIDENCE):
        with column:
            present = bool(row[key])
            status = "Included flag" if present else "No included flag"
            st.markdown(
                f'<div class="evidence-card" style="background:{PALE_BLUE if present else LIGHT}">'
                f'{icon_html(icon, 30)}<p><strong>{escape(label)}</strong></p><p>{status}</p></div>',
                unsafe_allow_html=True,
            )
    st.markdown("#### Interpretation of the example flags")
    for key, label, _, description in EVIDENCE:
        state = "Included" if row[key] else "Absent or excluded by configuration"
        with st.expander(f"{label}: {state}"):
            st.write(description)
            if not row[key]:
                st.write("An absent flag indicates a gap in this fixture. It does not demonstrate an absence of evidence in the scientific literature.")
    section_header("Questions for further research", "search")
    for number, question in enumerate(review_questions(config, row), start=1):
        st.markdown(f"{number}. {question}")


def render_downloads(indications, config):
    """Keep chart export available and provide a labelled copy of the displayed data."""
    st.markdown("### Download the configured example")
    export = indications.copy()
    export.insert(0, "compound", config["compound"])
    export.insert(1, "data_status", "synthetic demonstration")
    left, right = st.columns(2)
    with left:
        st.download_button(
            "Download results CSV", data=export.to_csv(index=False),
            file_name=f"{config['compound'].lower()}_synthetic_indications.csv", mime="text/csv",
        )
    with right:
        payload = {
            "title": APP_TITLE, "data_status": SYNTHETIC_NOTICE,
            "configuration": config,
            "scoring": "One point per available synthetic evidence category; Tier I: 5-6, Tier II: 4, Tier III: 0-3.",
            "results": json.loads(export.to_json(orient="records")),
        }
        st.download_button(
            "Download configuration and results JSON", data=json.dumps(payload, indent=2, ensure_ascii=False),
            file_name=f"{config['compound'].lower()}_synthetic_review.json", mime="application/json",
        )
    st.caption("Downloads contain the current configured shortlist. The tier selector changes only the ranked-indications view. Charts also retain their image-download controls.")


def page_results():
    config = st.session_state.config
    indications = get_results(config)
    render_header("Repurposing Results Dashboard", f"Illustrative indication shortlist for {config['compound']}.", "chart")
    lead = indications.iloc[0] if not indications.empty else None
    metrics = [
        ("Total indications", len(indications), "Meet the current filters", "data"),
        ("Tier I", int((indications["tier"] == "I").sum()), "Five or six available categories", "target"),
        ("Tier II", int((indications["tier"] == "II").sum()), "Four available categories", "chart"),
        ("Top example", lead["indication"] if lead is not None else "No matches",
         f"{int(lead['score'])}/6 categories" if lead is not None else "Adjust the configuration", "search"),
    ]
    for column, metric in zip(st.columns(4), metrics):
        with column:
            st.markdown(render_metric_card(*metric), unsafe_allow_html=True)
    st.caption(
        f"{config['strategy']} | minimum {config['evidence_threshold']} categories | "
        f"areas: {', '.join(config['therapeutic_areas']) or 'none selected'}. "
        "Ties retain the fixture order and do not imply a preference between equally scored indications."
    )
    if indications.empty:
        st.info("No example indications meet the current filters. Adjust the therapeutic area, evidence threshold or available data options.")
        if st.button("Edit Configuration"):
            st.session_state.page = "asset"
            st.rerun()
        render_downloads(indications, config)
        return
    ranking, heatmap, flow, details = st.tabs([
        "Ranked Indications", "Evidence Heatmap", "Evidence Flow", "Indication Deep-Dive",
    ])
    with ranking:
        section_header("Tiered Indication Ranking", "chart")
        st.caption("Scores count available synthetic categories. Coverage labels describe quantity and do not assess scientific confidence.")
        tier_filter = st.selectbox("Filter by Tier", ["All Tiers", "Tier I", "Tier II", "Tier III"], key="tier_filter")
        ranked = indications if tier_filter == "All Tiers" else indications.loc[indications["tier"] == tier_filter.split()[-1]]
        if ranked.empty:
            st.info("There are no indications in this tier for the current configuration.")
        for _, row in ranked.iterrows():
            columns = st.columns([0.5, 2, 1, 1.5, 1.2, 3])
            with columns[0]:
                st.markdown(f'<div class="score-box" style="background:{TIER_COLOURS[row["tier"]]}">{row["score"]}</div>', unsafe_allow_html=True)
            with columns[1]:
                st.markdown(f"**{row['indication']}**")
                st.caption(row["disease_category"])
            with columns[2]:
                st.markdown(render_tier_badge(row["tier"]), unsafe_allow_html=True)
            with columns[3]:
                st.caption(row["evidence_status"])
            with columns[4]:
                st.caption(row["coverage"])
            with columns[5]:
                st.caption(row["rationale"])
            st.divider()
    with heatmap:
        section_header("Evidence Matrix", "matrix")
        st.write("Filled circles show an included synthetic category. Open circles show an absent or excluded flag.")
        st.plotly_chart(create_evidence_heatmap(evidence_matrix(indications)), use_container_width=True)
        for column, (_, label, icon, _) in zip(st.columns(6), EVIDENCE):
            with column:
                st.markdown(f'{icon_html(icon, 22)} {escape(label)}', unsafe_allow_html=True)
        st.caption("Presence records availability only; it does not establish a favourable outcome or an independent source of support.")
    with flow:
        section_header("Evidence Flow Diagram", "network")
        st.write("Each link connects one available synthetic evidence category to an example indication.")
        left, right = st.columns([3, 1])
        with left:
            st.plotly_chart(create_sankey_diagram(indications), use_container_width=True)
        with right:
            section_header("Tier Distribution", "chart")
            st.plotly_chart(create_tier_distribution_chart(indications), use_container_width=True)
    with details:
        render_deep_dive(indications, config)
    render_downloads(indications, config)


def render_sidebar():
    with st.sidebar:
        st.markdown(f'### {APP_TITLE}')
        st.caption("Interactive synthetic example")
        st.divider()
        for label, page in [
            ("Overview", "overview"), ("Asset Configuration", "asset"),
            ("Run Analysis", "analysis"), ("Results Dashboard", "results"),
        ]:
            if st.button(label, key=f"nav_{page}", use_container_width=True):
                if page == "analysis":
                    st.session_state.analysis_step = 0
                st.session_state.page = page
                st.rerun()
        st.divider()
        st.markdown("**Current scenario**")
        st.write(f"{st.session_state.config['compound']} (fictional)")
        st.caption("All three scenarios share the included ten-row evidence fixture.")
        st.caption("The demonstration performs no validated biological analysis and contains no patient or client data.")


def main():
    if "page" not in st.session_state:
        st.session_state.page = "overview"
    if "analysis_step" not in st.session_state:
        st.session_state.analysis_step = 0
    if "config" not in st.session_state:
        st.session_state.config = deepcopy(DEFAULT_CONFIG)
    render_sidebar()
    pages = {"overview": page_overview, "asset": page_asset_input, "analysis": page_analysis, "results": page_results}
    pages.get(st.session_state.page, page_overview)()


if __name__ == "__main__":
    main()
