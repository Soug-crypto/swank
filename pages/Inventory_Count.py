import streamlit as st
import pandas as pd
from PIL import Image
import qrcode
from tqdm import tqdm  # for progress indicator
import zxing

def read_qr_code(image):
    try:
        reader = zxing.BarCodeReader()
        barcode = reader.decode(image)
        if barcode:
            return barcode.raw
        return None
    except Exception as e:
        st.error(f"Error decoding QR code: {e}")
        return None

def generate_qr_code(data, size=10, error_correction=qrcode.constants.ERROR_CORRECT_L):
    qr = qrcode.QRCode(version=size, error_correction=error_correction, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img


def validate_csv(file):
    try:
        df = pd.read_csv(file)
        required_columns = {'Product ID', 'Product Name', 'Quantity'}
        if not required_columns.issubset(df.columns):
            raise ValueError(f"Missing required columns: {required_columns - set(df.columns)}")
        return df
    except Exception as e:
        st.error(f"Invalid CSV file: {e}")
        return None

# --- Session State Initialization ---
if 'inventory_df' not in st.session_state:
    st.session_state.inventory_df = pd.DataFrame(columns=['Product ID', 'Product Name', 'Quantity'])
if 'qr_code_data' not in st.session_state:
    st.session_state.qr_code_data = {}
if 'qr_code_history' not in st.session_state:
    st.session_state.qr_code_history = pd.DataFrame(columns=['Product ID', 'Timestamp'])

# --- Sidebar Navigation ---
menu = st.sidebar.selectbox("Select an option", ["Inventory Management", "QR Code Scanning", "QR Code History"])

# --- Inventory Management ---
if menu == "Inventory Management":
    st.title("Inventory Management")
    inventory_file = st.file_uploader("Upload Inventory File (CSV)", type=["csv"])
    if inventory_file:
        with st.spinner("Validating and loading inventory..."):
            df = validate_csv(inventory_file)
            if df is not None:
                st.session_state.inventory_df = df
                st.success("Inventory loaded successfully!")
                st.dataframe(st.session_state.inventory_df)

    if not st.session_state.inventory_df.empty:
        scanned_products = pd.DataFrame(list(st.session_state.qr_code_data.items()), columns=['Product ID', 'Scanned Quantity'])
        st.subheader("Search Inventory")
        search_term = st.text_input("Search by Product ID:")
        filtered_inventory = st.session_state.inventory_df.query("`Product ID`.str.contains(@search_term, case=False)", engine='python') if search_term else st.session_state.inventory_df
        st.dataframe(filtered_inventory)

        
        # Merge to find accounted and missing products
        accounted_products = pd.merge(
            st.session_state.inventory_df, scanned_products, on='Product ID', how='inner'
        )
        
        missing_products = pd.merge(
            st.session_state.inventory_df, scanned_products, on='Product ID', how='left', indicator=True
        ).query('_merge == "left_only"').drop(columns=['_merge'])

        st.subheader("Accounted Products")
        # st.dataframe(accounted_products.style.applymap(lambda x: 'background-color: #D0F0C0;', subset='Product ID'))
        st.dataframe(accounted_products.style.apply(
            lambda row: ['background-color: #FFD700;' if row['Quantity'] < 5 else '' for _ in row], axis=1
        ))

        st.subheader("Missing Products")
        # st.dataframe(missing_products.style.applymap(lambda x: 'background-color: #F08080;', subset='Product ID'))
        st.dataframe(missing_products.style.applymap(
          lambda _: 'background-color: #F08080;', subset=['Product ID']
        ))

        # --- Download Inventory Button ---
        inventory_csv = st.session_state.inventory_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Inventory as CSV",
            inventory_csv,
            "inventory.csv",
            "text/csv",
            key='download-inventory'
        )


# --- QR Code Scanning ---
elif menu == "QR Code Scanning":
    st.title("QR Code Scanning")
    
    # File uploader for multiple QR code images
    uploaded_files = st.file_uploader("Upload QR Code Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        st.info("Decoding QR Codes. Please wait...")
        progress = st.progress(0)  # Initialize progress bar
        
        for i, uploaded_file in enumerate(tqdm(uploaded_files)):
            image = Image.open(uploaded_file)
            product_id = read_qr_code(image)  # Decoding QR code
            
            if product_id:
                # Update or add scanned product
                if product_id in st.session_state.qr_code_data:
                    st.session_state.qr_code_data[product_id] += 1
                else:
                    st.session_state.qr_code_data[product_id] = 1
                
                st.success(f"QR code from '{uploaded_file.name}' decoded: {product_id} (Quantity: {st.session_state.qr_code_data[product_id]})")
                st.toast("QR Codes scanned successfully!", icon="✅")

                
                # Prompt to add the scanned product to history
                if st.checkbox(f"Add '{product_id}' to QR Code History?", key=f"history_{product_id}_{i}"):
                    st.session_state.qr_code_history = pd.concat(
                        [st.session_state.qr_code_history, pd.DataFrame({"Product ID": [product_id], "Timestamp": [pd.Timestamp.now()]})],
                        ignore_index=True
                    )
            else:
                st.warning(f"QR code in '{uploaded_file.name}' could not be decoded.")
            
            # Update progress bar
            progress.progress((i + 1) / len(uploaded_files))

        
        st.success("QR Code scanning completed!")
    
    else:
        st.warning("Please upload QR code images to scan.")


# --- QR Code History ---
elif menu == "QR Code History":
    st.title("QR Code Scanning History")
    search_term = st.text_input("Search by Product ID:")
    filtered_history = st.session_state.qr_code_history.query("`Product ID`.str.contains(@search_term)", engine='python') if search_term else st.session_state.qr_code_history
    st.dataframe(filtered_history)

    if not st.session_state.qr_code_history.empty:
        history_csv = st.session_state.qr_code_history.to_csv(index=False).encode('utf-8')
        st.download_button("Download QR Code History as CSV", history_csv, "qr_code_history.csv", "text/csv")

# --- Add New Product Functionality ---
st.subheader("Add New Product")
new_product_id = st.text_input("Product ID")
new_product_name = st.text_input("Product Name")
new_product_quantity = st.number_input("Quantity", min_value=1, value=1)

if st.button("Add New Product"):
    if new_product_id and new_product_name:
        if new_product_id not in st.session_state.inventory_df['Product ID'].values:
            new_row = pd.DataFrame({"Product ID": [new_product_id], "Product Name": [new_product_name], "Quantity": [new_product_quantity]})
            st.session_state.inventory_df = pd.concat([st.session_state.inventory_df, new_row], ignore_index=True)
            st.success(f"Product '{new_product_name}' added successfully!")
            
            # Display the updated inventory immediately after adding
            st.dataframe(st.session_state.inventory_df)
        else:
            st.error("This Product ID already exists.")
    else:
        st.error("Please complete all product details.")
