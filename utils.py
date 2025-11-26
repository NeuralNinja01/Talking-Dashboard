import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

        /* Main Background */
        .stApp {
            background: radial-gradient(circle at 10% 20%, rgb(14, 17, 23) 0%, rgb(30, 30, 40) 90%);
            color: #ffffff;
            font-family: 'Outfit', sans-serif;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: rgba(22, 27, 34, 0.95);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Glassmorphism Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
            border-color: rgba(255, 255, 255, 0.15);
        }

        /* Headers */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        h1 {
            font-size: 3rem;
            background: linear-gradient(135deg, #FFFFFF 0%, #a5b4fc 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Buttons */
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 600;
            letter-spacing: 0.5px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5);
        }

        /* Inputs */
        .stTextInput>div>div>input {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 10px 15px;
        }
        .stTextInput>div>div>input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }

        /* Metrics */
        div[data-testid="stMetricValue"] {
            color: #a5b4fc;
            font-weight: 700;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0e1117; 
        }
        ::-webkit-scrollbar-thumb {
            background: #30363d; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #58a6ff; 
        }
    </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div style="text-align: center; margin-bottom: 50px; padding-top: 20px;">
        <h1 style="font-size: 4rem; margin-bottom: 10px;">
            Talking Rabbitt
        </h1>
        <p style="font-size: 1.4rem; color: #a5b4fc; font-weight: 300;">
            When your data finally learns to talk back...
        </p>
    </div>
    """, unsafe_allow_html=True)
