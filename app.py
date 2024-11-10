import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils.pdf_generator import generate_pdf
from utils.data_handling import upload_and_process_stock_data, filter_dataframe, display_filtered_dataframe


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
    st.success(f"Client '{name}' saved.")
    return True

def get_client_info(name):
    """Retrieves client information based on name."""
    return st.session_state.clients.get(name, ("", ""))

def get_client_names():
    """Returns a list of client names."""
    return list(st.session_state.clients.keys())



def add_product(description, quantity, unit_price, sub_items=None):
    """Adds a new product to the invoice."""
    if not description.strip():
        st.error("Product description is required.")
        return False
    if quantity <= 0:
        st.error("Quantity must be greater than zero.")
        return False
    if unit_price < 0:
        st.error("Unit price cannot be negative.")
        return False

    total = quantity * unit_price
    new_product = {
        "Description": description,
        "Quantity": quantity,
        "Unit Price": unit_price,
        "Total": total,
        "Sub-items": sub_items if sub_items else []
    }
    st.session_state.products.append(new_product)
    st.success("Product added.")
    return True

def delete_product(index):
    """Deletes a product from the invoice."""
    if 0 <= index < len(st.session_state.products):
        del st.session_state.products[index]
        st.success("Product deleted.")
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
        st.success("Product updated.")
    else:
        st.error("Invalid product index.")

def calculate_subtotal():
    """Calculates the subtotal of products in the invoice."""
    return sum(product['Total'] for product in st.session_state.products)


# --- Streamlit Components/Sections ---
def display_invoice_customization():
    """Sidebar for invoice customization options."""
    st.sidebar.header("Invoice Customization")
    company_name = st.sidebar.text_input("Company Name", "Your Company Name")
    company_logo = st.sidebar.file_uploader("Upload Logo (optional)", type=["jpg", "jpeg", "png"])
    invoice_id = st.sidebar.text_input("Invoice ID", f"INV-{datetime.now().strftime('%Y%m%d%H%M')}")
    invoice_date = st.sidebar.date_input("Invoice Date", datetime.now().date())
    due_date = st.sidebar.date_input("Due Date", datetime.now().date())
    return company_name, company_logo, invoice_id, invoice_date, due_date


def display_client_information():
    """Section for managing client information."""
    st.sidebar.header("Client Information")
    client_name = st.text_input("Client Name")
    client_contact = st.text_input("Client Contact Info")
    if st.button("Save Client"):
        save_client(client_name, client_contact)

    if get_client_names():
        selected_client = st.selectbox("Select Existing Client", [""] + get_client_names())
        if selected_client:
            client_name, client_contact = selected_client, get_client_info(selected_client)
            st.write(f"Loaded client info: {client_name}, {client_contact}")
    return client_name, client_contact



def display_and_manage_products():
    """Manages product display, stock integration, and manual/dropdown product entry."""

    st.header("Manage Products")

    display_and_manage_existing_products()

    combined_df = upload_and_process_stock_data()
    filter_and_display_stock_data(combined_df)

    st.header("Add New Product")

    add_method = st.radio("Add Method:", ["Manually", "From Stock (Dropdown)"])

    if add_method == "Manually":
        description = st.text_input("Description")
        quantity = st.number_input("Quantity", min_value=1)
        unit_price = st.number_input("Unit Price", min_value=0.0)
        sub_items_text = st.text_area("Sub-items (one per line)")
        sub_items = [line.strip() for line in sub_items_text.splitlines() if line.strip()]

        if st.button("Add Product"):
            add_product(description, quantity, unit_price, sub_items)

    elif add_method == "From Stock (Dropdown)" and combined_df is not None:
        if 'selected_product' not in st.session_state:
            st.session_state.selected_product = {}

        for col in st.session_state['unique_values']:
            if col != "description":
                options = [''] + list(st.session_state['unique_values'][col])
                st.session_state.selected_product[col] = st.selectbox(f"Select {col}:", options, key=f"product_dropdown_{col}")

        description = st.text_input("Description")
        quantity = st.number_input("Quantity", value=1, min_value=1)

        if st.button("Add Product from Stock"):
            filtered_product = combined_df.copy()
            for col, val in st.session_state.selected_product.items():
                if val != '':
                    filtered_product = filtered_product[filtered_product[col] == val]

            if not filtered_product.empty:
                product_data = filtered_product.iloc[0].to_dict()
                add_product(description, quantity, product_data.get('price', 0), product_data.get("Sub-items", []))
                st.success("Product added from stock.")
            else:
                st.warning("No matching product found in stock.")

    products = st.session_state.products
    subtotal = calculate_subtotal()

    if products:
        st.write("### Invoice Products")
        st.table(products)  # Display products in a table format
        st.write(f"**Subtotal:** ${subtotal:.2f}")
    else:
        st.write("No products added yet.")
        subtotal = 0

    return products, subtotal


