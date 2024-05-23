import streamlit as st
import pandas as pd
import os


# Define the models and corresponding csv files
models = {
    "gemini 1.5 pro": "gemini_15_pro.csv",
    "gpt-4o": "gpt_4o.csv",
    "Llama3 70b": "llama3_70b.csv",
}

# Load the users csv file (assuming it's in the same directory)
users_df = pd.read_csv("users.csv", dtype={"password": str})

# Initialize session state for login status (initially False)
if "loggedin" not in st.session_state:
    st.session_state["loggedin"] = False
    st.session_state["username"] = ""  # Store username for display after login

# Initialize session state for entry index (initially 0)
if "entry_index" not in st.session_state:
    st.session_state["entry_index"] = 0


# Function to check user credentials
def check_login(username, password):
    # Check if username exists in the dataframe
    if username in users_df["username"].values:
        # Get the corresponding row for the username
        user_row = users_df[users_df["username"] == username]
        # Validate password
        if user_row["password"].values[0] == password:
            return True
        else:
            st.error("Incorrect password")
    else:
        st.error("Username not found")
    return False


# Login form displayed only if not logged in
st.set_page_config(layout="wide")

if not st.session_state["loggedin"]:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if check_login(username, password):
            st.session_state["loggedin"] = True
            st.session_state["username"] = username
            st.success("Logged in successfully!")
        else:
            st.error("Login failed")

if st.session_state["loggedin"]:
    username = st.session_state["username"]
    # Main application content displayed only if logged in
    st.subheader(f"Welcome back, {username}")
    # Refresh button
    col1, col2, col3, col4 = st.columns([15, 15, 15, 6])
    with col4:
        if st.button("Refresh"):
            st.experimental_rerun()

    # Load the input csv file
    input_df = pd.read_csv("input.csv")

    # Create the sidebar
    st.sidebar.title("Menu")
    menu = st.sidebar.radio(
        "", ("Human Evaluation", "Automatic Evaluation", "Models", "Evaluation Metrics")
    )

    if menu == "Human Evaluation":
        st.sidebar.subheader("Select Model")
        model = st.sidebar.selectbox("", list(models.keys()))

        # Load the selected model's csv file
        model_df = pd.read_csv(models[model])

        # Display the current entry index
        st.markdown(
            f"**Current Entry Index: {st.session_state['entry_index'] + 1} / {len(input_df)}**"
        )

        # Display the selected entries side by side in two columns
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
                value=model_df.iloc[st.session_state["entry_index"]][
                    "ParaphrasedAbstract"
                ],
                height=250,
            )

        # Navigation and index input
        # col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
        # with col1:
        #     if st.button("Previous Entry"):
        #         if st.session_state["entry_index"] > 0:
        #             st.session_state["entry_index"] -= 1
        #             st.experimental_rerun()
        # with col3:
        #     entry_index_input = st.text_input("Go to Entry Index:", "")
        #     if entry_index_input.isdigit():
        #         entry_index = int(entry_index_input) - 1
        #         if 0 <= entry_index < len(input_df):
        #             st.session_state["entry_index"] = entry_index
        #             st.experimental_rerun()
        # with col5:
        #     if st.button("Next Entry"):
        #         if st.session_state["entry_index"] < len(input_df) - 1:
        #             st.session_state["entry_index"] += 1
        #             st.experimental_rerun()
        # Navigation buttons
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

        # Evaluation scores
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

        # Save the scores to a csv file
        col1, col2, col3, col4 = st.columns([15, 15, 15, 8])
        with col4:
            if st.button("Save Scores"):
                scores_df = pd.DataFrame(
                    {
                        "Title": [
                            input_df.iloc[st.session_state["entry_index"]]["Title"]
                        ],
                        "Semantic/Adequacy Score": [semantic_score],
                        "Syntactic/Novelty Score": [syntactic_score],
                        "Fluency Score": [fluency_score],
                        "Overall Score": [overall_score],
                    }
                )
                h_evals_dir = "H_Evals"
                if not os.path.exists(h_evals_dir):
                    os.makedirs(h_evals_dir)
                scores_file = f"{username}_{model}_scores.csv"
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

    elif menu == "Automatic Evaluation":
        st.write("You selected Automatic Evaluation")

    elif menu == "Models":
        st.write("You selected Models")

    elif menu == "Evaluation Metrics":
        st.write("You selected Evaluation Metrics")

    # Logout button in the top right corner
    if st.sidebar.button("Logout"):
        st.session_state["loggedin"] = False
        st.session_state["username"] = ""
        st.experimental_rerun()
