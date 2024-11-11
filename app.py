import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

from utils.pdf_generator import generate_pdf
from utils.data_handling import upload_and_process_stock_data


st.set_page_config(
    page_title="Product Management",
    layout="wide"  # Options: "centered", "wide"
)
# Initialize session state for clients and products
if "clients" not in st.session_state:
    st.session_state.clients = {}

if "products" not in st.session_state:
    st.session_state.products = []


if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = None  # Tracks which product is being edited

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
    return True

def calculate_subtotal():
    """Calculates the subtotal of products in the invoice."""
    return sum(product['Total'] for product in st.session_state.products)

# --- Streamlit Components/Sections ---
def display_invoice_customization():
    """Sidebar for invoice customization options with fallback to default logo."""
    st.sidebar.header("Invoice Customization")
    
    company_name = st.sidebar.text_input("Company Name", "Arkan Limited")
    company_logo = st.sidebar.file_uploader("Upload Logo", type=["jpg", "jpeg", "png"])
    
    # Fallback to default logo if no file is uploaded
    if not company_logo:
        default_logo_path = os.path.join("assets", "logo.png")
        if os.path.exists(default_logo_path):
            company_logo = default_logo_path
    
    # Display the logo
    if company_logo:
        st.sidebar.image(Image.open(company_logo), caption="Company Logo", use_column_width=True)
    
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
    """Manages the entire product display and management workflow."""
    st.title("📦 Product Management")
    
    # Sidebar for stock data
    combined_df = display_sidebar()
    
    # Product entry section
    col1, col2 = st.columns([1, 2], gap="large")
    
    with col1:
        display_product_entry_section(combined_df)
    
    with col2:
        display_invoice_summary()


def display_sidebar():
    """Handles stock data integration via file upload."""
    st.sidebar.header("Stock Data Integration")
    uploaded_file = st.sidebar.file_uploader("Upload Stock Data (CSV or Excel)", type=["csv", "xls", "xlsx"])

    if uploaded_file:
        with st.spinner("Processing stock data..."):
            return load_data(uploaded_file)
    
    return None


def display_product_entry_section(combined_df):
    """Displays the interface for adding new products manually or from stock."""
    st.subheader("🆕 Add New Product")
    add_method = st.radio("Add Method", ["Manually", "From Stock (Multi-Select)"], horizontal=True)

    if add_method == "Manually":
        display_manual_product_entry()
    elif add_method == "From Stock (Multi-Select)":
        display_stock_product_entry(combined_df)

def display_manual_product_entry():
    """Handles manual product entry."""
    description = st.text_input("Description", placeholder="Enter product description...")
    quantity = st.number_input("Quantity", min_value=1)
    unit_price = st.number_input("Unit Price ($)", min_value=0.0)
    sub_items = st.text_area("Sub-items (Optional)", placeholder="List sub-items, one per line")
    
    if st.button("Add Product", type="primary"):
        if add_product(description, quantity, unit_price, sub_items.splitlines()):
            st.success("🎉 Product added successfully!")


def display_stock_product_entry(combined_df):
    """Handles product entry from stock data with filtering options."""
    if combined_df is None or combined_df.empty:
        st.warning("⚠️ Please upload stock data first.")
        return
    
    filters = {col: st.multiselect(f"Filter by {col}", ["All"] + sorted(combined_df[col].astype(str).unique()), default=["All"]) for col in combined_df.columns}

    if st.button("Clear Filters"):
        for col in filters.keys():
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

# def display_invoice_summary():
#     """Displays the list of added products and the invoice summary."""
#     st.subheader("📃 Invoice Summary")
#     products = st.session_state.get("products", [])
#     subtotal = calculate_subtotal()

#     if products:
#         for idx, product in enumerate(products):
#             col1, col2 = st.columns([4, 1])
#             col1.write(f"{product['Description']} (Qty: {product['Quantity']}, Price: ${product['Unit Price']:.2f})")
#             if col2.button("Edit", key=f"edit_{idx}"):
#                 edit_product(idx)
#             if col2.button("Delete", key=f"delete_{idx}"):
#                 delete_product(idx)

#         st.metric("Subtotal", f"${subtotal:.2f}")
#     else:
#         st.info("No products added yet. Start adding products.")





def delete_product(index):
    """Deletes a product from the invoice."""
    if 0 <= index < len(st.session_state.products):
        del st.session_state.products[index]
        st.success("Product deleted.", icon="❌")
    else:
        st.error("Invalid product index.")

# def edit_product(index):
#     """Function to edit the selected product."""
#     # Check if products exist in session state
#     if 'products' not in st.session_state or index >= len(st.session_state.products):
#         st.error("❌ Product not found.")
#         return

#     product = st.session_state.products[index]
#     st.write("Editing product data:", product)  # Display current product data for debugging

#     # Ensure the unit price is a float
#     try:
#         unit_price = float(product.get('Unit Price', 0.0))
#     except (ValueError, TypeError):
#         st.error("❌ Invalid unit price. Please check the product data.")
#         return

