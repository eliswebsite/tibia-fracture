import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client
import plotly.graph_objects as go

# 1. DATABASE CONNECTION
URL = "https://sojkgoaefkgtnxmhkptz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvamtnb2FlZmtndG54bWhrcHR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MTYxMjIsImV4cCI6MjA5MDE5MjEyMn0.Ev1EmLOpdcVzj6Jcpsuv9m7z_3ybYowodU2yc7abpyQ"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Ortho Decision Support Pro", layout="wide")
st.title("🏥 Precision Tibia Case Matcher")

WEIGHTS = {
    'ap_angulation':     5.0,
    'infection_history': 4.0,
    'growth_plates':     3.0,
    'age':               2.0,
    'weight_kg':         1.5,
}

TREATMENT_KEYWORDS = {
    "Cast":              "cast",
    "ORIF":              "orif",
    "Nail":              "nail",
    "External Fixation": "external",
    "K-Wire":            "k-wire",
    "Closed Reduction":  "closed",
}

def get_suggestion(success_rate, treatment):
    if success_rate >= 80:
        return ("✅ **Strong Recommendation**",
                f"{success_rate}% of similar cases treated with **{treatment}** were successful. "
                f"Historical data strongly supports this treatment plan for this patient profile.")
    elif success_rate >= 60:
        return ("🟡 **Proceed with Caution**",
                f"{success_rate}% of similar cases treated with **{treatment}** were successful. "
                f"This treatment may be appropriate, but consider reviewing case differences carefully.")
    elif success_rate >= 40:
        return ("⚠️ **Low Confidence — Review Alternatives**",
                f"Only {success_rate}% of similar cases treated with **{treatment}** were successful. "
                f"Consider consulting additional clinical factors or exploring alternative treatments.")
    else:
        return ("🚨 **Not Recommended Based on Similar Cases**",
                f"Only {success_rate}% of similar cases treated with **{treatment}** were successful. "
                f"Historical data suggests this treatment has poor outcomes for this patient profile. "
                f"Alternative treatments are strongly advised.")

def std_diff(col_vals, input_val):
    std = col_vals.std()
    if std == 0:
        return pd.Series(np.zeros(len(col_vals)), index=col_vals.index)
    return ((col_vals - input_val) / std) ** 2

def compute_success_rate(df, keyword, in_age, in_angle, in_growth, in_weight, in_refracture, in_infection):
    db_col = df['treatment_type'].astype(str).str.strip().str.lower()
    subset = df[db_col.str.contains(keyword, na=False)].copy()
    if subset.empty:
        return None, None

    num_cols = ['age', 'ap_angulation', 'growth_plates', 'weight_kg']
    for col in num_cols:
        subset[col] = pd.to_numeric(subset[col], errors='coerce')
    subset = subset.dropna(subset=['age', 'ap_angulation'])
    if subset.empty:
        return None, None

    subset['growth_plates'] = subset['growth_plates'].fillna(subset['growth_plates'].median())
    subset['weight_kg']     = subset['weight_kg'].fillna(subset['weight_kg'].median())
    subset['inf_val'] = subset['infection_history'].map({True: 1, False: 0, 1: 1, 0: 0}).fillna(0)

    # Growth plate contribution:
    # If INPUT patient is over 18, growth plates are clinically irrelevant — weight = 0.
    # Also zero out growth plate contribution for DB rows where age > 18.
    if in_age > 18:
        growth_contribution = pd.Series(np.zeros(len(subset)), index=subset.index)
    else:
        # For rows in DB where age > 18, also ignore growth plates
        growth_contribution = std_diff(subset['growth_plates'], in_growth) * WEIGHTS['growth_plates']
        adult_mask = subset['age'] > 18
        growth_contribution[adult_mask] = 0

    subset['distance'] = np.sqrt(
        WEIGHTS['ap_angulation']     * std_diff(subset['ap_angulation'], in_angle) +
        WEIGHTS['infection_history'] * (subset['inf_val'] - (1 if in_infection else 0))**2 +
        growth_contribution +
        WEIGHTS['age']               * std_diff(subset['age'], in_age) +
        WEIGHTS['weight_kg']         * std_diff(subset['weight_kg'], in_weight)
    )

    MAX_DISTANCE = 2.0
    close_matches = subset[subset['distance'] <= MAX_DISTANCE].sort_values('distance', ascending=True).head(5)
    if close_matches.empty:
        return None, None

    success_rate = int((close_matches['success'].sum() / len(close_matches)) * 100)
    return success_rate, close_matches

