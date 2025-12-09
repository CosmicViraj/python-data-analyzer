import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

# --- Configuration and Setup ---
st.set_page_config(
    page_title="Multi-Graph Data Analyzer (Pandas/NumPy/Matplotlib)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize a global DataFrame and state variables
if 'df' not in st.session_state:
    st.session_state.df = None
if 'show_stats' not in st.session_state:
    st.session_state.show_stats = False
if 'show_plot' not in st.session_state:
    st.session_state.show_plot = False
if 'plot_type' not in st.session_state:
    st.session_state.plot_type = 'Histogram'
if 'plot_col_x' not in st.session_state:
    st.session_state.plot_col_x = None
if 'plot_col_y' not in st.session_state:
    st.session_state.plot_col_y = None


def load_data(uploaded_file):
    """Loads the uploaded CSV file into the session state DataFrame."""
    if uploaded_file is not None:
        try:
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            st.session_state.df = pd.read_csv(stringio)
            st.success(f"File loaded successfully: **{uploaded_file.name}**")
        except Exception as e:
            st.session_state.df = None
            st.error(f"Error loading file. Please check the format. Details: {e}")

def show_statistics(df):
    """Calculates and displays descriptive statistics using Pandas and NumPy."""
    st.subheader("📊 Descriptive Statistics (Pandas)")
    stats_df = df.describe().T
    st.dataframe(stats_df)

    st.subheader("🔢 Additional NumPy Analysis (Range)")
    numerical_cols = stats_df.index.tolist()
    range_data = []
    
    for col in numerical_cols:
        data_range = np.max(df[col]) - np.min(df[col])
        range_data.append({
            "Column": col,
            "Range (Max - Min)": f"{data_range:.2f}"
        })
    
    st.table(pd.DataFrame(range_data).set_index("Column"))

def generate_plot(df, plot_type, col_x, col_y=None):
    """Generates and displays the selected plot type using Matplotlib."""
    
    st.subheader(f"📈 {plot_type} Visualization")
    
    fig, ax = plt.subplots(figsize=(10, 6))

    if plot_type == 'Histogram':
        if not col_x or not pd.api.types.is_numeric_dtype(df[col_x]):
            st.warning("Please select a valid numerical column for the Histogram.")
            return
        
        df[col_x].hist(ax=ax, bins=20, edgecolor='black', color='#1f77b4')
        ax.set_title(f'Histogram of {col_x}')
        ax.set_xlabel(col_x)
        ax.set_ylabel('Frequency')

    elif plot_type == 'Bar Chart':
        if not col_x or not pd.api.types.is_categorical_dtype(df[col_x]) and not pd.api.types.is_object_dtype(df[col_x]):
            st.warning("Please select a valid categorical/text column for the Bar Chart.")
            return

        # Calculate value counts and plot
        counts = df[col_x].value_counts().head(10) # Limit to top 10 categories
        counts.plot(kind='bar', ax=ax, color='#ff7f0e')
        
        ax.set_title(f'Bar Chart of Top Categories in {col_x}')
        ax.set_xlabel(col_x, rotation=0)
        ax.set_ylabel('Count')
        plt.xticks(rotation=45, ha='right')

    elif plot_type == 'Scatter Plot':
        if not col_x or not col_y or not pd.api.types.is_numeric_dtype(df[col_x]) or not pd.api.types.is_numeric_dtype(df[col_y]):
            st.warning("Please select two valid numerical columns for the Scatter Plot.")
            return

        ax.scatter(df[col_x], df[col_y], alpha=0.6, color='#2ca02c')
        ax.set_title(f'Scatter Plot of {col_x} vs {col_y}')
        ax.set_xlabel(col_x)
        ax.set_ylabel(col_y)
    
    plt.grid(axis='y', alpha=0.5)
    st.pyplot(fig)


# =========================================================================
# --- STREAMLIT UI LAYOUT ---
# =========================================================================

st.title("Multi-Graph Data Analysis Web App 📊")
st.markdown("Upload a CSV file and choose from **Histograms**, **Bar Charts**, and **Scatter Plots**.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "1. Upload a CSV File",
    type="csv",
    help="Select a CSV file from your computer."
)

if uploaded_file is not None:
    if st.session_state.df is None or uploaded_file.name != st.session_state.get('last_uploaded_name'):
        load_data(uploaded_file)
        st.session_state.last_uploaded_name = uploaded_file.name

# --- Data Analysis Section ---
df = st.session_state.df

if df is not None:
    st.header("Data Preview")
    st.dataframe(df.head())

    # --- Controls Layout ---
    st.markdown("---")
    st.subheader("2. Analysis & Visualization Controls")
    
    col_stat, col_vis = st.columns([1, 2])
    
    with col_stat:
        # Statistics Button
        if st.button("Show Descriptive Statistics"):
            st.session_state.show_stats = True
            st.session_state.show_plot = False
            
    with col_vis:
        # Plot Type Selector
        plot_type = st.selectbox(
            "Select Plot Type",
            options=['Histogram', 'Bar Chart', 'Scatter Plot'],
            key='plot_type_select'
        )
        st.session_state.plot_type = plot_type
        
        # Determine available columns
        numerical_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
        categorical_cols = [col for col in df.columns if pd.api.types.is_categorical_dtype(df[col]) or pd.api.types.is_object_dtype(df[col])]
        all_cols = df.columns.tolist()

        # Input logic based on selected plot type
        if plot_type == 'Histogram':
            col_x = st.selectbox("Select Numerical Column (X-axis)", options=numerical_cols if numerical_cols else all_cols, key='hist_col_x')
            st.session_state.plot_col_x = col_x
            st.session_state.plot_col_y = None # Reset Y

        elif plot_type == 'Bar Chart':
            col_x = st.selectbox("Select Categorical Column (Categories)", options=categorical_cols if categorical_cols else all_cols, key='bar_col_x')
            st.session_state.plot_col_x = col_x
            st.session_state.plot_col_y = None # Reset Y

        elif plot_type == 'Scatter Plot':
            c1, c2 = st.columns(2)
            with c1:
                col_x = st.selectbox("Select Numerical X Column", options=numerical_cols if numerical_cols else all_cols, key='scatter_col_x')
            with c2:
                col_y = st.selectbox("Select Numerical Y Column", options=numerical_cols if numerical_cols else all_cols, key='scatter_col_y')
            st.session_state.plot_col_x = col_x
            st.session_state.plot_col_y = col_y

        if st.button("Generate Plot"):
            st.session_state.show_stats = False
            st.session_state.show_plot = True

    st.markdown("---")
    
    # --- Output Area ---
    if st.session_state.show_stats:
        show_statistics(df)
        
    if st.session_state.show_plot:
        generate_plot(
            df,
            st.session_state.plot_type,
            st.session_state.plot_col_x,
            st.session_state.plot_col_y
        )

else:
    st.info("Upload a CSV file above to begin the analysis.")