#     # Input fields for editing product details
#     new_description = st.text_input("Edit Description", value=product.get('Description', ''))
#     new_quantity = st.number_input("Edit Quantity", value=product.get('Quantity', 1), min_value=1)
    
#     try:
#         new_price = float(st.number_input("Edit Unit Price ($)", value=unit_price, min_value=0.0))
#     except (ValueError, TypeError):
#         st.error("❌ Invalid price. Please enter a valid number.")
#         return

#     # Edit Sub-items
#     sub_items = product.get('Sub-items', [])
#     new_sub_items = []
#     for i, sub_item in enumerate(sub_items):
#         new_sub_item = st.text_input(f"Edit Sub-item {i + 1}", value=sub_item)
#         new_sub_items.append(new_sub_item)

#     # Flag to track if a change was made
#     changes_made = False

#     # Button to add a new sub-item
#     if st.button("Add Sub-item"):
#         new_sub_items.append("")  # Add an empty field for a new sub-item
#         changes_made = True  # Set flag indicating a change has occurred

#     # Update button with validation
#     if st.button("Update Product"):
#         # Validation checks
#         if not new_description.strip():
#             st.error("❌ Description cannot be empty.")
#             return
#         if new_quantity <= 0:
#             st.error("❌ Quantity must be a positive integer.")
#             return

#         # Update the product in the session state
#         st.session_state.products[index] = {
#             'Description': new_description,
#             'Quantity': new_quantity,
#             'Unit Price': new_price,  # Allow zero price
#             'Total': new_quantity * new_price,  # Recalculate total
#             'Sub-items': new_sub_items  # Update with new sub-items
#         }
#         st.success("✅ Product updated successfully!")

# def edit_product(index):
#     """Function to edit the selected product using st.form."""
#     if 'products' not in st.session_state or not (0 <= index < len(st.session_state.products)):
#         st.error("Product not found.")
#         return

#     product = st.session_state.products[index]

#     with st.form(key=f"edit_form_{index}"):
#         new_description = st.text_input("Description", value=product.get('Description', ''), key=f"description_{index}")
#         new_quantity = st.number_input("Quantity", value=product.get('Quantity', 1), min_value=1, key=f"quantity_{index}")
#         unit_price = float(product.get('Unit Price', 0.0))
#         new_price = st.number_input("Unit Price ($)", value=unit_price, min_value=0.0, step=0.01, format="%.2f", key=f"price_{index}")

#         new_sub_items = product.get('Sub-items', []).copy()
#         with st.expander("Sub-items"):
#             for i in range(len(new_sub_items)):
#                 new_sub_items[i] = st.text_input(f"Sub-item {i+1}", value=new_sub_items[i], key=f"sub_item_{index}_{i}")
#             new_sub_item_input = st.text_input("New Sub-item", key=f"new_sub_item_input_{index}")  # For adding new sub-items

#         if st.form_submit_button("Update Product"):
#             try:
#                 new_quantity = int(new_quantity)
#                 new_price = float(new_price)
#             except ValueError:
#                 st.error("Quantity and Unit Price must be valid numbers.")
#                 return

#             if not new_description.strip():
#                 st.error("Description cannot be empty.")
#                 return
#             if new_quantity <= 0:
#                 st.error("Quantity must be a positive integer.")
#                 return
            
#             if new_sub_item_input.strip():  # Add new sub-item if input is not empty
#                 new_sub_items.append(new_sub_item_input)


#             st.session_state.products[index].update({
#                 'Description': new_description,
#                 'Quantity': new_quantity,
#                 'Unit Price': new_price,
#                 'Total': new_quantity * new_price,
#                 'Sub-items': new_sub_items  # Assign the updated sub-items list
#             })
#             st.success("Product updated successfully!")


# def display_invoice_summary():
#     """Displays the list of added products and the invoice summary."""
#     st.subheader("Invoice Summary")
#     products = st.session_state.get("products", [])
#     subtotal = calculate_subtotal()

#     if products:
#         for idx, product in enumerate(products):
#             col1, col2 = st.columns([4, 1])
#             try:
#                 col1.write(f"{product['Description']} (Qty: {product['Quantity']}, Price: ${product['Unit Price']:.2f})")
#             except KeyError as e:
#                 st.error(f"Error displaying product: Missing key {e}. Please check your product data.")
#                 continue

#             if col2.button("Edit", key=f"edit_{idx}"):
#                 edit_product(idx)  # Call edit_product (no reruns needed because of st.form)

#             if col2.button("Delete", key=f"delete_{idx}"):
#                 delete_product(idx)

#         st.metric("Subtotal", f"${subtotal:.2f}")
#     else:
#         st.info("No products added yet. Start adding products.")




