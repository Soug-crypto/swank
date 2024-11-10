import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils.pdf_generator import generate_pdf
from utils.data_handling import upload_and_process_stock_data

# Initialize session state for clients and products
if "clients" not in st.session_state:
    st.session_state.clients = {}

if "products" not in st.session_state:
    st.session_state.products = []

def save_client(name, contact):
    """Saves a client to the session state."""
    if not name or not contact:
        st.error("Client name and contact information are required.")
        return False
    st.session_state.clients[name] = contact
    st.success(f"Client '{name}' saved.", icon="✅")
    return True

def get_client_info(name):
    """Retrieves client information based on name."""
    return st.session_state.clients.get(name, ("", ""))

def get_client_names():
    """Returns a list of client names."""
    return list(st.session_state.clients.keys())


def add_product(description, quantity, unit_price, sub_items=None):
    """Adds a new product to the invoice."""
    
    # Ensure description is a string
    if not isinstance(description, str):
        description = str(description) if not pd.isna(description) else ""
    
    # Validate the description
    if not description.strip():
        st.error("Product description is required.")
        return False

    # Validate quantity and unit price
    if quantity <= 0:
        st.error("Quantity must be greater than zero.")
        return False
    if unit_price < 0:
        st.error("Unit price cannot be negative.")
        return False

    total = quantity * unit_price
    new_product = {
        "Description": description.strip(),
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Total": total,
        "Sub-items": sub_items if sub_items else []
    }

    # Add the new product to the session state
    if "products" not in st.session_state:
        st.session_state.products = []

    st.session_state.products.append(new_product)
    st.success("Product added.", icon="✅")
    return True


def delete_product(index):
    """Deletes a product from the invoice."""
    if 0 <= index < len(st.session_state.products):
        del st.session_state.products[index]
        st.success("Product deleted.", icon="❌")
    else:
        st.error("Invalid product index.")

def update_product(index, description, quantity, unit_price, sub_items):
    """Updates a product in the invoice."""
    if 0 <= index < len(st.session_state.products):
        product = st.session_state.products[index]
        product["Description"] = description
        product["Quantity"] = quantity
        product["Unit Price"] = unit_price
        product["Total"] = quantity * unit_price
        product["Sub-items"] = sub_items
        st.success("Product updated.", icon="🔄")
    else:
        st.error("Invalid product index.")

def calculate_subtotal():
    """Calculates the subtotal of products in the invoice."""
    return sum(product['Total'] for product in st.session_state.products)

