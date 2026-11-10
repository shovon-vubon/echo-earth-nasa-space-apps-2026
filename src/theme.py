"""Restrained UI styling; inherits the user's Streamlit light/dark theme."""
import streamlit as st


def apply_theme():
    st.html("""<style>
    .stMainBlockContainer{max-width:1400px;padding-top:2rem;padding-bottom:3rem}
    h1{letter-spacing:-.045em;font-weight:750!important}h2,h3{letter-spacing:-.025em}
    [data-testid="stMetric"]{border:1px solid color-mix(in srgb,currentColor 15%,transparent);border-radius:16px;padding:1.1rem}
    [data-testid="stMetricValue"]{font-variant-numeric:tabular-nums}
    [data-testid="stButton"] button[kind="primary"]{background:#087f72;border-color:#087f72;color:#fff;border-radius:10px;font-weight:600}
    [data-testid="stButton"] button:focus-visible{outline:3px solid #55bdb3;outline-offset:3px}
    .ee-kicker{color:#39a799;font-size:.78rem;letter-spacing:.15em;font-weight:650;margin:.25rem 0 .9rem}
    .ee-intro{font-size:1.1rem;line-height:1.65;max-width:37rem;opacity:.85}
    .ee-empty{padding:2rem;border:1px dashed #618b87;border-radius:18px;margin:1rem 0;line-height:1.8}
    </style>""")
