# Indication Expansion & Drug Repurposing Demo

An interactive Streamlit demonstration of a drug repurposing workflow, from asset configuration to a prioritised indication shortlist. The application uses fictional compounds and a small, embedded dataset to illustrate how different evidence categories can be brought together for review.

## Demonstration scope

The starting scenario is a fictional shelved development asset. Users can select a demonstration compound, configure the workflow, move through six analysis stages and explore the results.

All compound profiles, evidence flags, scores and rationales are illustrative. The application does not query live databases, process uploaded research data or generate validated therapeutic predictions. The rankings support a demonstration of the interface and workflow; they are not clinical recommendations.

## Features

| Page | Function |
| --- | --- |
| Overview | Introduces the fictional case and previews the workflow. |
| Asset Configuration | Selects a demonstration compound and analysis settings. |
| Analysis | Steps through data ingestion, evidence review, association mapping, scoring, omics review and prioritisation. |
| Results Dashboard | Displays tiered indication rankings, an evidence heatmap, a Sankey diagram, tier distribution and an indication deep dive. |

The interface uses a neutral colour palette, system fonts and icons defined in the application. No separate image assets are required.

All three compound choices share the same ten-row evidence matrix. Configuration filters determine the displayed shortlist. CSV and JSON downloads include the configured results with explicit synthetic-data labels.

## Run locally

Use Python 3.12 and install the dependencies in a virtual environment:

```bash
git clone https://github.com/Clem993/repurposing-drug-demo.git
cd repurposing-drug-demo
python -m venv .venv
```

Activate the environment on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Then install and start the application:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

No API keys or external database credentials are required.

## Deploy on Streamlit Community Cloud

Open [Streamlit Community Cloud](https://share.streamlit.io/), create an app and select the following GitHub settings:

| Setting | Value |
| --- | --- |
| Repository | `Clem993/repurposing-drug-demo` |
| Branch | `main` |
| Entrypoint file | `app.py` |
| Python version | `3.12` |

If you fork the repository, use your fork's owner and repository name. Review the app's sharing settings before distributing its URL. See the [official deployment guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) for the current deployment steps.

## Repository files

| File | Purpose |
| --- | --- |
| `app.py` | Application, fictional sample data, charts and inline icons. |
| `requirements.txt` | Python dependencies. |
| `.streamlit/config.toml` | Neutral interface theme. |
| `.gitignore` | Excludes local environments, caches and secrets from commits. |
| `README.md` | Scope, setup and deployment instructions. |

## Working with the example data

The sample data is defined in `app.py`. Keep the fictional-data labelling visible when adapting the demonstration. Any connection to real data sources, scientific validation or production access controls requires separate implementation.
