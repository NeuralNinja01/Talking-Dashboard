import streamlit as st
import pandas as pd
from agents import DataJanitor, VizArchitect, TalkingRabbit
from utils import inject_custom_css, render_header
from streamlit_mic_recorder import speech_to_text
from gtts import gTTS
import io
import os

# --- Configuration ---
st.set_page_config(page_title="Talking Rabbit", layout="wide", page_icon="🐰")

# --- Initialize Agents ---
# Ideally, use st.secrets. For this deliverable, we use the provided key or placeholder.
API_KEY = "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"

if 'janitor' not in st.session_state:
    st.session_state.janitor = DataJanitor()
if 'viz_architect' not in st.session_state:
    st.session_state.viz_architect = VizArchitect(api_key=API_KEY)
if 'rabbit' not in st.session_state:
    st.session_state.rabbit = TalkingRabbit(api_key=API_KEY)

# --- UI Setup ---
inject_custom_css()
render_header()

# --- Sidebar: Data Upload ---
with st.sidebar:
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])    
    if uploaded_file:
        # Check if file is new or different
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file.name:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Agent 1: Clean Data
                with st.spinner("🧹 Data Janitor is cleaning your data..."):
                    df_clean = st.session_state.janitor.clean_data(df)
                    st.session_state.df = df_clean
                    st.session_state.last_uploaded_file = uploaded_file.name
                    
                    # Reset previous analysis
                    if 'viz_results' in st.session_state:
                        del st.session_state.viz_results
                        
                st.success("Data Cleaned & Ready!")
            except Exception as e:
                st.error(f"Error loading file: {e}")

# --- Main Dashboard ---
if 'df' in st.session_state:
    df = st.session_state.df
    
    # 1. Data Overview
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 Data Overview (Cleaned)")
    st.dataframe(df.head(), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. Visualization Agent
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🎨 Data Visualization Insights")
    
    if st.button("Generate Dashboard Analysis"):
        with st.spinner("🤖 Architect is designing your dashboard..."):
            viz_results = st.session_state.viz_architect.generate_charts(df)
            st.session_state.viz_results = viz_results
    
    if 'viz_results' in st.session_state:
        results = st.session_state.viz_results
        if results:
            # Create a grid layout
            for i in range(0, len(results), 2):
                cols = st.columns(2)
                # Chart i
                if i < len(results):
                    with cols[0]:
                        try:
                            st.markdown(f"#### {results[i]['story']}")
                            st.caption(results[i]['description'])
                            st.plotly_chart(results[i]['figure'], use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not render chart: {str(e)[:100]}")
                
                # Chart i+1
                if i + 1 < len(results):
                    with cols[1]:
                        try:
                            st.markdown(f"#### {results[i+1]['story']}")
                            st.caption(results[i+1]['description'])
                            st.plotly_chart(results[i+1]['figure'], use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not render chart: {str(e)[:100]}")
        else:
            st.warning("No visualizations could be generated.")
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. Talking Rabbit (Analyst)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🐰 Talk to Rabbit")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        text_input = st.text_input("Ask a question about your data:", placeholder="e.g., What is the total revenue?")
    
    with col2:
        st.write("Voice Input:")
        voice_text = speech_to_text(language='en', start_prompt="🎤 Speak", stop_prompt="🛑 Stop", just_once=True, use_container_width=True)
    
    # Determine input source
    user_question = None
    is_voice = False
    
    if voice_text:
        user_question = voice_text
        is_voice = True
        st.info(f"Heard: {user_question}")
    elif text_input:
        user_question = text_input
        is_voice = False

    if user_question:
        with st.spinner("🐰 Rabbit is thinking..."):
            answer, code = st.session_state.rabbit.ask_question(df, user_question)
            
            # Display Answer
            st.markdown(f"### 🤖 Answer")
            st.write(answer)
            
            # Voice Response (Only if input was voice)
            if is_voice:
                try:
                    tts = gTTS(text=answer, lang='en')
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    
                    # Convert to base64 for embedding in HTML
                    import base64
                    audio_base64 = base64.b64encode(audio_bytes.read()).decode()
                    
                    # Hidden audio player that autoplays
                    audio_html = f"""
                    <audio autoplay style="display:none;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Voice generation failed: {e}")

            with st.expander("View Logic (Code)"):
                st.code(code, language='python')

    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload a dataset to begin.")