# --- Streamlit Components/Sections ---
def display_invoice_customization():
    """Sidebar for invoice customization options."""
    st.sidebar.header("Invoice Customization")
    company_name = st.sidebar.text_input("Company Name", "Arkan Limited")
    company_logo = st.sidebar.file_uploader("Upload Logo (optional)", type=["jpg", "jpeg", "png"])
    invoice_id = st.sidebar.text_input("Invoice ID", f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
    invoice_date = st.sidebar.date_input("Invoice Date", datetime.now().date())
    due_date = st.sidebar.date_input("Due Date", datetime.now().date())
    return company_name, company_logo, invoice_id, invoice_date, due_date

def display_client_information():
    """Sidebar for managing client information."""
    st.sidebar.header("Client Information")
    client_name = st.sidebar.text_input("Client Name", "")
    client_contact = st.sidebar.text_input("Client Contact Info", "")
    
    if st.sidebar.button("Save Client"):
        save_client(client_name, client_contact)

    if get_client_names():
        selected_client = st.sidebar.selectbox("Select Existing Client", [""] + get_client_names())
        if selected_client:
            client_name, client_contact = selected_client, get_client_info(selected_client)
            st.sidebar.write(f"Loaded client info: **{client_name}**, **{client_contact}**")

    return client_name, client_contact

def display_and_manage_existing_products():
    """Displays, updates, and deletes existing products in the invoice."""
    st.header("Invoice Products")
    
    if st.session_state.products:
        for i, product in enumerate(st.session_state.products):
            st.write(f"### Product {i + 1}")
            col1, col2 = st.columns(2)
            with col1:
                new_description = st.text_input(f"Description {i + 1}", product["Description"], key=f"desc_{i}")
                new_quantity = st.number_input(f"Quantity {i + 1}", min_value=1, value=product["Quantity"], key=f"qty_{i}")
                new_unit_price = st.number_input(f"Unit Price {i + 1}", min_value=0.0, value=product["Unit Price"], key=f"price_{i}")
                sub_items_text = st.text_area(f"Sub-items {i + 1} (one per line)", "\n".join(product["Sub-items"]), key=f"subitems_{i}")
                new_sub_items = [line.strip() for line in sub_items_text.splitlines() if line.strip()]
            with col2:
                if st.button(f"Update Product {i + 1}", key=f"update_{i}"):
                    update_product(i, new_description, new_quantity, new_unit_price, new_sub_items)
                if st.button(f"Delete Product {i + 1}", key=f"delete_{i}"):
                    if st.confirm(f"Are you sure you want to delete {product['Description']}?"):
                        delete_product(i)
            st.markdown("---")
    else:
        st.write("No products added yet.")

def update_dropdown_options(selected_filters, combined_df, current_col):
    """Updates dropdown options based on selected filters, excluding the current column."""
    filtered_df = combined_df.copy()
    for col, val in selected_filters.items():
        if val and col != current_col:  # Exclude the current column from filtering
            filtered_df = filtered_df[filtered_df[col] == val]
    return filtered_df

def searchable_selectbox(label, options):
    """Creates a searchable dropdown."""
    search_term = st.text_input(f"Search {label}:")
    
    # Convert options to strings and filter based on the search term
    filtered_options = [str(opt) for opt in options if opt is not None and str(opt) != '']
    filtered_options = [opt for opt in filtered_options if search_term.lower() in opt.lower()]
    
    # Ensure the selectbox has a default option if no matches are found
    if filtered_options:
        return st.selectbox(label, filtered_options)
    else:
        return st.selectbox(label, ["No matches found"])

def validate_product_selection(filtered_product):
    """Validates if the filtered product exists."""
    if filtered_product.empty:
        st.warning("No matching product found. Please adjust your selections.")
        return False
    return True


def load_data(uploaded_file):
    try:
        # Get the file extension using the name attribute
        file_extension = uploaded_file.name.split('.')[-1]  # Get the file extension

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xls', 'xlsx']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
        
        df = df.fillna("<Missing>")  # Convert NaN to a unique placeholder
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def apply_filters(df, filters):
    filtered_df = df.copy()
    for col, selected_values in filters.items():
        if "All" not in selected_values:
            filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
    return filtered_df


def display_and_manage_products():
    """Manages product display, stock integration, and manual product entry with enhanced UI/UX."""
    
    st.title("📦 Product Management")
    st.sidebar.header("Stock Data Integration")
    uploaded_file = st.sidebar.file_uploader("Upload Stock Data (CSV or Excel)", type=["csv", "xls", "xlsx"])
    
    combined_df = None
    if uploaded_file:
        with st.spinner("Processing stock data..."):
            combined_df = load_data(uploaded_file)
            if combined_df is None:
                st.error("❌ Failed to load data. Please check the file format.")
                return  # Stop if data loading fails

    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("🆕 Add New Product")
        add_method = st.radio("Add Method", ["Manually", "From Stock (Multi-Select)"], horizontal=True)

        if add_method == "Manually":
            description = st.text_input("Description", placeholder="Enter product description...")
            quantity = st.number_input("Quantity", min_value=1)
            unit_price = st.number_input("Unit Price ($)", min_value=0.0)
            sub_items = st.text_area("Sub-items (Optional)", placeholder="List sub-items, one per line")

            if st.button("Add Product", type="primary"):
                if description and quantity > 0 and unit_price >= 0:
                    add_product(description, quantity, unit_price, sub_items.splitlines())
                    st.success("🎉 Product added successfully!")
                else:
                    st.error("❌ Please fill in all fields correctly.")

        elif add_method == "From Stock (Multi-Select)":
            if combined_df is None or combined_df.empty:
                st.warning("⚠️ Please upload stock data first.")
            else:
                filters = {}
                columns = combined_df.columns.tolist()

                for col in columns:
                    unique_values = ["All"] + sorted(combined_df[col].astype(str).unique())
                    selected_values = st.multiselect(f"Filter by {col}", unique_values, default=["All"], key=f"filter_{col}")
                    filters[col] = selected_values

                # Clear Filters Button
                if st.button("Clear Filters"):
                    for col in columns:
                        st.session_state[f"filter_{col}"] = ["All"]

                filtered_product = apply_filters(combined_df, filters)

                if not filtered_product.empty:
                    st.subheader("Filtered Products")
                    product_options = filtered_product['description'].tolist()
                    selected_product = st.selectbox("Select a Product", product_options)

                    if selected_product:
                        product_info = filtered_product[filtered_product['description'] == selected_product].iloc[0]
                        st.text_input("Description", value=product_info['description'], disabled=True)
                        stock_qty = st.number_input("Quantity", min_value=1)

                        if st.button("Add Product from Stock", type="primary"):
                            add_product(product_info['description'], stock_qty, product_info.get('price', 0), product_info.get("Sub-items", []))
                            st.success("✅ Product added from stock.")
                else:
                    st.warning("No products match the current filters.")

    with col2:
        st.subheader("📃 Invoice Summary")
        products = st.session_state.get("products", [])
        subtotal = calculate_subtotal()

        if products:
            for idx, product in enumerate(products):
                col1, col2 = st.columns([4, 1])
                col1.write(f"{product['Description']} (Qty: {product['Quantity']}, Price: ${product['Unit Price']:.2f})")
                if col2.button("Edit", key=f"edit_{idx}"):
                    edit_product(idx)  # Function to edit the product
                if col2.button("Delete", key=f"delete_{idx}"):
                    delete_product(idx)  # Function to delete the product
            
            st.metric("Subtotal", f"${subtotal:.2f}")
        else:
            st.info("No products added yet. Start adding products.")

    return products, subtotal

def edit_product(index):
    """Function to edit the selected product."""
    if 'products' not in st.session_state or index >= len(st.session_state.products):
        st.error("❌ Product not found.")
        return

    product = st.session_state.products[index]

    # Input fields for editing product details
    new_description = st.text_input("Edit Description", value=product.get('Description', ''))
    new_quantity = st.number_input("Edit Quantity", value=product.get('Quantity', 1), min_value=1)
    new_price = st.number_input("Edit Unit Price ($)", value=product.get('Unit Price', 0.0), min_value=0.0)

    # Edit Sub-items
    sub_items = product.get('Sub-items', [])
    new_sub_items = []
    for i, sub_item in enumerate(sub_items):
        new_sub_item = st.text_input(f"Edit Sub-item {i + 1}", value=sub_item)
        new_sub_items.append(new_sub_item)

    # Button to add a new sub-item
    if st.button("Add Sub-item"):
        new_sub_items.append("")  # Add an empty field for the new sub-item

    # Place the Update button here
    if st.button("Update Product"):
        # Update the product in the session state
        st.session_state.products[index] = {
            'Description': new_description,
            'Quantity': new_quantity,
            'Unit Price': new_price,  # Allow zero price
            'Total': new_quantity * new_price,  # Recalculate total
            'Sub-items': new_sub_items  # Update with new sub-items
        }
        st.success("✅ Product updated successfully!")

def delete_product(index):
    """Function to delete the selected product."""
    del st.session_state.products[index]
    st.success("✅ Product deleted successfully!")

def edit_product(index):
    """Function to edit the selected product."""
    if 'products' not in st.session_state or index >= len(st.session_state.products):
        st.error("❌ Product not found.")
        return

    product = st.session_state.products[index]
    st.write("Editing product data:", product)  # Debugging output

    # Ensure the unit price is a float
    unit_price = float(product.get('Unit Price', 0.0))
    
    # Input fields for editing product details
    new_description = st.text_input("Edit Description", value=product.get('Description', ''))
    new_quantity = st.number_input("Edit Quantity", value=product.get('Quantity', 1), min_value=1)
    new_price = st.number_input("Edit Unit Price ($)", value=unit_price, min_value=0.0)

    # Edit Sub-items
    sub_items = product.get('Sub-items', [])
    new_sub_items = []
    for i, sub_item in enumerate(sub_items):
        new_sub_item = st.text_input(f"Edit Sub-item {i + 1}", value=sub_item)
        new_sub_items.append(new_sub_item)

    # Button to add a new sub-item
    if st.button("Add Sub-item"):
        new_sub_items.append("")  # Add an empty field for the new sub-item

    # Update button
    if st.button("Update Product"):
        # Update the product in the session state
        st.session_state.products[index] = {
            'Description': new_description,
            'Quantity': new_quantity,
            'Unit Price': new_price,  # Allow zero price
            'Total': new_quantity * new_price,  # Recalculate total
            'Sub-items': new_sub_items  # Update with new sub-items
        }
        st.success("✅ Product updated successfully!")

def generate_and_download_pdf(invoice_id, company_name, logo_path, invoice_date, due_date, client_name, client_contact, products, subtotal, discount_amount, total):
    """Generates and provides a download link for the PDF invoice."""
    if not products:
        st.error("Please add at least one product before generating an invoice.")
        return

    # Handle logo upload inside the PDF generation function
    temp_logo_path = None  # Initialize
    if logo_path is not None:
        temp_logo_path = f"temp_logo.{logo_path.type.split('/')[1]}"
        with open(temp_logo_path, "wb") as f:
            f.write(logo_path.getbuffer())

    try:
        pdf_file = generate_pdf(
            invoice_id, company_name, temp_logo_path, invoice_date, due_date,
            client_name, client_contact, products, subtotal, discount_amount, total
        )
        with open(pdf_file, "rb") as file:
            st.download_button("Download Invoice PDF", data=file, file_name=pdf_file, mime="application/pdf")
        st.success("PDF generated and ready to download.", icon="✅")
    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}", icon="⚠️")
    finally:
        if temp_logo_path and os.path.exists(temp_logo_path):  # Cleanup
            os.remove(temp_logo_path)


