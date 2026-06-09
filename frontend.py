import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Premium Predictor Pro", 
    page_icon="🛡️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Modern UI Custom Styling (Simulated Premium Dark Theme)
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    /* Custom styling for headers */
    h1 {
        color: #00ffcc !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
    }
    h3 {
        color: #00bfff !important;
    }
    /* Customizing container wrappers */
    div[data-testid="stBlock"] {
        background-color: #1e222b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #2d3139;
        margin-bottom: 15px;
    }
    /* Status boxes tweak */
    .stAlert {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Configuration
API_URL = "http://127.0.0.1:8000/predict" 

# Header section
st.title("🛡️ Insurance Premium Category Predictor")
st.markdown("Enter your details below to estimate your premium risk category with precision.")
st.markdown("---")

# 3. Organize inputs into clear sections using layout blocks
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("### 👤 Personal Profile")
    age = st.number_input("Age", min_value=1, max_value=120, value=30, step=1)
    
    occupation = st.selectbox(
        "Occupation",
        ['private_job', 'business_owner', 'government_job', 'freelancer', 'student', 'retired', 'unemployed']
    )
    # Ensuring income float structure is strict
    income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0, step=0.5)
    
    # Strip whitespaces and force clean string formatting
    city = st.text_input("City", value="Mumbai").strip()

with col2:
    st.markdown("### 🩺 Health Metrics")
    height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.70, step=0.01)
    weight = st.number_input("Weight (kg)", min_value=1.0, max_value=250.0, value=65.0, step=0.5)
    
    # Map selection cleanly to native Python booleans
    smoker_input = st.selectbox(
        "Do you smoke?", 
        options=[True, False], 
        format_func=lambda x: "Yes" if x else "No"
    )

st.markdown("---")

# 4. Predict Button & Robust Request Pipeline
if st.button("Predict Premium Category", type="primary", use_container_width=True):
    # Strictly cast and structure variables to ensure FastAPI Pydantic parsing complies completely
    input_data = {
        "age": int(age),
        "weight": float(weight),
        "height": float(height),
        "income_lpa": float(income_lpa),
        "smoker": bool(smoker_input),
        "city": str(city),
        "occupation": str(occupation)
    }

    try:
        with st.spinner("Analyzing risk metrics via API pipeline..."):
            response = requests.post(API_URL, json=input_data, timeout=10)
            
            # Defensive check for non-JSON or missing payloads
            try:
                result = response.json()
            except ValueError:
                result = {"detail": "The server returned an unparseable or blank payload."}

        # Handle successful prediction sequence
        if response.status_code == 200:
            st.toast("Analysis Complete!", icon="✅")
            
            # Extract and highlight prediction outcome safely
            predicted_cat = result.get('predicted_category', 'Unknown')
            st.success(f"### Predicted Category: **{predicted_cat}**")
            
            # Setup layout for feedback telemetry metrics
            m_col1, m_col2 = st.columns(2)
            
            with m_col1:
                if "confidence" in result:
                    confidence_value = result["confidence"]
                    # Format float values elegantly if present
                    formatted_confidence = f"{confidence_value:.2%}" if isinstance(confidence_value, float) else str(confidence_value)
                    st.metric(label="Prediction Confidence", value=formatted_confidence)
            
            with m_col2:
                # Optional placeholder or secondary KPI
                if "risk_score" in result:
                    st.metric(label="Relative Risk Score", value=result["risk_score"])

            # Render data visualizations cleanly
            if "class_probabilities" in result and result["class_probabilities"]:
                st.markdown("### 📊 Class Probabilities Breakdown")
                st.bar_chart(result["class_probabilities"])

        # Handle API Validation/Processing Errors (e.g., Pydantic 422 Unprocessable Entity)
        elif response.status_code == 422:
            st.error("❌ **Data Validation Error (422):** The API backend rejected the payload structure.")
            st.json(result)
            
        else:
            st.error(f"❌ **API Error:** Status Code {response.status_code}")
            st.json(result)

    except requests.exceptions.Timeout:
        st.error("❌ **Request Timeout:** The FastAPI server took too long to reply. Please verify your system's load status.")
        
    except requests.exceptions.ConnectionError:
        st.error("❌ **Connection Failed:** Could not establish a link to the FastAPI server. Please check that your backend service is running locally at `http://127.0.0.1:8000`.")
        
    except Exception as e:
        st.error(f"❌ **Unexpected Error Encountered:** {str(e)}")