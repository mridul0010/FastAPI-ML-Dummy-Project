import streamlit as st
import requests

# Configuration
API_URL = "http://127.0.0.1:8000/predict" 

st.set_page_config(page_title="Premium Predictor", page_icon="🛡️", layout="centered")

st.title("🛡️ Insurance Premium Category Predictor")
st.markdown("Enter your details below to estimate your premium risk category.")
st.markdown("---")

# Organize inputs into columns for better UX
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Personal Profile")
    age = st.number_input("Age", min_value=1, max_value=119, value=30)
    occupation = st.selectbox(
        "Occupation",
        ['private_job', 'business_owner', 'government_job', 'freelancer', 'student', 'retired', 'unemployed']
    )
    income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0, step=0.5)
    city = st.text_input("City", value="Mumbai")

with open ("model.pkl" , 'rb') as f:
    model = pickle.load(f)

with col2:
    st.subheader("🩺 Health Metrics")
    height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7, step=0.01)
    weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0, step=0.5)
    
    # User-friendly labels mapping to boolean values
    smoker = st.selectbox(
        "Do you smoke?", 
        options=[True, False], 
        format_func=lambda x: "Yes" if x else "No"
    )

st.markdown("---")

# Predict Button
if st.button("Predict Premium Category", type="primary", use_container_width=True):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        with st.spinner("Analyzing risk metrics..."):
            response = requests.post(API_URL, json=input_data)
            result = response.json()

        # FIXED: Handles direct dictionary output from FastAPI securely
        if response.status_code == 200:
            
            # 1. Display Main Result
            st.success(f"### Predicted Category: **{result['predicted_category']}**")
            
            # 2. Safely extract confidence metric if your API provides it
            if "confidence" in result:
                confidence_value = result["confidence"]
                formatted_confidence = f"{confidence_value:.2%}" if isinstance(confidence_value, float) else confidence_value
                st.metric(label="Prediction Confidence", value=formatted_confidence)
            
            # 3. Safely extract and chart class probabilities if your API provides them
            if "class_probabilities" in result:
                st.subheader("📊 Class Probabilities Breakdown")
                st.bar_chart(result["class_probabilities"])

        else:
            st.error(f"❌ API Error: Status Code {response.status_code}")
            st.json(result)

    except requests.exceptions.ConnectionError:
        st.error("❌ **Connection Failed:** Could not connect to the FastAPI server. Please verify that your backend service is active at `http://127.0.0.1:8000`.")