def edit_product(index):
    """Function to edit a selected product."""
    st.session_state.edit_mode = index
    st.session_state.temp_edit = st.session_state.products[index].copy()

    st.write("### Edit Product")

    temp_product = st.session_state.temp_edit

    # Append index to each key for uniqueness
    temp_product['Description'] = st.text_input(
        "Description", value=temp_product['Description'], key=f'edit_description_{index}'
    )
    temp_product['Quantity'] = st.number_input(
        "Quantity", value=temp_product['Quantity'], min_value=1, key=f'edit_quantity_{index}'
    )
    temp_product['Unit Price'] = st.number_input(
        "Unit Price", value=temp_product['Unit Price'], min_value=0.0, step=0.01, key=f'edit_price_{index}'
    )
    temp_product['Total'] = temp_product['Quantity'] * temp_product['Unit Price']

    with st.expander("Edit Sub-items"):
        for i, sub_item in enumerate(temp_product['Sub-items']):
            temp_product['Sub-items'][i] = st.text_input(
                f"Sub-item {i + 1}", value=sub_item, key=f'edit_sub_item_{index}_{i}'
            )
        new_sub_item = st.text_input("New Sub-item", key=f'edit_new_sub_item_{index}')
        if new_sub_item.strip():
            temp_product['Sub-items'].append(new_sub_item.strip())

    if st.button("Save", key=f'save_edit_{index}'):
        save_edit(index)
    if st.button("Cancel", key=f'cancel_edit_{index}'):
        cancel_edit()



def save_edit(index):
    """Saves the edited product back to the main list."""
    st.session_state.products[index] = st.session_state.temp_edit
    st.session_state.edit_mode = None
    st.success("Product updated successfully!")


def cancel_edit():
    """Closes the modal without saving changes."""
    st.session_state.edit_mode = None
    st.info("Edit canceled.")


st.title("Product Management")

# Display products with an edit button
for i, product in enumerate(st.session_state.products):
    st.write(f"**Product {i + 1}:** {product['Description']}")
    st.write(f"Quantity: {product['Quantity']}, Unit Price: ${product['Unit Price']:.2f}")
    st.write(f"Total: ${product['Total']:.2f}")
    st.write(f"Sub-items: {', '.join(product['Sub-items'])}")
    st.button("Edit", key=f"edit_button_{i}", on_click=edit_product, args=(i,))

# Show the edit form if a product is being edited
if st.session_state.edit_mode is not None:
    edit_product(st.session_state.edit_mode)




def display_invoice_summary():
    """Displays the list of added products and the invoice summary with debugging."""
    st.subheader("Invoice Summary")

    products = st.session_state.get("products", [])

    subtotal = calculate_subtotal()

    if products:
        for idx, product in enumerate(products):
            col1, col2 = st.columns([4, 1])
            try:
                col1.write(f"{product['Description']} (Qty: {product['Quantity']}, Price: ${product['Unit Price']:.2f})")

                # Displaying sub-items if they exist
                if product['Sub-items']:
                    sub_items_str = ', '.join(product['Sub-items'])
                    col1.write(f"Sub-items: {sub_items_str}")

            except KeyError as e:
                st.error(f"Error displaying product: Missing key '{e}'. Please check your product data. Product: {product}") # More informative error
                continue

            if col2.button("Edit", key=f"edit_{idx}"):
                try:
                    edit_product(idx)
                except Exception as e:
                    st.error(f"Error editing product: {e}")


            if col2.button("Delete", key=f"delete_{idx}"):
                delete_product(idx)


        st.metric("Subtotal", f"${subtotal:.2f}")
    else:
        st.info("No products added yet. Start adding products.")

def generate_and_download_pdf(invoice_id, company_name, logo_path, invoice_date, due_date, client_name, client_contact, products, subtotal, discount_amount, total):
    """Generates and provides a download link for the PDF invoice."""
    if not products:
        st.error("Please add at least one product before generating an invoice.")
        return

    temp_logo_path = None  # Initialize

    try:
        # Handle logo upload or default logo path
        if logo_path is not None and hasattr(logo_path, 'type'):
            temp_logo_path = f"temp_logo.{logo_path.type.split('/')[1]}"
            with open(temp_logo_path, "wb") as f:
                f.write(logo_path.getbuffer())
        elif isinstance(logo_path, str) and os.path.exists(logo_path):
            temp_logo_path = logo_path  # Use existing logo path if provided

        # Generate PDF
        pdf_file = generate_pdf(
            invoice_id, company_name, temp_logo_path, invoice_date, due_date,
            client_name, client_contact, products, subtotal, discount_amount, total
        )

        # Provide download link
        with open(pdf_file, "rb") as file:
            st.download_button("Download Invoice PDF", data=file, file_name=pdf_file, mime="application/pdf")
        st.success("PDF generated and ready to download.", icon="✅")

    except Exception as e:
        st.error(f"Error generating PDF: {str(e)}", icon="⚠️")

    finally:
        # Cleanup temporary logo if applicable
        if temp_logo_path and temp_logo_path.startswith("temp_logo") and os.path.exists(temp_logo_path):
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
    # st.set_page_config(page_title="Invoice Generator", page_icon="🧾", layout="wide")
    
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