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

    # 3. Chat with Rabbitt Button
    if st.session_state.get('chat_open', False):
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✖ Close Chat", use_container_width=True, key="close_chat_main", type="primary"):
                st.session_state.chat_open = False
                st.session_state.last_input = ""
                if 'input_key' in st.session_state:
                    st.session_state.input_key += 1
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💬 Chat with Rabbitt", use_container_width=True, key="open_chat_btn"):
                st.session_state.chat_open = True
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Please upload a dataset to begin.")

# --- Chat in Sidebar ---
if 'df' in st.session_state and st.session_state.get('chat_open', False):
    # Initialize
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'last_input' not in st.session_state:
        st.session_state.last_input = ""
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    
    # Wider sidebar
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            width: 550px !important;
            min-width: 550px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            width: 550px !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### 🐰 Chat with Rabbitt")
        st.markdown("---")
        
        # Chat messages
        chat_container = st.container(height=500)
        with chat_container:
            if len(st.session_state.chat_history) == 0:
                st.info("👋 Hi! Ask me anything about your data. I can answer questions and create visualizations!")
            else:
                for idx, message in enumerate(st.session_state.chat_history):
                    from utils import render_chat_message
                    render_chat_message(message, key_prefix=f"chat_{idx}")
        
        st.markdown("---")
        
        # Input with dynamic key to clear after sending
        user_input = st.text_input(
            "Message", 
            key=f"chat_input_{st.session_state.input_key}", 
            label_visibility="collapsed",
            placeholder="Type your question..."
        )
        
        col_voice, _ = st.columns([1, 4])
        with col_voice:
            voice_input = speech_to_text(
                language='en',
                start_prompt="🎤",
                stop_prompt="🛑",
                just_once=True,
                use_container_width=True,
                key=f"chat_voice_{st.session_state.input_key}"
            )
        
        # Process
        question = None
        is_voice = False
        
        if voice_input and voice_input != st.session_state.last_input:
            question = voice_input
            is_voice = True
            st.session_state.last_input = voice_input
        elif user_input and user_input != st.session_state.last_input and user_input.strip():
            question = user_input
            is_voice = False
            st.session_state.last_input = user_input
        
        if question:
            df = st.session_state.df
            
            st.session_state.chat_history.append({
                "role": "user",
                "content": question,
                "code": None,
                "figure": None
            })
            
            with st.spinner("🐰 Thinking..."):
                response = st.session_state.rabbit.ask_question(
                    df, question, st.session_state.chat_history
                )
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response["answer"],
                "code": response.get("code"),
                "figure": response.get("figure")
            })
            
            if is_voice:
                try:
                    from gtts import gTTS
                    import base64
                    tts = gTTS(text=response["answer"], lang='en')
                    audio_bytes = io.BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    st.session_state.pending_audio = base64.b64encode(audio_bytes.read()).decode()
                except:
                    pass
            
            # Increment key to clear input
            st.session_state.input_key += 1
            st.rerun()
        
        if 'pending_audio' in st.session_state:
            st.markdown(f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{st.session_state.pending_audio}" type="audio/mp3">
            </audio>
            """, unsafe_allow_html=True)
            del st.session_state.pending_audio
        
        # Clear button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_input = ""
            st.session_state.input_key += 1
            st.rerun()








