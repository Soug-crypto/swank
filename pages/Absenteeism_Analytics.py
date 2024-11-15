import streamlit as st
import plotly.io as pio
from pathlib import Path
import json
# from footer import footer
# from header import header



# with open('./files/style.css') as f:
#     css = f.read()

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)

# st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# header()

@st.cache_data(ttl=3600, max_entries=10)
def load_figure_from_json(json_file: Path):
    """
    Loads a Plotly figure from a JSON file.

    Args:
        json_file (Path): Path to the JSON file containing the Plotly figure.

    Returns:
        plotly.graph_objs.Figure: The Plotly figure object.
        None: If an error occurs during file loading or JSON parsing.
    """
    try:
        with open(json_file, 'r') as f:
            figure_json = json.load(f)
        return pio.from_json(json.dumps(figure_json))
    except FileNotFoundError:
        st.error(f"File {json_file} not found.")
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON in {json_file}.")
    return None


def get_json_files(directory: Path) -> list:
    """
    Retrieves a list of JSON files from a specified directory.

    Args:
        directory (Path): The directory to search for JSON files.

    Returns:
        list: A list of JSON filenames.
    """
    return [f.name for f in directory.glob('*.json')]


def extract_file_types(json_files: list) -> set:
    """
    Extracts distinct file types from a list of JSON filenames.

    Args:
        json_files (list): List of JSON filenames.

    Returns:
        set: A set of unique file types extracted from the filenames.
    """
    return set(f.split('_')[0] for f in json_files)

def main():
    """
    Main function to run the Streamlit app for interactive chart loading.
    """
    # Directory where JSON files are stored
    chart_dir = Path('assets/absentee_graphs')

    # Load available JSON files
    json_files = get_json_files(chart_dir)

    if not json_files:
        st.error("No JSON files found in the specified directory.")
        return

    # Extract distinct file types for filtering
    file_types = extract_file_types(json_files)

    # Streamlit UI components
    st.title("Interactive Absenteeism Data")

    # Search bar to filter charts by name or metadata
    search_query = st.text_input("Search by chart name")
    if search_query:
        filtered_json_files = [f for f in json_files if search_query.lower() in f.lower()]
    else:
        filtered_json_files = json_files

    # Multiselect for filtering by file type
    selected_file_types = st.multiselect("Filter by file type", sorted(file_types))

    # Filter the JSON files based on selected file types
    filtered_json_files = (
        [f for f in filtered_json_files if f.split('_')[0] in selected_file_types]
        if selected_file_types
        else filtered_json_files
    )

    # Ensure there's at least one file to display
    if not filtered_json_files:
        st.info("No charts match the selected filters.")
        return

    # Selectbox for choosing a chart with an option to display all
    chart_options = ['Select a chart...'] + filtered_json_files + ['Show All Charts']
    selected_chart = st.selectbox("Select a chart to display", chart_options)

    # Slider for adjusting chart height
    chart_height = st.slider("Adjust chart height", min_value=400, max_value=1200, value=600)

    # Display the selected chart(s)
    if selected_chart != 'Select a chart...':
        if selected_chart == 'Show All Charts':
            for chart in filtered_json_files:
                chart_path = chart_dir / chart
                
                with st.spinner(f'Loading chart: {chart}...'):
                    fig = load_figure_from_json(chart_path)
                
                if fig:
                    fig.update_layout(height=chart_height)  # Set height; width will be responsive
                    st.plotly_chart(fig, key=chart, use_container_width=True)  # Use container width
                else:
                    st.error(f"Failed to load the chart: {chart}")
        else:
            chart_path = chart_dir / selected_chart
            
            with st.spinner('Loading chart...'):
                fig = load_figure_from_json(chart_path)

            if fig:
                fig.update_layout(height=chart_height)  # Set height; width will be responsive
                st.plotly_chart(fig, key=selected_chart, use_container_width=True)  # Use container width
            else:
                st.error(f"Failed to load the chart: {selected_chart}")
    else:
        st.info("Please select a chart to display.")

    # Footer
    # footer()

if __name__ == "__main__":
    main()