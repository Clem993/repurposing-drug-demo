# Excelra Indication Expansion & Drug Repurposing Demo

Interactive sales demonstration tool showcasing the GRIP-powered drug repurposing workflow.

## Overview

This Streamlit application demonstrates Excelra's Indication Expansion and Drug Repurposing service capabilities through an interactive workflow simulation. It showcases how GRIP (Global Repository of Integrated Phenotypes) technology identifies new therapeutic applications for shelved pharmaceutical assets.

### Demo Case
**Shelved Phase II Asset** - A Japanese large pharma compound (EXC-7842/Somnolexin) that failed Phase II trials for sleep disorders. The demo shows how multi-omics data can be leveraged to identify alternative indications and recover R&D investment.

## Features

- **Overview Page**: Introduction to the demo case and workflow preview
- **Asset Configuration**: Interactive compound and analysis parameter selection
- **GRIP Analysis**: Step-by-step workflow progression through 6 analysis stages
- **Results Dashboard**: Tiered indication ranking, evidence heatmap, Sankey diagram, and deep-dive analysis

## Deploying to Streamlit Cloud

### Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click **New repository** (green button)
3. Name it (e.g., `excelra-repurposing-demo`)
4. Set to **Private** (recommended for internal tools)
5. Click **Create repository**

### Step 2: Upload Files

Upload all files from this package to your repository. You can either:

**Option A: Upload via GitHub web interface**
1. Click "uploading an existing file" on the empty repo page
2. Drag and drop all files
3. Click "Commit changes"

**Option B: Use Git command line**
```bash
git clone https://github.com/YOUR_USERNAME/excelra-repurposing-demo.git
cd excelra-repurposing-demo
# Copy all files from this package into the folder
git add .
git commit -m "Initial commit"
git push origin main
```

### Step 3: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Select:
   - Repository: `YOUR_USERNAME/excelra-repurposing-demo`
   - Branch: `main`
   - Main file path: `app.py`
5. Click **Deploy**

Your app will be live at: `https://YOUR-APP-NAME.streamlit.app`

### Step 4: Share with Colleagues

For private repositories:
1. Go to your GitHub repo → Settings → Collaborators
2. Add colleagues by their GitHub username
3. Share the Streamlit Cloud URL

## Required Files

```
excelra-repurposing-demo/
├── app.py                 # Main application
├── requirements.txt       # Dependencies
├── README.md             # This file
├── .gitignore            # Git ignore rules
├── .streamlit/
│   └── config.toml       # Theme configuration
└── assets/               # All PNG icons (see list below)
```

### Required Assets (PNG files)

Copy all these from your existing assets folder:
- Logo.png, Slogan.png, Wave.png
- repurpose.png, repurpose2.png, Start.png
- Input.png, Analysis.png, ranking.png, Home.png
- Novel.png, Clinical.png, adverse.png, books.png
- flow.png, metabolomic.png, Network.png
- Data acquisition.png, deep_dive.png, heatmap.png
- Bar_chart.png, Pie_chart.png, Gene.png
- total.png, tier1.png, tier2.png, lipidomimc.png

## Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

## Brand Colours

| Colour | Hex | Usage |
|--------|-----|-------|
| Deep Blue | #0A1E4A | Primary text |
| Violet | #A24DBE | Accents, Tier II |
| Magenta | #E04F8A | Primary accent, Tier I |
| Soft Lavender | #E3D9F2 | Backgrounds |

---

**© 2024 Excelra** | Where data means more
