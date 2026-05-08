import streamlit as st
import requests

st.title("AI Backend & Database Generator")

user_input = st.text_area("Describe your application:")

dataset_size = st.selectbox(
    "Select dataset size",
    [0, 700, 5000, 15000]
)
uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

if st.button("Generate Backend"):

    if not user_input.strip():
        st.error("Please enter a description.")
    else:

        response = requests.post(
            "http://localhost:8000/generate",
            data={"description": user_input,
                  "dataset_size": dataset_size
                  },
                  files={"file": uploaded_file} if uploaded_file else None  
        )

        data = response.json()

        if "error" in data:
            st.error(data["error"])
        else:

            st.subheader("Generated SQL Schema")
            st.code(data["generated_schema"], language="sql")

            st.success("Backend project generated!")

            download_url = "http://localhost:8000/download"

            st.markdown(
                f"[Download Backend Project]({download_url})",
                unsafe_allow_html=True
            )