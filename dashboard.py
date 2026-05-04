import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from supabase import create_client
import plotly.graph_objects as go
import os

URL = "https://sojkgoaefkgtnxmhkptz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvamtnb2FlZmtndG54bWhrcHR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MTYxMjIsImV4cCI6MjA5MDE5MjEyMn0.Ev1EmLOpdcVzj6Jcpsuv9m7z_3ybYowodU2yc7abpyQ"
supabase = create_client(URL, KEY)

# Sidebar collapsed on landing, expanded on app
sidebar_state = "collapsed" if st.session_state.get("page", "landing") == "landing" else "expanded"
st.set_page_config(page_title="Precision Tibia Case Matcher", layout="wide", initial_sidebar_state=sidebar_state)

if "page" not in st.session_state:
    st.session_state.page = "landing"

# ── LANDING ───────────────────────────────────────────────────────────────────
if st.session_state.page == "landing":

    st.markdown("""
    <style>
    #MainMenu, header, footer { display: none !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .main .block-container { padding-top: 0 !important; }
    [data-testid="stAppViewContainer"] { background: #FAFAF8 !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    div[data-testid="stButton"] { display: flex; justify-content: center; margin-top: 20px; margin-bottom: 40px; }
    div[data-testid="stButton"] > button {
        background: #111 !important; color: white !important;
        border: none !important; border-radius: 100px !important;
        padding: 18px 56px !important; font-size: 17px !important;
        font-weight: 500 !important; cursor: pointer !important;
    }
    div[data-testid="stButton"] > button:hover { background: #2563EB !important; }
    </style>
    """, unsafe_allow_html=True)

    html_path = os.path.join(os.path.dirname(__file__), "landing.html")
    with open(html_path, "r") as f:
        landing_html = f.read()

    components.html(landing_html, height=1900, scrolling=True)

    if st.button("🚀  Launch Tool  →", key="launch"):
        st.session_state.page = "app"
        st.rerun()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <style>
    #MainMenu, footer { display: none !important; }
    [data-testid="stAppViewContainer"] { background: #0d0d14; }
    [data-testid="stSidebar"] { background: #13131f; border-right: 1px solid #1e1e2e; }
    /* Prevent title from being clipped */
    .block-container { padding-top: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

    WEIGHTS = {
        'ap_angulation':     5.0,
        'infection_history': 4.0,
        'growth_plates':     3.0,
        'age':               1.5,
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
        for col in ['age', 'ap_angulation', 'growth_plates', 'weight_kg']:
            subset[col] = pd.to_numeric(subset[col], errors='coerce')
        subset = subset.dropna(subset=['age', 'ap_angulation'])
        if subset.empty:
            return None, None
        subset['growth_plates'] = subset['growth_plates'].fillna(subset['growth_plates'].median())
        subset['weight_kg']     = subset['weight_kg'].fillna(subset['weight_kg'].median())
        subset['inf_val'] = subset['infection_history'].map({True:1,False:0,1:1,0:0}).fillna(0)
        if in_age > 18:
            growth_contribution = pd.Series(np.zeros(len(subset)), index=subset.index)
        else:
            growth_contribution = std_diff(subset['growth_plates'], in_growth) * WEIGHTS['growth_plates']
            growth_contribution[subset['age'] > 18] = 0
        subset['distance'] = np.sqrt(
            WEIGHTS['ap_angulation']     * std_diff(subset['ap_angulation'], in_angle) +
            WEIGHTS['infection_history'] * (subset['inf_val'] - (1 if in_infection else 0))**2 +
            growth_contribution +
            WEIGHTS['age']               * std_diff(subset['age'], in_age) +
            WEIGHTS['weight_kg']         * std_diff(subset['weight_kg'], in_weight)
        )
        close = subset[subset['distance'] <= 2.0].sort_values('distance').head(5)
        if close.empty:
            return None, None
        return int((close['success'].sum() / len(close)) * 100), close

    def build_radar(treatment_rates):
        labels = list(treatment_rates.keys())
        values = [treatment_rates[t] if treatment_rates[t] is not None else 0 for t in labels]
        lc = labels + [labels[0]]
        vc = values + [values[0]]
        avg = np.mean([v for v in values if v > 0])
        if avg >= 70:   fc, lcolor = 'rgba(29,158,117,0.35)', '#1d9e75'
        elif avg >= 45: fc, lcolor = 'rgba(186,117,23,0.35)', '#ba7517'
        else:           fc, lcolor = 'rgba(162,45,45,0.35)',  '#a32d2d'
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=vc, theta=lc, fill='toself', fillcolor=fc,
            line=dict(color=lcolor, width=2.5), marker=dict(size=7, color=lcolor),
            hovertemplate='<b>%{theta}</b><br>Success Rate: %{r}%<extra></extra>'))
        fig.update_layout(
            polar=dict(bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0,100], tickvals=[20,40,60,80,100],
                    ticktext=['20%','40%','60%','80%','100%'],
                    tickfont=dict(size=10, color='rgba(255,255,255,0.45)'),
                    gridcolor='rgba(255,255,255,0.08)', linecolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(tickfont=dict(size=13, color='white'),
                    linecolor='rgba(255,255,255,0.15)', gridcolor='rgba(255,255,255,0.08)')),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=520, margin=dict(t=40,b=40,l=80,r=80), dragmode=False)
        return fig, dict(displayModeBar=False, staticPlot=True)

    def build_scatter(df, in_age, in_angle, keyword):
        np.random.seed(42)
        db_col = df['treatment_type'].astype(str).str.strip().str.lower()
        subset = df[db_col.str.contains(keyword, na=False)].copy()
        for col in ['age','ap_angulation','success']:
            subset[col] = pd.to_numeric(subset[col], errors='coerce')
        subset = subset.dropna(subset=['age','ap_angulation','success']).copy()
        subset['age_j']   = subset['age']           + np.random.uniform(-0.35,0.35,len(subset))
        subset['angle_j'] = subset['ap_angulation'] + np.random.uniform(-0.18,0.18,len(subset))
        s = subset[subset['success']==1]
        f = subset[subset['success']==0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=f['age_j'], y=f['angle_j'], mode='markers',
            marker=dict(color='#FF3333',size=8,opacity=0.85,line=dict(color='rgba(0,0,0,0.3)',width=0.5)),
            name='Failed', customdata=f[['age','ap_angulation']].values,
            hovertemplate='Age: %{customdata[0]}<br>Angulation: %{customdata[1]}°<br><b>Failed</b><extra></extra>'))
        fig.add_trace(go.Scatter(x=s['age_j'], y=s['angle_j'], mode='markers',
            marker=dict(color='#00E676',size=8,opacity=0.75,line=dict(color='rgba(0,0,0,0.3)',width=0.5)),
            name='Success', customdata=s[['age','ap_angulation']].values,
            hovertemplate='Age: %{customdata[0]}<br>Angulation: %{customdata[1]}°<br><b>Success</b><extra></extra>'))
        fig.add_trace(go.Scatter(x=[in_age], y=[in_angle], mode='markers',
            marker=dict(symbol='circle',color='rgba(255,255,255,0.18)',size=42,
                        line=dict(color='rgba(255,255,255,0.5)',width=1.5)),
            showlegend=False, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=[in_age], y=[in_angle], mode='markers',
            marker=dict(symbol='star',color='white',size=26,line=dict(color='#111',width=2)),
            name='Your Patient',
            hovertemplate=f'<b>Your Patient</b><br>Age: {in_age}<br>Angulation: {in_angle}°<extra></extra>'))
        fig.update_layout(
            xaxis=dict(title='Age',gridcolor='rgba(255,255,255,0.05)',
                       zerolinecolor='rgba(255,255,255,0.08)',tickfont=dict(color='rgba(255,255,255,0.6)')),
            yaxis=dict(title='AP Angulation (°)',gridcolor='rgba(255,255,255,0.05)',
                       zerolinecolor='rgba(255,255,255,0.08)',tickfont=dict(color='rgba(255,255,255,0.6)')),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(12,12,18,1)',
            legend=dict(orientation='h',yanchor='bottom',y=1.02,xanchor='right',x=1,
                        font=dict(color='white',size=12),bgcolor='rgba(0,0,0,0)'),
            height=460, margin=dict(t=20,b=50,l=60,r=20), dragmode=False)
        return fig, dict(displayModeBar=False)

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    st.sidebar.markdown("## 🏥 Patient Profile")
    if st.sidebar.button("← Back to Home"):
        st.session_state.page = "landing"
        st.rerun()
    st.sidebar.markdown("---")

    in_age        = st.sidebar.slider("Patient Age", 1, 80, 14)
    in_angle      = st.sidebar.slider("AP Angulation (Degrees)", 0.0, 20.0, 13.0, step=0.1)
    in_growth     = st.sidebar.slider("Growth Plate Width (mm)", 0.0, 10.0, 3.0, step=0.1)
    in_weight     = st.sidebar.slider("Weight (kg)", 5, 150, 60)
    in_refracture = st.sidebar.checkbox("Refracture History?")
    in_infection  = st.sidebar.checkbox("Previous Infection History?")
    in_treatment  = st.sidebar.selectbox("Proposed Treatment Plan", list(TREATMENT_KEYWORDS.keys()))

    if in_age > 18:
        st.sidebar.info("ℹ️ Growth plate width is not factored into matching for patients over 18.")

    st.sidebar.markdown("---")
    analyze = st.sidebar.button("🔍 Analyze Similar Cases", use_container_width=True)

    # ── MAIN AREA ─────────────────────────────────────────────────────────────
    st.title("🏥 Precision Tibia Case Matcher")
    st.caption("Set the patient profile in the sidebar and click **Analyze Similar Cases** to begin.")
    st.divider()

    if analyze:
        try:
            response = supabase.table("tibia_fractures1").select("*").execute()
            df = pd.DataFrame(response.data)
            if df.empty:
                st.error("No data found.")
            else:
                df.columns = df.columns.str.strip().str.lower()
                st.header(f"Proposed Treatment: {in_treatment}")
                proposed_rate, proposed_matches = compute_success_rate(
                    df, TREATMENT_KEYWORDS[in_treatment],
                    in_age, in_angle, in_growth, in_weight, in_refracture, in_infection)
                if proposed_matches is None:
                    st.warning(f"⚠️ No sufficiently similar historical cases found for **{in_treatment}**.")
                else:
                    pm = proposed_matches.set_index('patient_id')
                    st.subheader("Top 5 Most Similar Cases")
                    st.dataframe(pm[['age','ap_angulation','growth_plates','weight_kg','refracture','success']], use_container_width=True)
                    st.metric("Success Rate", f"{proposed_rate}%")
                    label, message = get_suggestion(proposed_rate, in_treatment)
                    st.markdown(f"### {label}")
                    st.info(message)
                    st.subheader("🔭 Patient Universe")
                    st.caption("🟢 Green = success  🔴 Red = failed  ⭐ Star = your patient")
                    sf, sc = build_scatter(df, in_age, in_angle, TREATMENT_KEYWORDS[in_treatment])
                    st.plotly_chart(sf, use_container_width=True, config=sc)

                st.divider()
                st.header("📊 Treatment Comparison — All Options")
                st.caption("Success rate based on genuinely similar cases only.")
                treatment_rates = {}
                results = []
                for tn, kw in TREATMENT_KEYWORDS.items():
                    rate, _ = compute_success_rate(df, kw, in_age, in_angle, in_growth, in_weight, in_refracture, in_infection)
                    treatment_rates[tn] = rate
                    results.append({"Treatment": tn,
                                    "Success Rate": f"{rate}%" if rate is not None else "No similar cases",
                                    "Proposed": "⭐ Proposed" if tn == in_treatment else ""})
                rdf = pd.DataFrame(results)
                rdf['_sort'] = pd.to_numeric(rdf['Success Rate'].str.replace('%','',regex=False), errors='coerce')
                rdf = rdf.sort_values('_sort', ascending=False).drop(columns='_sort').reset_index(drop=True)
                rdf.index += 1
                nr = [(r['Treatment'], int(r['Success Rate'].replace('%','')))
                      for r in results if isinstance(r['Success Rate'],str) and '%' in r['Success Rate']]
                if nr:
                    bt, br = max(nr, key=lambda x: x[1])
                    if bt != in_treatment:
                        ps = f"{proposed_rate}%" if proposed_rate is not None else "no similar cases"
                        st.success(f"🏆 **Recommended: {bt}** — {br}% success rate, outperforming {in_treatment} ({ps}).")
                    else:
                        st.success(f"🏆 **{in_treatment} is already the best option** with {br}% success rate.")
                else:
                    st.warning("⚠️ No treatments found with sufficiently similar historical cases.")
                st.dataframe(rdf[['Treatment','Success Rate','Proposed']], use_container_width=True)
                st.divider()
                st.header("🕸️ Treatment Success Radar")
                st.caption("Each axis = a treatment type. Further from center = higher success rate.")
                rf, rc = build_radar(treatment_rates)
                st.plotly_chart(rf, use_container_width=True, config=rc)
        except Exception as e:
            st.error(f"Error: {e}")