def display_and_manage_existing_products():
    """Displays, updates, and deletes existing products in the invoice."""
    st.header("Invoice Products")

    if st.session_state.products:
        for i, product in enumerate(st.session_state.products):
            st.write(f"**Product {i + 1}:**")
            col1, col2 = st.columns(2)
            with col1:
                new_description = st.text_input(f"Description {i + 1}", product["Description"])
                new_quantity = st.number_input(f"Quantity {i + 1}", min_value=1, value=product["Quantity"])
                new_unit_price = st.number_input(f"Unit Price {i + 1}", min_value=0.0, value=product["Unit Price"])
                sub_items_text = st.text_area(f"Sub-items {i + 1} (one per line)", "\n".join(product["Sub-items"]))
                new_sub_items = [line.strip() for line in sub_items_text.splitlines() if line.strip()]
            with col2:
                if st.button(f"Update Product {i + 1}"):
                    update_product(i, new_description, new_quantity, new_unit_price, new_sub_items)
                if st.button(f"Delete Product {i + 1}"):
                    delete_product(i)
            st.markdown("---")


def filter_and_display_stock_data(combined_df):
    """Filters and displays the stock data based on user selections."""
    if combined_df is None:  # Handle the case where DataFrame loading failed.
        return

    if 'selected_values' not in st.session_state:
        st.session_state['selected_values'] = {col: 'All' for col in st.session_state['unique_values']}

    for col in st.session_state['unique_values']:
        options = ['All'] + list(st.session_state['unique_values'][col])
        for other_col in st.session_state['unique_values']:
            if other_col != col and st.session_state['selected_values'][other_col] != 'All':
                filtered_df = combined_df[combined_df[other_col] == st.session_state['selected_values'][other_col]]
                options = ['All'] + filtered_df[col].dropna().unique().tolist()

        st.session_state['selected_values'][col] = st.selectbox(
            f"Filter by {col}:", options, index=0, key=f"selectbox_{col}"
        )

    filtered_stock_df = filter_dataframe(combined_df, st.session_state['selected_values'])
    display_filtered_dataframe(filtered_stock_df, add_product)  # Pass add_product as an argument





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

    pdf_file = generate_pdf(
        invoice_id, company_name, temp_logo_path, invoice_date, due_date,
        client_name, client_contact, products, subtotal, discount_amount, total
    )

    if temp_logo_path and os.path.exists(temp_logo_path):  # Cleanup
        os.remove(temp_logo_path)

    with open(pdf_file, "rb") as file:
        st.download_button("Download Invoice PDF", data=file, file_name=pdf_file, mime="application/pdf")
    st.success("PDF generated and ready to download.")


def display_stock_integration():
    """Handles stock data upload, filtering, and adding from stock."""
    st.header("Add Product from Stock")
    combined_df = upload_and_process_stock_data()

    if combined_df is not None:  # Check if DataFrame loading was successful
        filter_and_display_stock_data(combined_df)

        if 'selected_product' not in st.session_state:
            st.session_state.selected_product = {}

        if 'unique_values' in st.session_state: # Check if unique values are available
            for col in st.session_state['unique_values']:
                if col != "description":
                    options = [''] + list(st.session_state['unique_values'][col])
                    st.session_state.selected_product[col] = st.selectbox(f"Select {col}:", options, key=f"product_dropdown_{col}")

        description = st.text_input("Description")
        quantity = st.number_input("Quantity", value=1, min_value=1)

        if st.button("Add Product from Stock"):
            if combined_df is not None: # Check if the dataframe is loaded
                filtered_product = combined_df.copy()
                for col, val in st.session_state.selected_product.items():
                    if val != '':
                        filtered_product = filtered_product[filtered_product[col] == val]

                if not filtered_product.empty:
                    product_data = filtered_product.iloc[0].to_dict()
                    add_product(description, quantity, product_data.get('price', 0), product_data.get("Sub-items", []))
                    st.success("Product added from stock.")
                else:
                    st.warning("No matching product found in stock.")
            else:
                st.error("Please upload stock data first.")


# --- Main Streamlit App ---
def main():
    st.title("Invoice Generator")
    st.sidebar.title("Navigation")

    page = st.sidebar.selectbox("Select a section", ["Invoice Customization", "Client Information", "Products", "Stock Integration", "Discounts"])

    company_name, company_logo, invoice_id, invoice_date, due_date = display_invoice_customization()
    client_name, client_contact = display_client_information()  # Get client info here

    # Initialize variables to avoid NameError
    subtotal = 0
    discount_amount = 0
    total = 0

    if page == "Products":
        display_and_manage_products()
        subtotal = calculate_subtotal()  # Calculate subtotal after managing products
        discount_amount, total = display_discount_section(subtotal) # Calculate discount and total after managing products
    elif page == "Stock Integration":
        display_stock_integration()
        subtotal = calculate_subtotal()  # Calculate subtotal after stock integration
        discount_amount, total = display_discount_section(subtotal) # Calculate discount and total after stock integration
    elif page == "Discounts":
        subtotal = calculate_subtotal()
        discount_amount, total = display_discount_section(subtotal)

    if page in ["Products", "Stock Integration", "Discounts"]:
        if st.button("Generate PDF"):
            with st.spinner("Generating PDF..."):
                generate_and_download_pdf(
                    invoice_id, company_name, company_logo, invoice_date, due_date,
                    client_name, client_contact, st.session_state.products, subtotal, discount_amount, total
                )


if __name__ == "__main__":
    main()
