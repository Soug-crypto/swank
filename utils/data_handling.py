import pandas as pd
import streamlit as st


def upload_and_process_stock_data(uploaded_file):
    """Handles uploading stock data, calculating unique values, and data validation."""
    if uploaded_file is not None:
        try:
            combined_df = pd.read_excel(uploaded_file)

            # 1. Add missing 'price' column if not present, defaulting to 0
            if 'price' not in combined_df.columns:
                combined_df['price'] = 0.0  # Default price to 0
                st.warning("The 'price' column is missing. It has been added and defaulted to 0.")

            # 2. Validate required columns (after adding 'price' if needed)
            required_cols = ['description', 'price']  # Add other required columns
            missing_cols = [col for col in required_cols if col not in combined_df.columns]
            if missing_cols:
                st.error(f"Missing required columns in Excel file: {', '.join(missing_cols)}")
                return None

            # 3. Convert relevant columns to numeric, handle errors
            numeric_cols = ['quantity', 'price']  # 'price' is now always present
            for col in numeric_cols:
                if col in combined_df.columns:
                    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
                    invalid_rows = combined_df[combined_df[col].isna()]
                    if not invalid_rows.empty:
                        st.warning(f"Invalid numeric values found in column '{col}'. These rows will be ignored:\n{invalid_rows}")

            # 3. Calculate unique values efficiently, handle TypeError
            if 'unique_values' not in st.session_state or st.session_state.get('unique_values_file') != uploaded_file:
                unique_values = {}
                for col in combined_df.columns:
                    if col != 'description':  # Or any other columns to exclude
                        unique_vals = combined_df[col].dropna().unique()
                        try:
                            unique_vals = sorted(unique_vals)
                        except TypeError:
                            unique_vals = sorted(unique_vals, key=lambda x: (isinstance(x, str), x))
                        unique_values[col] = unique_vals
                st.session_state['unique_values'] = unique_values
                st.session_state['unique_values_file'] = uploaded_file

            return combined_df

        except ValueError as ve:
            st.error(f"Value error: {ve}. Please check your Excel file.")
            return None
        except Exception as e:
            st.error(f"Error loading/processing Excel: {e}")
            return None

    return None  # Return None if no file is uploaded

def filter_dataframe(df, selected_values):
    """Filters the DataFrame based on selected values."""
    if df is None: # Handle case where df is None
        return None
    filtered_df = df.copy()
    for col, selected_value in selected_values.items():
        if selected_value != 'All':
            filtered_df = filtered_df[filtered_df[col] == selected_value]
    return filtered_df


def display_filtered_dataframe(df, add_product_func):
    """Displays the filtered DataFrame or a message if empty."""
    if df is not None and not df.empty: # Check for both None and empty
        st.dataframe(df, use_container_width=True)
        if st.button("Add Selected Product to Invoice"):
            if df is not None and not df.empty: # Check if DataFrame is not empty or None
                selected_product = df.iloc[0].to_dict()

                if 'description' not in selected_product or pd.isna(selected_product['description']):
                    st.error("Description is missing for the selected product.")
                    return

                description = str(selected_product['description'])

                if 'price' not in selected_product or pd.isna(selected_product['price']):
                    st.error("Price is missing for the selected product.")
                    return
                try:
                    price = float(selected_product['price'])
                except (ValueError, TypeError):
                    st.error("Invalid price format for the selected product.")
                    return

                sub_items = selected_product.get("Sub-items", [])
                if not isinstance(sub_items, list):
                    sub_items = [sub_items] if sub_items else [] # Ensure sub_items is a list


                add_product_func(description, 1, price, sub_items)
                st.success(f"Product '{description}' added.")
            else:
                st.write("No product selected. Please filter the data to select a product.") # Inform user to select a product

    elif df is None:
        st.write("No data loaded. Please upload a file.") # Message for no data loaded
    else:
        st.write("No matching data. Adjust filters.")