def display_discount_section(subtotal):
    """Section for applying discounts (percentage or amount)."""
    st.header("Discount")
    discount_type = st.radio("Discount Type", ["Percentage", "Amount"])

    # Initialize discount_amount and discount_percentage
    discount_amount = 0
    discount_percentage = 0

    if subtotal == 0:
        st.warning("Subtotal is zero. Discounts cannot be applied.")
    else:
        if discount_type == "Percentage":
            discount_percentage = st.number_input("Discount (%)", min_value=0.0, max_value=100.0, value=0.0)
            discount_amount = (discount_percentage / 100) * subtotal
        else:  # discount_type == "Amount"
            discount_amount = st.number_input("Discount Amount", min_value=0.0, value=0.0)
            discount_percentage = (discount_amount / subtotal) * 100 if subtotal > 0 else 0

    total = subtotal - discount_amount  # Calculate total once
    st.write(f"**Discount Type:** {discount_type}")
    st.write(f"**Discount Percentage:** {discount_percentage:.2f}%")
    st.write(f"**Discount Amount:** ${discount_amount:.2f}")
    st.write(f"**Total:** ${total:.2f}")
    return discount_amount, total

# --- Main Streamlit App ---
def main():
    st.set_page_config(page_title="Invoice Generator", page_icon="🧾", layout="wide")
    
    st.title("Invoice Generator")
    st.sidebar.title("Navigation")

    page = st.sidebar.selectbox("Select a section", ["Products", "Discounts"])

    company_name, company_logo, invoice_id, invoice_date, due_date = display_invoice_customization()
    client_name, client_contact = display_client_information()  # Get client info here

    # Initialize variables to avoid NameError
    subtotal = 0
    discount_amount = 0
    total = 0

    if page == "Products":
        display_and_manage_products()
        subtotal = calculate_subtotal()  # Calculate subtotal after managing products
    elif page == "Discounts":
        subtotal = calculate_subtotal()
        discount_amount, total = display_discount_section(subtotal)

    if page in ["Products", "Discounts"]:
        if st.button("Generate PDF"):
            with st.spinner("Generating PDF..."):
                generate_and_download_pdf(
                    invoice_id, company_name, company_logo, invoice_date, due_date,
                    client_name, client_contact, st.session_state.products, subtotal, discount_amount, total
                )

if __name__ == "__main__":
    main()