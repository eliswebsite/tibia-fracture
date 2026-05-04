Precision Tibia Case Matcher

A clinical decision support tool for orthopaedic surgeons evaluating tibia fracture treatment options. Built with Streamlit and powered by a Supabase patient database.

---

How It Works

The tool takes six inputs from the treating clinician — patient age, AP angulation, growth plate width, weight, refracture history, and infection history — and runs them against a database of historical tibia fracture cases to find the five most clinically similar patients.

Similarity is calculated using a weighted Euclidean distance formula. Each feature is first normalized by its standard deviation across the dataset, which ensures that a large-range variable like weight does not mathematically dominate a clinically critical but numerically small variable like AP angulation. Once normalized, each feature is multiplied by a clinical priority weight before the distance is computed. AP angulation carries the highest weight (5.0), followed by infection history (4.0), growth plate width (3.0), and age and weight (1.5 each). For patients over 18, growth plate width is automatically excluded from the calculation entirely, as fused growth plates carry no clinical relevance in adult fracture management.

A maximum distance threshold is enforced so that only genuinely similar cases contribute to the success rate. If no cases fall within this threshold, the tool returns no result rather than surfacing misleading matches.

This matching process runs independently for all six treatment types. The output includes a ranked success rate table, a treatment recommendation with a confidence tier, a patient universe scatter plot showing where the current patient sits relative to all historical cases for the selected treatment, and a radar chart comparing success rates across all treatment options simultaneously.

Stack

- **Frontend & logic** — Streamlit (Python)
- **Database** — Supabase (PostgreSQL)
- **Visualisation** — Plotly
- **Data processing** — Pandas, NumPy

Setup

```bash
pip install streamlit pandas numpy supabase plotly
streamlit run dashboard.py
```

Requires a Supabase project with a `tibia_fractures1` table containing the following columns: `patient_id`, `age`, `ap_angulation`, `growth_plates`, `infection_history`, `weight_kg`, `treatment_type`, `refracture`, `success`.
