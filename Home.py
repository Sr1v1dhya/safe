import streamlit as st
import importlib.util
import os
from streamlit_extras.badges import badge

# Get URL query params early
params = st.query_params
hidden_page = params.get("page")

# Only call set_page_config here if NOT loading a hidden page
if hidden_page not in ["Data_Upload", "Statistics"]:
    st.set_page_config(
        page_title="SAFE App",
        page_icon="🛡", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stButton>button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .stTextInput>div>div>input {
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }
        .welcome-header {
            font-size: 2.5rem !important;
            margin-bottom: 1rem;
        }
        .feature-card {
            border-radius: 10px;
            padding: 1.5rem;
            background-color: #f0f2f6;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .feature-icon {
            font-size: 1.8rem;
            margin-bottom: 0.5rem;
        }
        .divider {
            margin: 2rem 0;
            border-top: 1px solid #e1e4e8;
        }
        .footer {
            margin-top: 3rem;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# Route to hidden pages
if hidden_page in ["Data_Upload", "Statistics"]:
    file_path = f"hidden_pages/{hidden_page}.py"
    if os.path.exists(file_path):
        spec = importlib.util.spec_from_file_location("hidden_module", file_path)
        hidden_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hidden_module)
        hidden_module.main()  # assumes each hidden page defines main()
    else:
        st.set_page_config(page_title="Error", layout="centered")
        st.error("Page not found")
else:
    # Default homepage UI with improved layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="welcome-header">🆘 Welcome to S.A.F.E. Chatbot</h1>', unsafe_allow_html=True)
        st.markdown("""
            **Your Secure AI-powered Assistant** for document analysis and intelligent conversations.
            Upload your documents, ask questions, and get accurate answers powered by advanced AI.
        """)
    
    with col2:
        st.image("firstaid.png", width=150)  # Replace with your logo
    
    st.divider()
    
    # Feature cards
    st.subheader("Key Features")
    cols = st.columns(2)
    
    with cols[0]:
        with st.container(border=True):
            st.markdown('<div class="feature-icon">💬</div>', unsafe_allow_html=True)
            st.markdown('<a href="/Chat_Bot" target="_self" style="text-decoration: none;"><strong>SAFE Chatbot</strong></a>',unsafe_allow_html=True)
            st.markdown("Ask questions using multi-modal inputs and get answers based on medically certified first aid manuals.")
    with cols[1]:
        with st.container(border=True):
            st.markdown('<div class="feature-icon">🏥</div>', unsafe_allow_html=True)
            st.markdown('<a href="/Hospitals" target="_self" style="text-decoration: none;"><strong>Nearby Hospitals</strong></a>',unsafe_allow_html=True)
            st.markdown("Lists nearby Hospitals based on your location along with a map link to the hospitals.")
    
    st.divider()
    
    
    # Quick start section
    st.subheader("Get Started")
    with st.expander("How to use the S.A.F.E. App", expanded=True):
        st.markdown("""
        1. **Choose Your Input Mode**: Select from audio, image, or text to ask your question.
        2. **Start Chatting**: Go to the **Chatbot** section to interact with the AI.
        3. **Receive Verified Answers**: Get responses based on certified first aid manuals and reliable medical sources.
        4. **Find Nearby Help**: Use the **Maps** feature to locate the closest hospitals or medical centers.
        5. **Stay Informed**: Explore the **Statistics** page to view usage trends and common queries.
        """)

   
    
    # Footer
    st.markdown("""
        <div class="footer">
            <p>S.A.F.E. Chatbot v1.0 | Secure AI For Everyone</p>
            <div style="margin-top: 0.5rem;">
                <a href="https://github.com/Sr1v1dhya/safe" target="_blank">GitHub</a> |  
                <a href="mailto:sharon23110444@snuchennai.edu.in">Support</a>
            </div>
        </div>
    """, unsafe_allow_html=True)