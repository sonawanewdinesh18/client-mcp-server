import streamlit as st

def inject_custom_css():
    """Inject modern CSS styling into the Streamlit application."""
    st.markdown(
        """
        <style>
        /* Font & Layout Optimization */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        .stApp {
            min-height: 100vh;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            text-rendering: optimizeLegibility;
            font-display: swap;
        }


        /* Modern Header styling */
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
            min-height: 2.6rem;
        }
        
        .sub-title {
            color: #64748b;
            font-size: 1.05rem;
            margin-bottom: 1.5rem;
            min-height: 1.5rem;
        }


        /* Server Card Badge */
        .badge-sse {
            display: inline-block;
            background-color: #0284c7;
            color: white;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-stdio {
            display: inline-block;
            background-color: #7c3aed;
            color: white;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge-active {
            display: inline-block;
            background-color: #10b981;
            color: white;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-inactive {
            display: inline-block;
            background-color: #6b7280;
            color: white;
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* Performance & Layout Stability Optimization */
        .stButton > button, button[kind="primary"], button[kind="secondary"] {
            contain: layout style;
            min-height: 38px;
            transition: all 0.15s ease-in-out;
        }

        /* Expander & Card Stabilization */
        [data-testid="stExpander"] {
            contain: layout;
            border-radius: 8px;
        }

        /* Tool invocation display */
        .tool-call-box {
            border-left: 3px solid #3b82f6;
            padding: 8px 12px;
            margin: 6px 0;
            background: rgba(59, 130, 246, 0.05);
            border-radius: 0 8px 8px 0;
            contain: content;
        }

        /* Tool item chip in sidebar */
        .tool-chip {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 6px 10px;
            margin-bottom: 6px;
            font-size: 0.85rem;
            contain: content;
        }

        .tool-name {
            font-weight: 600;
            color: #38bdf8;
        }
        </style>

        """,
        unsafe_allow_html=True
    )
