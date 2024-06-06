import streamlit as st
import pandas as pd
import os
import base64

# Define the models and corresponding csv files
models = {
    "gemini 1.5 pro": "gemini_15_pro.csv",
    "gpt-4o": "gpt_4o.csv",
    "Llama3 70b": "llama3_70b.csv",
}

# Load the users csv file (assuming it's in the same directory)
users_df = pd.read_csv("users.csv", dtype={"password": str})

# Initialize session state for login status and entry index
if "loggedin" not in st.session_state:
    st.session_state["loggedin"] = False
    st.session_state["username"] = ""
    st.session_state["entry_index"] = 0


# Function to check user credentials
def check_login(username, password):
    if username in users_df["username"].values:
        user_row = users_df[users_df["username"] == username]
        if user_row["password"].values[0] == password:
            return True
        else:
            st.error("Incorrect password")
    else:
        st.error("Username not found")
    return False


# Function to load model and input data
def load_data():
    input_df = pd.read_csv("input.csv")
    return input_df


# Function to display login form
def login_form():
    st.subheader("Login")
    st.info(
        "For testing purposes, use the following credentials:\n\n**Username:** test\n\n**Password:** 123"
    )
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_login(username, password):
            st.session_state["loggedin"] = True
            st.session_state["username"] = username
            st.success("Logged in successfully!")
        else:
            st.error("Login failed")


# Function to display model entries for evaluation
def display_model_entries(input_df):
    st.sidebar.subheader("Select Model")
    model = st.sidebar.selectbox("", list(models.keys()))
    model_df = pd.read_csv(models[model])

    st.markdown(
        f"**Current Entry Index: {st.session_state['entry_index'] + 1} / {len(input_df)}**"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Input Entry:**")
        st.markdown(
            f"**Title:** {input_df.iloc[st.session_state['entry_index']]['Title']}"
        )
        st.text_area(
            "Abstract:",
            value=input_df.iloc[st.session_state["entry_index"]]["Abstract"],
            height=250,
        )
    with col2:
        st.markdown(f"**{model} Entry:**")
        st.markdown(
            f"**Title:** {model_df.iloc[st.session_state['entry_index']]['Title']}"
        )
        st.text_area(
            "Paraphrased Abstract:",
            value=model_df.iloc[st.session_state["entry_index"]]["ParaphrasedAbstract"],
            height=250,
        )

    navigation_buttons(input_df)


# Function to handle navigation buttons
def navigation_buttons(input_df):
    col1, col2, col3 = st.columns([3, 10, 2])
    with col1:
        if st.button("Previous Entry"):
            if st.session_state["entry_index"] > 0:
                st.session_state["entry_index"] -= 1
                st.experimental_rerun()
    with col3:
        if st.button("Next Entry"):
            if st.session_state["entry_index"] < len(input_df) - 1:
                st.session_state["entry_index"] += 1
                st.experimental_rerun()


# Function to display evaluation scores form
def evaluation_scores():
    st.subheader("Evaluation Scores")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        semantic_score = st.radio("Semantic Score (1-5)", range(1, 6))
    with col2:
        syntactic_score = st.radio("Syntactic Score (1-5)", range(1, 6))
    with col3:
        fluency_score = st.radio("Fluency Score (1-5)", range(1, 6))
    with col4:
        overall_score = st.radio("Overall Score (1-5)", range(1, 6))
    save_scores_button(semantic_score, syntactic_score, fluency_score, overall_score)


# Function to save evaluation scores
def save_scores_button(semantic_score, syntactic_score, fluency_score, overall_score):
    col1, col2, col3, col4 = st.columns([15, 15, 15, 8])
    with col4:
        if st.button("Save Scores"):
            input_df = pd.read_csv("input.csv")
            scores_df = pd.DataFrame(
                {
                    "Title": [input_df.iloc[st.session_state["entry_index"]]["Title"]],
                    "Semantic/Adequacy Score": [semantic_score],
                    "Syntactic/Novelty Score": [syntactic_score],
                    "Fluency Score": [fluency_score],
                    "Overall Score": [overall_score],
                }
            )
            h_evals_dir = "H_Evals"
            if not os.path.exists(h_evals_dir):
                os.makedirs(h_evals_dir)
            scores_file = f"{st.session_state['username']}_{model}_scores.csv"
            filepath = os.path.join(h_evals_dir, scores_file)
            if os.path.exists(filepath):
                scores_df_existing = pd.read_csv(filepath)
                scores_df_existing = scores_df_existing[
                    scores_df_existing.Title
                    != input_df.iloc[st.session_state["entry_index"]]["Title"]
                ]
                scores_df = pd.concat([scores_df_existing, scores_df])
            scores_df.to_csv(filepath, index=False)
            st.write("Scores saved successfully!")


# Function to display images in a directory
def display_images(images_dir):
    if os.path.exists(images_dir):
        for image_file in os.listdir(images_dir):
            image_path = os.path.join(images_dir, image_file)
            st.image(image_path, caption="")
    else:
        st.error("Images folder not found")


# Function to display CSV files in a directory
def display_csv_files(csv_dir):
    if os.path.exists(csv_dir):
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]
        if csv_files:
            selected_csv = st.selectbox("Select a CSV file", csv_files)
            if selected_csv:
                csv_path = os.path.join(csv_dir, selected_csv)
                df = pd.read_csv(csv_path)
                st.dataframe(df)
        else:
            st.error("No CSV files found in the directory")
    else:
        st.error("CSV folder not found")


# Main application logic
st.set_page_config(layout="wide")

headings = {
    "Human Evaluation": "An Intuitive Web Tool for Evaluating LLM Paraphrase Performance",
    "Automatic Evaluation Metrics": "Automatic Evaluation Metrics Deployed in this Study",
    "Language Models": "Overview of LLM Studied",
    "Results and Findings": "Comparative Analysis of The Paraphrasing Performance of the LLMs",
    "Contact Us": "",
}

if not st.session_state["loggedin"]:
    login_form()
else:
    username = st.session_state["username"]
    col1, col2, col3, col4 = st.columns([15, 15, 15, 6])
    with col4:
        if st.button("Refresh"):
            st.experimental_rerun()

    input_df = load_data()
    st.sidebar.title("Revolutionize AI Assessments")
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("", list(headings.keys()))

    if menu == "Results and Findings":
        sub_menu = st.sidebar.selectbox(
            "Select Results Type",
            ["Abstract Paraphrase Results", "Sentence Paraphrase Results"],
        )

        if sub_menu == "Abstract Paraphrase Results":
            st.markdown(
                "<h1 style='text-align: center;'>Abstract Paraphrase Results</h1>",
                unsafe_allow_html=True,
            )
            display_csv_files("abstract_para")
        elif sub_menu == "Sentence Paraphrase Results":
            st.markdown(
                "<h1 style='text-align: center;'>Sentence Paraphrase Results</h1>",
                unsafe_allow_html=True,
            )
            display_images("results_images")

    else:
        st.markdown(
            f"<h1 style='text-align: center;'>{headings[menu]}</h1>",
            unsafe_allow_html=True,
        )

    if menu == "Human Evaluation":
        display_model_entries(input_df)
        evaluation_scores()
    elif menu == "Automatic Evaluation Metrics":
        display_images("metrics_images")
    elif menu == "Language Models":
        display_images("models_images")
    elif menu == "Contact Us":
        display_images("about_us")

    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state["username"] = ""
        st.experimental_rerun()
