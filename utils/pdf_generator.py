from fpdf import FPDF
import streamlit as st
from bidi.algorithm import get_display
from arabic_reshaper import reshape

def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
    """Generates a visually refined PDF invoice with Arabic support."""

    gray_color = 150
    try:
        _log_status("بدء إنشاء ملف PDF...")

        # Initialize PDF and configure fonts
        pdf = _initialize_pdf()
        _register_fonts(pdf)

        # Add company logo, header, invoice metadata, and client information
        _add_invoice_details(pdf, logo_path, company_name, invoice_id, date, due_date, client_name, client_contact, gray_color)

        # Add product table
        _add_product_table(pdf, products)

        # Add summary section
        _add_summary(pdf, subtotal, discount, total)

        # Add footer with page number
        _add_footer(pdf)

        # Generate and return PDF
        pdf_output = f"{invoice_id}.pdf"
        pdf.output(pdf_output)

        _log_status(f"تم إنشاء ملف PDF: {pdf_output}")
        return pdf_output

    except Exception as e:
        st.error(f"حدث خطأ أثناء إنشاء ملف PDF: {e}")
        _log_status(f"خطأ في إنشاء ملف PDF: {e}")
        return None


def _initialize_pdf():
    """Creates and configures a new PDF instance."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_text_color(90)  # Default text color
    return pdf


def _register_fonts(pdf):
    """Registers Arabic-compatible fonts."""
    pdf.add_font('Amiri', '', 'assets/fonts/Amiri-Regular.ttf', uni=True)
    pdf.add_font('Amiri', 'B', 'assets/fonts/Amiri-Bold.ttf', uni=True)

def _add_invoice_details(pdf, logo_path, company_name, invoice_id, date, due_date, client_name, client_contact, gray_color):
    """Adds logo, company header, invoice metadata, and client information to the PDF with specific layout."""
    
    # Add logo if provided
    if logo_path:
        try:
            pdf.image(logo_path, x=10, y=10, w=30)
        except Exception as e:
            st.error(f"خطأ أثناء إضافة الشعار: {e}")

    # Set the font for the company name
    pdf.set_font("Amiri", "B", 18)
    pdf.set_text_color(0)  # Black color for the company name
    pdf.set_xy(200, 20)  # Set position for company name
    pdf.cell(0, 10, txt=_reshape_text(company_name), ln=1, align='R')  # Align text to the right

    # Set the text color for the following details
    pdf.set_text_color(gray_color)
    pdf.set_font("Amiri", size=12)  # Use Amiri font for Arabic text

    print("Adding invoice details...")

    # Set the position for the invoice details
    pdf.set_xy(10, 30)
    pdf.cell(0, 5, _reshape_text(f"رقم الفاتورة: {invoice_id}"), ln=1, align='R')
    pdf.cell(0, 5, _reshape_text(f"تاريخ الفاتورة: {date}"), ln=1, align='R')
    pdf.cell(0, 5, _reshape_text(f"تاريخ الاستحقاق: {due_date}"), ln=1, align='R')

    print("Adding client information...")

    # Set the position for the client information
    pdf.set_xy(10, 50)
    pdf.cell(0, 5, _reshape_text("الاخوة:"), ln=1, align='R')  # Bill to in Arabic
    pdf.set_text_color(0)  # Reset color for client name
    pdf.cell(0, 5, _reshape_text(client_name), ln=1, align='R')  # Client name in Arabic
    pdf.set_text_color(gray_color)  # Set gray color for contact info
    pdf.cell(0, 5, _reshape_text(client_contact), ln=1, align='R')  # Client contact in Arabic

    # Draw a line below the client information
    pdf.set_draw_color(gray_color)  # Set line color
    pdf.line(x1=10, y1=70, x2=200, y2=70)  # Draw a line
    pdf.set_text_color(0)  # Reset color for client name
    pdf.ln(10)  # Add extra space before the product table





# def _add_product_table(pdf, products):
#     """Adds a mirrored product table for RTL layout with refined Sub-item formatting."""
#     pdf.set_font('Amiri', 'B', 12)
    
#     # Define headers in reverse order for RTL
#     headers = [_reshape_text(header) for header in ["الإجمالي", "سعر الوحدة", "الكمية", "الوصف"]]
#     widths = [35, 35, 30, 90]  # Define column widths
    
#     # Add table headers (RTL order)
#     for i, header in enumerate(headers):
#         pdf.cell(widths[i], 10, header, 1, 0, "C")
#     pdf.ln()

#     pdf.set_font('Amiri', '', 12)
#     for i, product in enumerate(products):
#         pdf.set_fill_color(255)

#         # Main product row in RTL (mirrored layout)
#         pdf.cell(widths[0], 10, f"${product['Total']:.2f}", 1, 0, "R", fill=True)
#         pdf.cell(widths[1], 10, f"${product['Unit Price']:.2f}", 1, 0, "R", fill=True)
#         pdf.cell(widths[2], 10, str(product["Quantity"]), 1, 0, "C", fill=True)
#         pdf.cell(widths[3], 10, _reshape_text(product["Description"]), 1, 1, "R", fill=True)

#         # Sub-items (if any)
#         if "Sub-items" in product and product["Sub-items"]:
#             pdf.set_font('Amiri', '', 10)  # Smaller font for sub-items
#             pdf.set_fill_color(245)  # Subtle background for sub-items
#             for sub_item in product["Sub-items"]:
#                 pdf.cell(10)  # Indent sub-item
#                 pdf.cell(180, 8, _reshape_text(f"- {sub_item}"), ln=1, align="R", border=0, fill=True)
#             pdf.set_font('Amiri', '', 12)  # Reset to regular font size

def _add_product_table(pdf, products):
    """Adds a mirrored product table for RTL layout with refined sub-item formatting."""
    
    # Set font for headers
    pdf.set_font('Amiri', 'B', 12)

    # Define headers in reverse order for RTL
    headers = [_reshape_text(header) for header in ["الإجمالي", "سعر الوحدة", "الكمية", "الوصف"]]
    widths = [35, 35, 30, 90]  # Define column widths

    # Add table headers (RTL order)
    for i, header in enumerate(headers):
        pdf.cell(widths[i], 10, header, 1, 0, "C")
    pdf.ln()

    # Set font for product details
    pdf.set_font('Amiri', '', 12)

    # Add product rows
    for product in products:
        pdf.set_fill_color(255)  # White background for product rows

        # Main product row in RTL (mirrored layout)
        pdf.cell(widths[0], 10, f"${product['Total']:.2f}", 1, 0, "R", fill=True)
        pdf.cell(widths[1], 10, f"${product['Unit Price']:.2f}", 1, 0, "R", fill=True)
        pdf.cell(widths[2], 10, str(product["Quantity"]), 1, 0, "C", fill=True)
        pdf.cell(widths[3], 10, _reshape_text(product["Description"]), 1, 1, "R", fill=True)
        pdf.ln(1)
        # Sub-items (if any)
        if "Sub-items" in product and product["Sub-items"]:
            pdf.set_font('Amiri', '', 10)  # Smaller font for sub-items
            pdf.set_fill_color(250)  # Subtle background for sub-items
            for sub_item in product["Sub-items"]:
                pdf.cell(10)  # Indent sub-item
                pdf.cell(180, 8, _reshape_text(f"- {sub_item}"), ln=True, align="R", border=0, fill=True)
            pdf.set_font('Amiri', '', 12)  # Reset to regular font size
            pdf.ln(10)

def _add_summary(pdf, subtotal, discount, total):
    """Adds a mirrored summary section with subtotal, discount, and total for RTL layout."""
    pdf.set_font('Amiri', 'B', 14)

    # Add summary items directly with RTL alignment
    pdf.cell(40, 10, f"${subtotal:.2f}", 0, 0, "L")  # Subtotal on the left
    pdf.cell(110, 10, _reshape_text("الإجمالي الفرعي:"), 0, 1, "R")

    pdf.cell(40, 10, f"${-discount:.2f}", 0, 0, "L")  # Discount on the left
    pdf.cell(110, 10, _reshape_text("الخصم:"), 0, 1, "R")

    pdf.cell(40, 10, f"${total:.2f}", 0, 0, "L")  # Total on the left
    pdf.cell(110, 10, _reshape_text("الإجمالي:"), 0, 1, "R")

def _add_footer(pdf):
    """Adds a footer with the page number."""
    pdf.set_y(-20)
    pdf.set_font('Amiri', '', 10)
    pdf.cell(0, 10, _reshape_text(f"الصفحة {pdf.page_no()}"), align='C')


def _reshape_text(text):
    """Reshapes and reorders Arabic text for correct display."""
    return get_display(reshape(text))


def _log_status(message):
    """Logs a status message to the console."""
    print(message)


def _add_footer(pdf):
    """Adds a footer with the page number."""
    pdf.set_y(-20)
    pdf.set_font('Amiri', '', 10)
    pdf.cell(0, 10, _reshape_text(f"الصفحة {pdf.page_no()}"), align='C')


def _reshape_text(text):
    """Reshapes and reorders Arabic text for correct display."""
    return get_display(reshape(text))


def _log_status(message):
    """Logs a status message to the console."""
    print(message)








# from fpdf import FPDF
# import streamlit as st
# from bidi.algorithm import get_display
# from arabic_reshaper import reshape

# def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
#     """Generates a visually refined PDF invoice with Arabic support."""
    
#     try:
#         _log_status("Starting PDF generation...")

#         # Initialize PDF and configure fonts
#         pdf = _initialize_pdf()
#         _register_fonts(pdf)

#         # Add company logo and header
#         _add_logo(pdf, logo_path)
#         _add_company_header(pdf, company_name)

#         # Add invoice metadata
#         _add_invoice_metadata(pdf, invoice_id, date, due_date)

#         # Add client information
#         _add_client_info(pdf, client_name, client_contact)

#         # Add product table
#         _add_product_table(pdf, products)

#         # Add summary section
#         _add_summary(pdf, subtotal, discount, total)

#         # Add footer with page number
#         _add_footer(pdf)

#         # Generate and return PDF
#         pdf_output = f"{invoice_id}.pdf"
#         pdf.output(pdf_output)

#         _log_status(f"PDF generated: {pdf_output}")
#         return pdf_output

#     except Exception as e:
#         st.error(f"An error occurred during PDF generation: {e}")
#         _log_status(f"PDF generation error: {e}")
#         return None


# def _initialize_pdf():
#     """Creates and configures a new PDF instance."""
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.set_text_color(90)  # Default text color
#     return pdf


# def _register_fonts(pdf):
#     """Registers Arabic-compatible fonts."""
#     pdf.add_font('Amiri', '', 'assets/fonts/Amiri-Regular.ttf', uni=True)
#     pdf.add_font('Amiri', 'B', 'assets/fonts/Amiri-Bold.ttf', uni=True)


# def _add_logo(pdf, logo_path):
#     """Adds the company logo to the PDF, if provided."""
#     if logo_path:
#         try:
#             pdf.image(logo_path, x=10, y=10, w=30)
#         except Exception as e:
#             st.error(f"Error adding logo: {e}")


# def _add_company_header(pdf, company_name):
#     """Adds the company name as a header in bold Arabic font."""
#     pdf.set_font('Amiri', 'B', 22)
#     pdf.set_text_color(0)  # Black
#     reshaped_name = _reshape_text(company_name)
#     pdf.cell(0, 20, txt=reshaped_name, ln=True, align='C')
#     pdf.ln(5)


# def _add_invoice_metadata(pdf, invoice_id, date, due_date):
#     """Adds invoice metadata such as ID, issue date, and due date."""
#     pdf.set_font('Amiri', '', 12)
#     pdf.cell(0, 10, _reshape_text(f"Invoice ID: {invoice_id}"), ln=True, align='R')
#     pdf.cell(0, 10, _reshape_text(f"Issue Date: {date}"), ln=True, align='R')
#     pdf.cell(0, 10, _reshape_text(f"Due Date: {due_date}"), ln=True, align='R')
#     pdf.ln(5)


# def _add_client_info(pdf, client_name, client_contact):
#     """Adds client information to the PDF."""
#     pdf.set_font('Amiri', 'B', 12)
#     pdf.cell(0, 10, _reshape_text("Bill to:"), ln=True, align='L')
#     pdf.set_font('Amiri', '', 12)
#     pdf.cell(0, 10, _reshape_text(client_name), ln=True, align='L')
#     pdf.cell(0, 10, _reshape_text(client_contact), ln=True, align='L')
#     pdf.ln(5)


# def _add_product_table(pdf, products):
#     """Adds a product table with details such as description, quantity, and price, including sub-items."""
#     pdf.set_font('Amiri', 'B', 12)
#     headers = [_reshape_text(header) for header in ["Description", "Quantity", "Unit Price", "Total"]]
#     widths = [90, 30, 35, 35]

#     for i, header in enumerate(headers):
#         pdf.cell(widths[i], 10, header, 1, 0, "C")
#     pdf.ln()

#     pdf.set_font('Amiri', '', 12)
#     for i, product in enumerate(products):
#         # Alternate row shading for main products
#         if i % 2 == 1:
#             pdf.set_fill_color(240)
#         else:
#             pdf.set_fill_color(255)

#         # Main product row
#         pdf.cell(90, 10, _reshape_text(product["Description"]), 1, 0, "R", fill=True)
#         pdf.cell(30, 10, str(product["Quantity"]), 1, 0, "C", fill=True)
#         pdf.cell(35, 10, f"${product['Unit Price']:.2f}", 1, 0, "R", fill=True)
#         pdf.cell(35, 10, f"${product['Total']:.2f}", 1, 1, "R", fill=True)

#         # Sub-items (if any)
#         if "Sub-items" in product and product["Sub-items"]:
#             pdf.set_font('Amiri', '', 10)  # Smaller font for sub-items
#             for sub_item in product["Sub-items"]:
#                 pdf.cell(10)  # Indent sub-item
#                 pdf.cell(80, 8, f"- {_reshape_text(sub_item)}", ln=1, align="R", border=0)
#             pdf.set_font('Amiri', '', 12)  # Reset to regular font size



# def _add_summary(pdf, subtotal, discount, total):
#     """Adds a summary section with subtotal, discount, and total."""
#     pdf.set_font('Amiri', 'B', 14)
#     summary_items = [
#         ("Subtotal", subtotal),
#         ("Discount", -discount),
#         ("Total", total)
#     ]

#     for label, amount in summary_items:
#         pdf.cell(110, 10, _reshape_text(f"{label}:"), 0, 0, "R")
#         pdf.cell(40, 10, f"${amount:.2f}", 0, 1, "R")


# def _add_footer(pdf):
#     """Adds a footer with the page number."""
#     pdf.set_y(-20)
#     pdf.set_font('Amiri', '', 10)
#     pdf.cell(0, 10, f"Page {pdf.page_no()}", align='C')


# def _reshape_text(text):
#     """Reshapes and reorders Arabic text for correct display."""
#     return get_display(reshape(text))


# def _log_status(message):
#     """Logs a status message to the console."""
#     print(message)














# from fpdf import FPDF
# import streamlit as st
# from bidi.algorithm import get_display
# from arabic_reshaper import reshape

# def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
#     """Generates a PDF invoice with Arabic support."""
#     try:
#         print("Starting PDF generation...")

#         pdf = FPDF()
#         pdf.add_page()
        
#         # Register and use Arabic-compatible fonts
#         pdf.add_font('Amiri', '', 'assets/fonts/Amiri-Regular.ttf', uni=True)
#         pdf.add_font('Amiri', 'B', 'assets/fonts/Amiri-Bold.ttf', uni=True)

#         pdf.set_font('Amiri', size=12)

#         gray_color = 150
#         pdf.set_text_color(gray_color)

#         # Add logo if available
#         if logo_path:
#             try:
#                 pdf.image(logo_path, x=150, y=10, w=50)
#             except Exception as e:
#                 st.error(f"Error adding logo: {e}")

#         # Use reshaping and bidi for Arabic text
#         reshaped_company_name = get_display(reshape(company_name))
#         reshaped_client_name = get_display(reshape(client_name))

#         pdf.set_font('Amiri', 'B', 18)
#         pdf.set_text_color(0)
#         pdf.text(x=10, y=20, txt=reshaped_company_name)
        
#         pdf.set_text_color(gray_color)
#         pdf.set_font('Amiri', size=12)

#         print("Adding invoice details...")

#         pdf.set_xy(10, 30)
#         pdf.cell(0, 5, get_display(reshape(f"Invoice ID: {invoice_id}")), ln=1)
#         pdf.cell(0, 5, get_display(reshape(f"Invoice Date: {date}")), ln=1)
#         pdf.cell(0, 5, get_display(reshape(f"Due Date: {due_date}")), ln=1)

#         print("Adding client information...")

#         pdf.set_xy(10, 50)
#         pdf.cell(0, 5, get_display(reshape("Bill to:")), ln=1)
#         pdf.set_text_color(0)
#         pdf.cell(0, 5, reshaped_client_name, ln=1)
#         pdf.set_text_color(gray_color)
#         pdf.cell(0, 5, get_display(reshape(client_contact)), ln=1)
#         pdf.set_draw_color(gray_color)
#         pdf.line(x1=10, y1=70, x2=200, y2=70)

#         pdf.set_xy(10, 80)
#         pdf.set_font('Amiri', 'B', 12)
#         pdf.set_text_color(0)
#         pdf.cell(90, 10, get_display(reshape("Description")), 1, 0, "R")
#         pdf.cell(30, 10, get_display(reshape("Quantity")), 1, 0, "C")
#         pdf.cell(35, 10, get_display(reshape("Unit Price")), 1, 0, "L")
#         pdf.cell(35, 10, get_display(reshape("Total")), 1, 1, "L")

#         pdf.set_font('Amiri', size=12)
#         pdf.set_text_color(gray_color)

#         print("Adding products...")

#         for product in products:
#             reshaped_desc = get_display(reshape(product["Description"]))
#             pdf.cell(90, 10, reshaped_desc, 1, 0, "R")
#             pdf.cell(30, 10, str(product["Quantity"]), 1, 0, "C")
#             pdf.cell(35, 10, f"${product['Unit Price']:.2f}", 1, 0, "R")
#             pdf.cell(35, 10, f"${product['Total']:.2f}", 1, 1, "R")

#             if product.get("Sub-items"):
#                 pdf.set_x(10)
#                 pdf.set_font('Amiri', size=10)
#                 for sub_item in product["Sub-items"]:
#                     pdf.cell(90, 5, f"- {get_display(reshape(sub_item))}", 0, 1, "R")
#                 pdf.ln(2)

#         pdf.set_y(pdf.get_y() + 15)
#         pdf.set_font('Amiri', 'B', 12)
#         pdf.set_text_color(0)
#         pdf.set_xy(120, pdf.get_y())
#         pdf.cell(70, 10, get_display(reshape(f"Subtotal: ${subtotal:.2f}")), 0, 1, "R")
#         pdf.cell(70, 10, get_display(reshape(f"Discount: -${discount:.2f}")), 0, 1, "R")
#         pdf.set_font('Amiri', 'B', 14)
#         pdf.cell(70, 10, get_display(reshape(f"Total: ${total:.2f}")), 0, 1, "R")

#         pdf_output = f"{invoice_id}.pdf"
#         pdf.output(pdf_output)

#         print(f"PDF generated: {pdf_output}")

#         return pdf_output

#     except Exception as e:
#         st.error(f"An error occurred during PDF generation: {e}")
#         print(f"PDF generation error: {e}")

#         return None

























# from fpdf import FPDF
# import streamlit as st  # Import Streamlit for error handling

# def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
#     """Generates a PDF invoice."""
#     try:
#         print("Starting PDF generation...")  # Print at the beginning

#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Helvetica", size=12)
#         gray_color = 150
#         pdf.set_text_color(gray_color)

#         # # Set UTF-8 encoding (for fpdf>=2.4.5)
#         # pdf.set_doc_option("core_fonts_encoding", "utf-8")

#         if logo_path:
#             try:
#                 pdf.image(logo_path, x=150, y=10, w=50)
#             except Exception as e:
#                 st.error(f"Error adding logo: {e}")  # Display error in Streamlit

#         pdf.set_font("Helvetica", "B", 18)
#         pdf.set_text_color(0)
#         pdf.text(x=10, y=20, txt=company_name)
#         pdf.set_text_color(gray_color)
#         pdf.set_font("Helvetica", size=12)


#         print("Adding invoice details...")

#         pdf.set_xy(10, 30)
#         pdf.cell(0, 5, f"Invoice ID: {invoice_id}", ln=1)
#         pdf.cell(0, 5, f"Invoice Date: {date}", ln=1)
#         pdf.cell(0, 5, f"Due Date: {due_date}", ln=1)


#         print("Adding client information...")

#         pdf.set_xy(10, 50)
#         pdf.cell(0, 5, "Bill to:", ln=1)
#         pdf.set_text_color(0)
#         pdf.cell(0, 5, f"{client_name}", ln=1)
#         pdf.set_text_color(gray_color)
#         pdf.cell(0, 5, f"{client_contact}", ln=1)
#         pdf.set_draw_color(gray_color)
#         pdf.line(x1=10, y1=70, x2=200, y2=70)

#         pdf.set_xy(10, 80)
#         pdf.set_font("Helvetica", "B", 12)
#         pdf.set_text_color(0)
#         pdf.cell(90, 10, "Description", 1, 0, "L")
#         pdf.cell(30, 10, "Quantity", 1, 0, "C")
#         pdf.cell(35, 10, "Unit Price", 1, 0, "R")
#         pdf.cell(35, 10, "Total", 1, 1, "R")

#         pdf.set_font("Helvetica", size=12)
#         pdf.set_text_color(gray_color)


#         print("Adding products...")

#         for product in products:
#             pdf.cell(90, 10, product["Description"], 1, 0, "L")
#             pdf.cell(30, 10, str(product["Quantity"]), 1, 0, "C")
#             pdf.cell(35, 10, f"${product['Unit Price']:.2f}", 1, 0, "R")
#             pdf.cell(35, 10, f"${product['Total']:.2f}", 1, 1, "R")

#             if product.get("Sub-items"):
#                 pdf.set_x(10)
#                 pdf.set_font("Helvetica", size=10)
#                 for sub_item in product["Sub-items"]:
#                     pdf.cell(90, 5, f"- {sub_item}", 0, 1, "L")
#                 pdf.ln(2)


#         pdf.set_y(pdf.get_y() + 15)
#         pdf.set_font("Helvetica", "B", 12)
#         pdf.set_text_color(0)
#         pdf.set_xy(120, pdf.get_y())
#         pdf.cell(70, 10, f"Subtotal: ${subtotal:.2f}", 0, 1, "R")
#         pdf.cell(70, 10, f"Discount: -${discount:.2f}", 0, 1, "R")
#         pdf.set_font("Helvetica", "B", 14)
#         pdf.cell(70, 10, f"Total: ${total:.2f}", 0, 1, "R")

#         pdf_output = f"{invoice_id}.pdf"
#         pdf.output(pdf_output)

#         print(f"PDF generated: {pdf_output}")  # Print the generated file path

#         return pdf_output


#     except Exception as e:
#         st.error(f"An error occurred during PDF generation: {e}") # Catch and display any PDF generation errors
#         print(f"PDF generation error: {e}") # Print the error to the console

#         return None # Return None to indicate failure





