import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client
import plotly.graph_objects as go

# 1. DATABASE CONNECTION
URL = "https://sojkgoaefkgtnxmhkptz.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNvamtnb2FlZmtndG54bWhrcHR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ2MTYxMjIsImV4cCI6MjA5MDE5MjEyMn0.Ev1EmLOpdcVzj6Jcpsuv9m7z_3ybYowodU2yc7abpyQ"
supabase = create_client(URL, KEY)

st.set_page_config(page_title="Precision Tibia Case Matcher", layout="wide", initial_sidebar_state="collapsed")

# ── SESSION STATE ────────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

# ── LANDING PAGE ─────────────────────────────────────────────────────────────
if st.session_state.page == 'landing':

    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        /* Hide Streamlit chrome */
        #MainMenu, header, footer, [data-testid="stToolbar"] { visibility: hidden; }
        [data-testid="stAppViewContainer"] { background: #FAFAF8; }
        [data-testid="stVerticalBlock"] > div { padding: 0 !important; }
        .block-container { padding: 0 !important; max-width: 100% !important; }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'DM Sans', sans-serif;
            background: #FAFAF8;
            color: #1a1a1a;
        }

        /* NAV */
        .nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 28px 64px;
            border-bottom: 1px solid #E8E8E4;
            background: #FAFAF8;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .nav-logo {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            font-weight: 700;
            color: #1a1a1a;
            letter-spacing: -0.3px;
        }
        .nav-logo span { color: #2563EB; }
        .nav-tag {
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: #888;
        }

        /* HERO */
        .hero {
            display: grid;
            grid-template-columns: 1fr 1fr;
            min-height: 88vh;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 64px;
            align-items: center;
            gap: 80px;
        }
        .hero-left { animation: fadeUp 0.8s ease both; }
        .hero-tag {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #EFF6FF;
            color: #2563EB;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: 100px;
            margin-bottom: 28px;
        }
        .hero-tag::before {
            content: '';
            width: 6px; height: 6px;
            background: #2563EB;
            border-radius: 50%;
        }
        .hero-title {
            font-family: 'Playfair Display', serif;
            font-size: clamp(42px, 5vw, 68px);
            font-weight: 700;
            line-height: 1.08;
            letter-spacing: -1.5px;
            color: #111;
            margin-bottom: 24px;
        }
        .hero-title em {
            font-style: italic;
            color: #2563EB;
        }
        .hero-desc {
            font-size: 17px;
            font-weight: 300;
            line-height: 1.75;
            color: #555;
            max-width: 480px;
            margin-bottom: 44px;
        }
        .hero-cta-row { display: flex; align-items: center; gap: 20px; }
        .cta-btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: #111;
            color: white;
            font-family: 'DM Sans', sans-serif;
            font-size: 15px;
            font-weight: 500;
            padding: 16px 32px;
            border-radius: 100px;
            text-decoration: none;
            border: none;
            cursor: pointer;
            transition: all 0.2s;
            letter-spacing: -0.2px;
        }
        .cta-btn:hover { background: #2563EB; transform: translateY(-1px); }
        .cta-btn svg { transition: transform 0.2s; }
        .cta-btn:hover svg { transform: translateX(3px); }
        .cta-secondary {
            font-size: 14px;
            color: #888;
            font-weight: 400;
        }

        /* HERO RIGHT — visual card */
        .hero-right {
            animation: fadeUp 0.8s ease 0.15s both;
        }
        .visual-card {
            background: white;
            border: 1px solid #E8E8E4;
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 8px 40px rgba(0,0,0,0.06);
        }
        .card-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 24px;
        }
        .card-dot { width: 10px; height: 10px; border-radius: 50%; }
        .card-title {
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: #888;
        }
        .treatment-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #F0F0EC;
        }
        .treatment-row:last-child { border-bottom: none; }
        .treatment-name { font-size: 14px; font-weight: 500; color: #333; }
        .treatment-bar-wrap { flex: 1; margin: 0 16px; height: 6px; background: #F0F0EC; border-radius: 100px; overflow: hidden; }
        .treatment-bar { height: 100%; border-radius: 100px; animation: growBar 1.2s ease both; }
        .treatment-pct { font-size: 13px; font-weight: 600; color: #111; min-width: 36px; text-align: right; }

        /* DIVIDER LINE */
        .section-divider {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 64px;
            border-top: 1px solid #E8E8E4;
        }

        /* STATS */
        .stats {
            max-width: 1400px;
            margin: 0 auto;
            padding: 80px 64px;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 48px;
            animation: fadeUp 0.8s ease 0.3s both;
        }
        .stat-item { }
        .stat-num {
            font-family: 'Playfair Display', serif;
            font-size: 52px;
            font-weight: 700;
            color: #111;
            letter-spacing: -2px;
            line-height: 1;
            margin-bottom: 8px;
        }
        .stat-num span { color: #2563EB; }
        .stat-label {
            font-size: 13px;
            font-weight: 400;
            color: #888;
            line-height: 1.5;
        }

        /* FEATURES */
        .features {
            background: #111;
            padding: 100px 64px;
        }
        .features-inner {
            max-width: 1400px;
            margin: 0 auto;
        }
        .features-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 64px;
        }
        .features-title {
            font-family: 'Playfair Display', serif;
            font-size: 44px;
            font-weight: 700;
            color: white;
            letter-spacing: -1px;
            line-height: 1.1;
        }
        .features-title em { font-style: italic; color: #60A5FA; }
        .features-sub {
            font-size: 14px;
            color: #666;
            max-width: 260px;
            line-height: 1.6;
            text-align: right;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2px;
        }
        .feature-card {
            background: #1a1a1a;
            padding: 40px 36px;
            border-radius: 2px;
            transition: background 0.2s;
        }
        .feature-card:first-child { border-radius: 16px 2px 2px 2px; }
        .feature-card:nth-child(3) { border-radius: 2px 16px 2px 2px; }
        .feature-card:nth-child(4) { border-radius: 2px 2px 2px 16px; }
        .feature-card:last-child { border-radius: 2px 2px 16px 2px; }
        .feature-card:hover { background: #222; }
        .feature-icon {
            width: 44px; height: 44px;
            background: #2563EB18;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            margin-bottom: 20px;
        }
        .feature-name {
            font-size: 16px;
            font-weight: 600;
            color: white;
            margin-bottom: 10px;
            letter-spacing: -0.2px;
        }
        .feature-desc {
            font-size: 13px;
            color: #666;
            line-height: 1.65;
        }

        /* FOOTER */
        .footer {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 64px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #E8E8E4;
        }
        .footer-logo {
            font-family: 'Playfair Display', serif;
            font-size: 15px;
            font-weight: 700;
            color: #888;
        }
        .footer-note {
            font-size: 12px;
            color: #aaa;
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes growBar {
            from { width: 0; }
        }

        /* Streamlit button override */
        .stButton > button {
            display: none !important;
        }
    </style>

    <!-- NAV -->
    <div class="nav">
        <div class="nav-logo">Tibia<span>Matcher</span></div>
        <div class="nav-tag">Clinical Decision Support</div>
    </div>

    <!-- HERO -->
    <div class="hero">
        <div class="hero-left">
            <div class="hero-tag">Orthopaedic Intelligence</div>
            <h1 class="hero-title">Find the right<br>treatment, <em>faster.</em></h1>
            <p class="hero-desc">
                A data-driven case matcher for tibia fractures. Enter a patient profile and instantly surface the five most similar historical cases — with treatment success rates, clinical comparisons, and visual insights.
            </p>
            <div class="hero-cta-row">
                <button class="cta-btn" onclick="window.launchApp()">
                    Launch Tool
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M3 8h10M9 4l4 4-4 4" stroke="white" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
                <span class="cta-secondary">2,800+ historical cases</span>
            </div>
        </div>

        <div class="hero-right">
            <div class="visual-card">
                <div class="card-header">
                    <div class="card-dot" style="background:#22C55E"></div>
                    <span class="card-title">Treatment Success Rates</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">Cast</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:82%;background:#22C55E"></div></div>
                    <span class="treatment-pct">82%</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">Closed Reduction</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:76%;background:#3B82F6"></div></div>
                    <span class="treatment-pct">76%</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">K-Wire Fixation</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:73%;background:#8B5CF6"></div></div>
                    <span class="treatment-pct">73%</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">Nail (Intramedullary)</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:61%;background:#F59E0B"></div></div>
                    <span class="treatment-pct">61%</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">ORIF</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:54%;background:#F97316"></div></div>
                    <span class="treatment-pct">54%</span>
                </div>
                <div class="treatment-row">
                    <span class="treatment-name">External Fixation</span>
                    <div class="treatment-bar-wrap"><div class="treatment-bar" style="width:47%;background:#EF4444"></div></div>
                    <span class="treatment-pct">47%</span>
                </div>
            </div>
        </div>
    </div>

    <div class="section-divider"></div>

    <!-- STATS -->
    <div class="stats">
        <div class="stat-item">
            <div class="stat-num">2<span>,</span>800<span>+</span></div>
            <div class="stat-label">Historical cases<br>in the database</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">6</div>
            <div class="stat-label">Treatment types<br>compared simultaneously</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">5</div>
            <div class="stat-label">Weighted clinical<br>similarity factors</div>
        </div>
        <div class="stat-item">
            <div class="stat-num"><span>&lt;</span>2s</div>
            <div class="stat-label">Time to generate<br>a full case analysis</div>
        </div>
    </div>

    <!-- FEATURES -->
    <div class="features">
        <div class="features-inner">
            <div class="features-header">
                <h2 class="features-title">Built for<br><em>clinical precision.</em></h2>
                <p class="features-sub">Every design decision prioritises how surgeons actually think about fracture management.</p>
            </div>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">⚖️</div>
                    <div class="feature-name">Weighted Similarity</div>
                    <div class="feature-desc">AP angulation and infection history carry more weight than age or weight — because clinically, they should.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🦴</div>
                    <div class="feature-name">Age-Aware Matching</div>
                    <div class="feature-desc">Growth plate data is automatically excluded from the similarity score for patients over 18.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🕸️</div>
                    <div class="feature-name">Radar Comparison</div>
                    <div class="feature-desc">All six treatments visualised at once. See which option has the best success profile for this specific patient.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔭</div>
                    <div class="feature-name">Patient Universe</div>
                    <div class="feature-desc">Scatter plot shows where your patient sits relative to all historical cases — red clusters signal high risk at a glance.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-name">Honest Thresholds</div>
                    <div class="feature-desc">If no genuinely similar cases exist, the tool says so — rather than surfacing misleading matches.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <div class="feature-name">Tiered Confidence</div>
                    <div class="feature-desc">Four confidence levels from Strong Recommendation to Not Recommended, based on historical success rates.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <div class="footer-logo">TibiaMatcher</div>
        <div class="footer-note">For clinical decision support only. Not a substitute for professional medical judgement.</div>
    </div>

    <script>
        window.launchApp = function() {
            // Click the hidden Streamlit button
            const btn = window.parent.document.querySelector('[data-testid="stButton"] button');
            if (btn) btn.click();
        }
    </script>
    """, unsafe_allow_html=True)

    # Hidden Streamlit button triggered by JS
    if st.button("launch", key="launch_btn"):
        st.session_state.page = 'app'
        st.rerun()

# ── MAIN APP ──────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] { background: #0a0a0f; }
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
        num_cols = ['age', 'ap_angulation', 'growth_plates', 'weight_kg']
        for col in num_cols:
            subset[col] = pd.to_numeric(subset[col], errors='coerce')
        subset = subset.dropna(subset=['age', 'ap_angulation'])
        if subset.empty:
            return None, None
        subset['growth_plates'] = subset['growth_plates'].fillna(subset['growth_plates'].median())
        subset['weight_kg']     = subset['weight_kg'].fillna(subset['weight_kg'].median())
        subset['inf_val'] = subset['infection_history'].map({True: 1, False: 0, 1: 1, 0: 0}).fillna(0)

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
        close_matches = subset[subset['distance'] <= 2.0].sort_values('distance', ascending=True).head(5)
        if close_matches.empty:
            return None, None
        return int((close_matches['success'].sum() / len(close_matches)) * 100), close_matches

    def build_radar(treatment_rates):
        labels = list(treatment_rates.keys())
        values = [treatment_rates[t] if treatment_rates[t] is not None else 0 for t in labels]
        labels_closed = labels + [labels[0]]
        values_closed = values + [values[0]]
        avg = np.mean([v for v in values if v > 0])
        if avg >= 70:   fill_color, line_color = 'rgba(29,158,117,0.35)', '#1d9e75'
        elif avg >= 45: fill_color, line_color = 'rgba(186,117,23,0.35)', '#ba7517'
        else:           fill_color, line_color = 'rgba(162,45,45,0.35)',  '#a32d2d'
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed, theta=labels_closed, fill='toself',
            fillcolor=fill_color, line=dict(color=line_color, width=2.5),
            marker=dict(size=7, color=line_color),
            hovertemplate='<b>%{theta}</b><br>Success Rate: %{r}%<extra></extra>',
        ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0,100],
                    tickvals=[20,40,60,80,100], ticktext=['20%','40%','60%','80%','100%'],
                    tickfont=dict(size=10, color='rgba(255,255,255,0.45)'),
                    gridcolor='rgba(255,255,255,0.08)', linecolor='rgba(255,255,255,0.1)'),
                angularaxis=dict(tickfont=dict(size=13, color='white'),
                    linecolor='rgba(255,255,255,0.15)', gridcolor='rgba(255,255,255,0.08)'),
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False, height=520, margin=dict(t=40,b=40,l=80,r=80), dragmode=False,
        )
        return fig, dict(displayModeBar=False, staticPlot=True)

    def build_scatter(df, in_age, in_angle, keyword):
        np.random.seed(42)
        db_col = df['treatment_type'].astype(str).str.strip().str.lower()
        subset = df[db_col.str.contains(keyword, na=False)].copy()
        for col in ['age', 'ap_angulation', 'success']:
            subset[col] = pd.to_numeric(subset[col], errors='coerce')
        subset = subset.dropna(subset=['age', 'ap_angulation', 'success'])
        subset = subset.copy()
        subset['age_j']   = subset['age']           + np.random.uniform(-0.35, 0.35, len(subset))
        subset['angle_j'] = subset['ap_angulation'] + np.random.uniform(-0.18, 0.18, len(subset))
        s = subset[subset['success'] == 1]
        f = subset[subset['success'] == 0]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=f['age_j'], y=f['angle_j'], mode='markers',
            marker=dict(color='#FF3333', size=8, opacity=0.85, line=dict(color='rgba(0,0,0,0.3)', width=0.5)),
            name='Failed',
            hovertemplate='Age: %{customdata[0]}<br>Angulation: %{customdata[1]}°<br><b>Failed</b><extra></extra>',
            customdata=f[['age','ap_angulation']].values,
        ))
        fig.add_trace(go.Scatter(
            x=s['age_j'], y=s['angle_j'], mode='markers',
            marker=dict(color='#00E676', size=8, opacity=0.75, line=dict(color='rgba(0,0,0,0.3)', width=0.5)),
            name='Success',
            hovertemplate='Age: %{customdata[0]}<br>Angulation: %{customdata[1]}°<br><b>Success</b><extra></extra>',
            customdata=s[['age','ap_angulation']].values,
        ))
        fig.add_trace(go.Scatter(
            x=[in_age], y=[in_angle], mode='markers',
            marker=dict(symbol='circle', color='rgba(255,255,255,0.18)', size=42,
                        line=dict(color='rgba(255,255,255,0.5)', width=1.5)),
            showlegend=False, hoverinfo='skip',
        ))
        fig.add_trace(go.Scatter(
            x=[in_age], y=[in_angle], mode='markers',
            marker=dict(symbol='star', color='white', size=26, line=dict(color='#111', width=2)),
            name='Your Patient',
            hovertemplate=f'<b>⭐ Your Patient</b><br>Age: {in_age}<br>Angulation: {in_angle}°<extra></extra>',
        ))
        fig.update_layout(
            xaxis=dict(title='Age', gridcolor='rgba(255,255,255,0.05)',
                       zerolinecolor='rgba(255,255,255,0.08)', tickfont=dict(color='rgba(255,255,255,0.6)')),
            yaxis=dict(title='AP Angulation (°)', gridcolor='rgba(255,255,255,0.05)',
                       zerolinecolor='rgba(255,255,255,0.08)', tickfont=dict(color='rgba(255,255,255,0.6)')),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(12,12,18,1)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                        font=dict(color='white', size=12), bgcolor='rgba(0,0,0,0)'),
            height=460, margin=dict(t=20, b=50, l=60, r=20), dragmode=False,
        )
        return fig, dict(displayModeBar=False)

    # SIDEBAR
    st.sidebar.markdown("## 🏥 Patient Profile")
    if st.sidebar.button("← Back to Home"):
        st.session_state.page = 'landing'
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

    st.title("🏥 Precision Tibia Case Matcher")

    if st.sidebar.button("Analyze Similar Cases"):
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
                    in_age, in_angle, in_growth, in_weight, in_refracture, in_infection
                )

                if proposed_matches is None:
                    st.warning(f"⚠️ No sufficiently similar historical cases found for **{in_treatment}** with this patient profile.")
                else:
                    proposed_matches_display = proposed_matches.set_index('patient_id')
                    st.subheader("Top 5 Most Similar Cases")
                    st.dataframe(proposed_matches_display[['age','ap_angulation','growth_plates','weight_kg','refracture','success']], use_container_width=True)
                    st.metric("Success Rate", f"{proposed_rate}%")
                    label, message = get_suggestion(proposed_rate, in_treatment)
                    st.markdown(f"### {label}")
                    st.info(message)
                    st.subheader("🔭 Patient Universe")
                    st.caption("🟢 Green = success  🔴 Red = failed  ⭐ Star = your patient")
                    scatter_fig, scatter_config = build_scatter(df, in_age, in_angle, TREATMENT_KEYWORDS[in_treatment])
                    st.plotly_chart(scatter_fig, use_container_width=True, config=scatter_config)

                st.divider()
                st.header("📊 Treatment Comparison — All Options")
                st.caption("Success rate based on genuinely similar cases only.")

                treatment_rates = {}
                results = []
                for treatment_name, keyword in TREATMENT_KEYWORDS.items():
                    rate, _ = compute_success_rate(df, keyword, in_age, in_angle, in_growth, in_weight, in_refracture, in_infection)
                    treatment_rates[treatment_name] = rate
                    results.append({
                        "Treatment":    treatment_name,
                        "Success Rate": f"{rate}%" if rate is not None else "No similar cases",
                        "Proposed":     "⭐ Proposed" if treatment_name == in_treatment else "",
                    })

                results_df = pd.DataFrame(results)
                results_df['_sort'] = pd.to_numeric(results_df['Success Rate'].str.replace('%','', regex=False), errors='coerce')
                results_df = results_df.sort_values('_sort', ascending=False).drop(columns='_sort').reset_index(drop=True)
                results_df.index += 1

                numeric_results = [(r['Treatment'], int(r['Success Rate'].replace('%','')))
                                   for r in results if isinstance(r['Success Rate'], str) and '%' in r['Success Rate']]
                if numeric_results:
                    best_treatment, best_rate = max(numeric_results, key=lambda x: x[1])
                    if best_treatment != in_treatment:
                        proposed_str = f"{proposed_rate}%" if proposed_rate is not None else "no similar cases"
                        st.success(f"🏆 **Recommended Treatment: {best_treatment}** — {best_rate}% success rate, outperforming the proposed {in_treatment} ({proposed_str}).")
                    else:
                        st.success(f"🏆 **The proposed treatment ({in_treatment}) is already the best option** with a {best_rate}% success rate.")
                else:
                    st.warning("⚠️ No treatments found with sufficiently similar historical cases.")

                st.dataframe(results_df[['Treatment','Success Rate','Proposed']], use_container_width=True)
                st.divider()
                st.header("🕸️ Treatment Success Radar")
                st.caption("Each axis = a treatment type. Further from center = higher success rate for this patient profile.")
                fig, config = build_radar(treatment_rates)
                st.plotly_chart(fig, use_container_width=True, config=config)

        except Exception as e:
            st.error(f"Error: {e}")
