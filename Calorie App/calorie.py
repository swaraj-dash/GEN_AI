from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

st.set_page_config(page_title="Know Your Food!", page_icon="🍏", layout="wide")

st.markdown("""
    <style>
        .reportview-container {
            background-color: #f1f8f3;
            font-family: 'Arial', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #2c6b2f;
        }
        .css-1lcbv9v {
            background-color: #388e3c;
        }
        .stButton>button {
            background-color: #4caf50;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 12px 25px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stButton>button:hover {
            background-color: #388e3c;
            box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
        }
        .stFileUploader>label {
            background-color: white;
            color: white;
            font-weight: bold;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            display: block;
        }
        .stFileUploader>label:hover {
            background-color: #388e3c;
        }
        .stImage {
            border: 3px solid #388e3c;
            border-radius: 15px;
        }
        h1, h2, h3, p {
            color: #388e3c;
        }
        .stTextArea textarea, .stTextInput input {
            border: 1px solid #388e3c;
            border-radius: 8px;
            padding: 10px;
            font-size: 14px;
        }
        .stMarkdown {
            font-size: 16px;
            color: #388e3c;
        }
        .stWarning {
            color: #ff5722;
            font-weight: bold;
        }
        .stSubheader {
            color: #388e3c;
            font-size: 20px;
            font-weight: bold;
        }
        .stTextInput input {
            background-color: #e8f5e9;
        }
        .stTextInput input:focus {
            border: 2px solid #388e3c;
        }
        .stAlert {
            background-color: #f9fbe7;
            color: #2e7d32;
            border: 1px solid #2e7d32;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
        }
        footer {
            background-color: #388e3c;
            padding: 15px;
            color: white;
            text-align: center;
            border-radius: 8px;
        }
        footer a {
            color: white;
            text-decoration: none;
        }
        footer a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🍏 Know Your Food!")

st.markdown("""
    Welcome to **Know Your Food!: Your Calorie Checker**, a smart nutrition assistant that analyzes food images
    and provides detailed nutritional information, including calories. Upload a food image and let us
    help you track your nutrition!
""")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Upload a Food Image to Analyze")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

with col2:
    st.markdown("### Analyze Your Food")
    submit = st.button("Calculate Total Calories", use_container_width=True)

progress_bar = st.progress(0)

input_prompt = """
You are an expert in nutrition. See the food items from the image and calculate the total calories, 
also provide the details of every food item with calories intake in the following format:

1. Item 1 - calories
2. Item 2 - calories
...
"""

if submit:
    if uploaded_file is not None:
        for i in range(100):
            progress_bar.progress(i + 1)
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response("Food Image", image_data, input_prompt)
        progress_bar.progress(100)
        st.subheader("Nutrition Information")
        st.write(response)
    else:
        st.warning("Please upload an image to analyze!")

st.success("Ready to analyze your food image! Upload a picture and hit 'Calculate Total Calories'.")

st.markdown("""
    <div class="stAlert">
        Tip: For better results, upload clear images of food items with minimal background clutter!
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <footer>
        <p>&copy; 2025 Vaidya: Your Calorie Checker. All rights reserved. | Follow us on 
            <a href="https://twitter.com">Twitter</a> | 
            <a href="https://instagram.com">Instagram</a>
        </p>
    </footer>
""", unsafe_allow_html=True)
