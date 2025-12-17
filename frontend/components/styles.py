import streamlit as st

def apply_custom_css():
    st.markdown("""
    <style>
        /* 1. FONT IMPORT (Poppins) */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        /* Apply Font Globally */
        html, body, [class*="css"], .stMarkdown, p, div {
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* 2. TEXT COLORS (Adaptive for Dark Mode) */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important; 
        }
        
        p, div, label, span {
            color: #e0e0e0;
        }

        /* 3. LINKEDIN PREVIEW CARD (Dark Glass Style) */
        .linkedin-preview {
            background-color: rgba(255, 255, 255, 0.95) !important; /* Keep it light/white for realism, or dark for theme? */
            /* Let's make it look like a REAL LinkedIn post (White Card) inside the dark app, for contrast */
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto;
            color: #000000 !important; /* Force Black Text inside the card */
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            margin-top: 10px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .linkedin-preview .li-name { 
            font-weight: 600; 
            color: #191919 !important; 
            font-size: 14px;
        }
        
        .linkedin-preview .li-desc { 
            font-size: 12px; 
            color: #666666 !important; 
        }
        
        .linkedin-preview .li-body { 
            white-space: pre-wrap; 
            margin-top: 10px; 
            margin-bottom: 10px; 
            font-size: 14px;
            color: #191919 !important;
            line-height: 1.5;
        }
        
        .linkedin-preview .li-footer { 
            border-top: 1px solid #e0e0e0; 
            padding-top: 10px; 
            color: #666666 !important; 
            display: flex; 
            gap: 20px; 
            font-weight: 600; 
            font-size: 14px;
        }
        
        /* 4. CODE BLOCKS */
        code {
            color: #ff79c6 !important;
            background-color: #282a36 !important;
            border-radius: 4px;
            padding: 2px 5px;
        }
        
        /* 5. SUCCESS/ERROR MESSAGES */
        .stSuccess, .stError, .stInfo, .stWarning {
            background-color: rgba(0, 0, 0, 0.4) !important;
            color: white !important;
            border-radius: 8px !important;
            backdrop-filter: blur(5px);
        }

    </style>
    """, unsafe_allow_html=True)