def build_radar(treatment_rates):
    labels = list(treatment_rates.keys())
    values = [treatment_rates[t] if treatment_rates[t] is not None else 0 for t in labels]
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]

    avg = np.mean([v for v in values if v > 0])
    if avg >= 70:
        fill_color = 'rgba(29, 158, 117, 0.35)'
        line_color = '#1d9e75'
    elif avg >= 45:
        fill_color = 'rgba(186, 117, 23, 0.35)'
        line_color = '#ba7517'
    else:
        fill_color = 'rgba(162, 45, 45, 0.35)'
        line_color = '#a32d2d'

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=labels_closed,
        fill='toself',
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5),
        marker=dict(size=7, color=line_color),
        hovertemplate='<b>%{theta}</b><br>Success Rate: %{r}%<extra></extra>',
        name='Success Rate',
    ))
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=['20%', '40%', '60%', '80%', '100%'],
                tickfont=dict(size=10, color='rgba(255,255,255,0.45)'),
                gridcolor='rgba(255,255,255,0.08)',
                linecolor='rgba(255,255,255,0.1)',
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color='white'),
                linecolor='rgba(255,255,255,0.15)',
                gridcolor='rgba(255,255,255,0.08)',
            ),
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=520,
        margin=dict(t=40, b=40, l=80, r=80),
        dragmode=False,
    )
    config = dict(displayModeBar=False, staticPlot=True)
    return fig, config

def build_scatter(df, in_age, in_angle, in_treatment, keyword):
    db_col = df['treatment_type'].astype(str).str.strip().str.lower()
    subset = df[db_col.str.contains(keyword, na=False)].copy()
    subset['age']           = pd.to_numeric(subset['age'], errors='coerce')
    subset['ap_angulation'] = pd.to_numeric(subset['ap_angulation'], errors='coerce')
    subset['success']       = pd.to_numeric(subset['success'], errors='coerce')
    subset = subset.dropna(subset=['age', 'ap_angulation', 'success'])

    successes = subset[subset['success'] == 1]
    failures  = subset[subset['success'] == 0]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=failures['age'], y=failures['ap_angulation'],
        mode='markers',
        marker=dict(color='#e24b4a', size=9, opacity=0.75, line=dict(color='#a32d2d', width=0.5)),
        name='Failed',
        hovertemplate='Age: %{x}<br>Angulation: %{y}°<br>Outcome: Failed<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=successes['age'], y=successes['ap_angulation'],
        mode='markers',
        marker=dict(color='#1d9e75', size=9, opacity=0.75, line=dict(color='#0f6e56', width=0.5)),
        name='Success',
        hovertemplate='Age: %{x}<br>Angulation: %{y}°<br>Outcome: Success<extra></extra>',
    ))
    fig.add_trace(go.Scatter(
        x=[in_age], y=[in_angle],
        mode='markers',
        marker=dict(symbol='star', color='white', size=18, line=dict(color='#333', width=1.5)),
        name='Your Patient',
        hovertemplate=f'<b>Your Patient</b><br>Age: {in_age}<br>Angulation: {in_angle}°<extra></extra>',
    ))
    fig.update_layout(
        xaxis=dict(title='Age', gridcolor='rgba(255,255,255,0.07)', zerolinecolor='rgba(255,255,255,0.1)'),
        yaxis=dict(title='AP Angulation (°)', gridcolor='rgba(255,255,255,0.07)', zerolinecolor='rgba(255,255,255,0.1)'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(color='white')),
        height=420,
        margin=dict(t=20, b=40, l=50, r=20),
        dragmode=False,
    )
    return fig, dict(displayModeBar=False)

# 2. SIDEBAR INPUTS
st.sidebar.header("Detailed Patient Profile")
in_age        = st.sidebar.slider("Patient Age", 1, 80, 14)
in_angle      = st.sidebar.slider("AP Angulation (Degrees)", 0.0, 20.0, 13.0, step=0.1)
in_growth     = st.sidebar.slider("Growth Plate Width (mm)", 0.0, 10.0, 3.0, step=0.1)
in_weight     = st.sidebar.slider("Weight (kg)", 5, 150, 60)
in_refracture = st.sidebar.checkbox("Refracture History?")
in_infection  = st.sidebar.checkbox("Previous Infection History?")
in_treatment  = st.sidebar.selectbox("Proposed Treatment Plan", list(TREATMENT_KEYWORDS.keys()))

