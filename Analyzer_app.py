import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Configuration and Setup ---
st.set_page_config(
    page_title="Streamlit Data Analyzer (Pandas/NumPy/Matplotlib)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize a global DataFrame state variable
# Streamlit uses st.session_state to maintain variable values across reruns
if 'df' not in st.session_state:
    st.session_state.df = None

def load_data(uploaded_file):
    """Loads the uploaded CSV file into the session state DataFrame."""
    if uploaded_file is not None:
        try:
            # Pandas: Read the uploaded file into a DataFrame
            # Use io.StringIO to read the content of the uploaded file object
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            st.session_state.df = pd.read_csv(stringio)
            st.success(f"File loaded successfully: **{uploaded_file.name}**")
        except Exception as e:
            st.session_state.df = None
            st.error(f"Error loading file. Please check the format. Details: {e}")

def show_statistics(df):
    """Calculates and displays descriptive statistics using Pandas and NumPy."""
    st.subheader("📊 Descriptive Statistics (Pandas)")

    # 1. Pandas: Generate descriptive statistics
    stats_df = df.describe().T # Transpose for better web display

    # Streamlit displays DataFrames beautifully
    st.dataframe(stats_df)

    # 2. NumPy: Example of explicit NumPy usage: calculating range (Max - Min)
    st.subheader("🔢 Additional NumPy Analysis (Range)")

    numerical_cols = stats_df.index.tolist()
    range_data = []
    
    # Iterate through numerical columns to calculate range
    for col in numerical_cols:
        # NumPy: Calculate range using max and min
        data_range = np.max(df[col]) - np.min(df[col])
        range_data.append({
            "Column": col,
            "Range (Max - Min)": f"{data_range:.2f}"
        })
    
    # Display NumPy results in a clean Streamlit table
    st.table(pd.DataFrame(range_data).set_index("Column"))

def visualize_data(df, column_name):
    """Generates and displays a histogram for the selected numerical column using Matplotlib."""
    if column_name and column_name in df.columns and pd.api.types.is_numeric_dtype(df[column_name]):
        st.subheader(f"📈 Histogram of **{column_name}**")
        
        # 3. Matplotlib: Create a figure for the histogram
        fig, ax = plt.subplots(figsize=(8, 5))
        
        # Use Matplotlib to plot the histogram
        df[column_name].hist(ax=ax, bins=20, edgecolor='black', color='#1f77b4')

        ax.set_title(f'Histogram of {column_name}', fontsize=16)
        ax.set_xlabel(column_name, fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        plt.grid(axis='y', alpha=0.5)

        # 4. Streamlit & Matplotlib Integration: Display the figure
        st.pyplot(fig)
    else:
        st.warning("Please select a valid numerical column to plot.")

# =========================================================================
# --- STREAMLIT UI LAYOUT ---
# =========================================================================

st.title("Data Analysis Web App")
st.markdown("Upload a CSV file to analyze and visualize your data using **Pandas**, **NumPy**, and **Matplotlib**.")

# --- File Uploader (Equivalent to Tkinter's Load Button/Dialog) ---
uploaded_file = st.file_uploader(
    "1. Upload a CSV File",
    type="csv",
    help="Select a CSV file from your computer."
)

# Automatically load data when a file is uploaded
if uploaded_file is not None:
    # Check if the file has changed to avoid unnecessary re-reading
    if st.session_state.df is None or uploaded_file.name != st.session_state.get('last_uploaded_name'):
        load_data(uploaded_file)
        st.session_state.last_uploaded_name = uploaded_file.name

# --- Data Analysis Section ---
df = st.session_state.df

if df is not None:
    st.header("Data Preview")
    st.dataframe(df.head()) # Display the first few rows

    # Create two columns for the analysis and visualization controls
    col1, col2 = st.columns([1, 1])
    
    # Column 1: Statistics Button (Equivalent to Tkinter's Analyze Button)
    with col1:
        if st.button("2. Show Descriptive Statistics"):
            st.session_state.show_stats = True
            st.session_state.show_plot = False # Clear plot if showing stats
        
    # Column 2: Visualization Controls (Equivalent to Tkinter's Column Selector and Plot Button)
    numerical_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    
    with col2:
        if numerical_cols:
            selected_col = st.selectbox(
                "3. Select a Numerical Column for Histogram",
                options=numerical_cols,
                index=0
            )
            if st.button("Generate Histogram"):
                st.session_state.show_stats = False # Clear stats if showing plot
                st.session_state.show_plot = True
                st.session_state.plot_col = selected_col
        else:
            st.warning("No numerical columns found for visualization.")

    st.markdown("---")
    
    # --- Output Area (Display results based on button clicks) ---
    if st.session_state.get('show_stats', False):
        show_statistics(df)
        
    if st.session_state.get('show_plot', False) and st.session_state.get('plot_col'):
        visualize_data(df, st.session_state.plot_col)

else:
    st.info("Upload a CSV file above to begin the analysis.")