# Show note if growth plates are being ignored
if in_age > 18:
    st.sidebar.info("ℹ️ Growth plate width is not factored into matching for patients over 18.")

# 3. MAIN LOGIC
if st.sidebar.button("Analyze Similar Cases"):
    try:
        response = supabase.table("tibia_fractures1").select("*").execute()
        df = pd.DataFrame(response.data)

        if df.empty:
            st.error("No data found.")
        else:
            df.columns = df.columns.str.strip().str.lower()

            # ── SECTION A: PROPOSED TREATMENT ───────────────────────────────
            st.header(f"Proposed Treatment: {in_treatment}")

            proposed_rate, proposed_matches = compute_success_rate(
                df, TREATMENT_KEYWORDS[in_treatment],
                in_age, in_angle, in_growth, in_weight, in_refracture, in_infection
            )

            if proposed_matches is None:
                st.warning(f"⚠️ No sufficiently similar historical cases found for **{in_treatment}** with this patient profile.")
            else:
                proposed_matches_display = proposed_matches.set_index('patient_id')
                st.subheader("Top 5 Most Similar Cases")
                st.dataframe(
                    proposed_matches_display[['age', 'ap_angulation', 'growth_plates', 'weight_kg', 'refracture', 'success']],
                    use_container_width=True
                )
                st.metric("Success Rate", f"{proposed_rate}%")
                label, message = get_suggestion(proposed_rate, in_treatment)
                st.markdown(f"### {label}")
                st.info(message)

                st.subheader("🔭 Patient Universe")
                st.caption("All historical cases for this treatment. 🟢 Green = success, 🔴 Red = failed, ⭐ White star = your patient.")
                scatter_fig, scatter_config = build_scatter(df, in_age, in_angle, in_treatment, TREATMENT_KEYWORDS[in_treatment])
                st.plotly_chart(scatter_fig, use_container_width=True, config=scatter_config)

            st.divider()

            # ── SECTION B: ALL TREATMENTS COMPARISON ────────────────────────
            st.header("📊 Treatment Comparison — All Options")
            st.caption("Success rate based on genuinely similar cases only.")

            treatment_rates = {}
            results = []
            for treatment_name, keyword in TREATMENT_KEYWORDS.items():
                rate, _ = compute_success_rate(
                    df, keyword,
                    in_age, in_angle, in_growth, in_weight, in_refracture, in_infection
                )
                treatment_rates[treatment_name] = rate
                results.append({
                    "Treatment":    treatment_name,
                    "Success Rate": f"{rate}%" if rate is not None else "No similar cases",
                    "Proposed":     "⭐ Proposed" if treatment_name == in_treatment else "",
                })

            results_df = pd.DataFrame(results)
            results_df['_sort'] = pd.to_numeric(
                results_df['Success Rate'].str.replace('%', '', regex=False), errors='coerce'
            )
            results_df = results_df.sort_values('_sort', ascending=False).drop(columns='_sort').reset_index(drop=True)
            results_df.index += 1

            numeric_results = [(r['Treatment'], int(r['Success Rate'].replace('%', '')))
                               for r in results if isinstance(r['Success Rate'], str) and '%' in r['Success Rate']]
            if numeric_results:
                best_treatment, best_rate = max(numeric_results, key=lambda x: x[1])
                if best_treatment != in_treatment:
                    proposed_str = f"{proposed_rate}%" if proposed_rate is not None else "no similar cases"
                    st.success(f"🏆 **Recommended Treatment: {best_treatment}** — {best_rate}% success rate, outperforming the proposed {in_treatment} ({proposed_str}).")
                else:
                    st.success(f"🏆 **The proposed treatment ({in_treatment}) is already the best option** with a {best_rate}% success rate.")
            else:
                st.warning("⚠️ No treatments found with sufficiently similar historical cases for this patient profile.")

            st.dataframe(results_df[['Treatment', 'Success Rate', 'Proposed']], use_container_width=True)

            st.divider()

            # ── SECTION C: RADAR CHART ───────────────────────────────────────
            st.header("🕸️ Treatment Success Radar")
            st.caption("Each axis = a treatment type. Further from center = higher success rate for this patient profile.")
            fig, config = build_radar(treatment_rates)
            st.plotly_chart(fig, use_container_width=True, config=config)

    except Exception as e:
        st.error(f"Error: {e}")