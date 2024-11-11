from fpdf import FPDF
import streamlit as st
from bidi.algorithm import get_display
from arabic_reshaper import reshape
from fpdf.enums import XPos, YPos

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
    """Adds a summary section as a small table on the left side of the page."""
    pdf.set_font('Amiri', 'B', 14)

    # Set table position
    pdf.set_xy(10, pdf.get_y() + 10)  # Position on the left with some vertical space

    # Define column widths and row height
    col1_width = 50  # Adjusted for the numeric values
    col2_width = 40  # Adjusted for the labels
    row_height = 10

    # Draw the table rows with swapped columns
    pdf.cell(col1_width, row_height, f"${subtotal:.2f}", 1, 0, "L")  # Numeric value in the first column
    pdf.cell(col2_width, row_height, _reshape_text("الإجمالي الفرعي:"), 1, 1, "R")  # Label in the second column

    pdf.cell(col1_width, row_height, f"${-discount:.2f}", 1, 0, "L")
    pdf.cell(col2_width, row_height, _reshape_text("الخصم:"), 1, 1, "R")

    pdf.cell(col1_width, row_height, f"${total:.2f}", 1, 0, "L")
    pdf.cell(col2_width, row_height, _reshape_text("الإجمالي:"), 1, 1, "R")


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


def _add_invoice_details(pdf, logo_path, company_name, invoice_id, date, due_date, client_name, client_contact, gray_color):
    """Adds a refined RTL header with the company info below the logo."""

    # Logo
    logo_width = 45  # Adjust as needed
    logo_x = 10
    logo_y = 2
    if logo_path:
        try:
            pdf.image(logo_path, x=logo_x, y=logo_y, w=logo_width)
        except Exception as e:
            print(f"Error adding logo: {e}")  # Or log the error

    # Company Information (Left-Aligned, below logo)
    current_y = logo_y + logo_width / 2 + 18  # Start below the logo + some padding. Logo height assumed to be equal to width.

    pdf.set_font("Amiri", "B", 18)
    pdf.set_text_color(0)
    pdf.set_xy(logo_x, current_y)  # Position below logo
    pdf.cell(0, 10, _reshape_text(company_name), ln=1, align="L")

    current_y += 10  # Add space between company name and next line
    pdf.set_font("Amiri", "", 12)
    pdf.set_xy(logo_x, current_y)
    pdf.multi_cell(0, 8, _reshape_text("teleset DOGTAS LAZZONI MONTEL\nالهاتف: 0913273608"), align="L")

    # Invoice Metadata (Right-Aligned, below logo, like the company info)
    pdf.set_text_color(gray_color)
    pdf.set_font("Amiri", "", 12)

    right_x = pdf.w - 10
    current_y = 15  # Start at the top right

    invoice_metadata = [
        _reshape_text(f"رقم الفاتورة: {invoice_id}"),
        _reshape_text(f"تاريخ الفاتورة: {date}"),
        _reshape_text(f"تاريخ الاستحقاق: {due_date}"),
    ]

    for line in invoice_metadata:
        pdf.set_xy(right_x, current_y)
        pdf.cell(0, 8, line, ln=1, align="R")
        current_y += 8  # Increment y-coordinate for the next line

    # Client Information (Right-Aligned, below Invoice Metadata)
    pdf.set_text_color(0)
    pdf.set_font("Amiri", "B", 12)
    current_y += 3  # Add some space between metadata and client info

    client_info = [
        _reshape_text("الاخوة"),
        _reshape_text(client_name),
        _reshape_text(client_contact),
    ]

    for i, line in enumerate(client_info):
        pdf.set_xy(right_x, current_y)
        pdf.set_font("Amiri", "B" if i == 0 else "", 12)  # Bold only the first line
        pdf.set_text_color(0 if i < 2 else gray_color)  # Gray for last line (client_contact)
        pdf.cell(0, 8, line, ln=1, align="R")
        current_y += 8

    # Divider Line (Adjust y-coordinate)
    pdf.set_draw_color(200)
    current_y += 5  # Add space above the line
    pdf.line(10, current_y, pdf.w - 10, current_y)
    pdf.ln(10)  # Space below the line
    pdf.set_text_color(0)








# from fpdf import FPDF
# import streamlit as st
# from bidi.algorithm import get_display
# from arabic_reshaper import reshape

# def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
#     """Generates a visually refined PDF invoice with Arabic support."""

#     gray_color = 150
#     try:
#         _log_status("بدء إنشاء ملف PDF...")

#         # Initialize PDF and configure fonts
#         pdf = _initialize_pdf()
#         _register_fonts(pdf)

#         # Add company logo, header, invoice metadata, and client information
#         _add_invoice_details(pdf, logo_path, company_name, invoice_id, date, due_date, client_name, client_contact, gray_color)

#         # Add product table
#         _add_product_table(pdf, products)

#         # Add summary section
#         _add_summary(pdf, subtotal, discount, total)

#         # Add footer with page number
#         _add_footer(pdf)

#         # Generate and return PDF
#         pdf_output = f"{invoice_id}.pdf"
#         pdf.output(pdf_output)

#         _log_status(f"تم إنشاء ملف PDF: {pdf_output}")
#         return pdf_output

#     except Exception as e:
#         st.error(f"حدث خطأ أثناء إنشاء ملف PDF: {e}")
#         _log_status(f"خطأ في إنشاء ملف PDF: {e}")
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


# def _add_product_table(pdf, products):
#     """Adds a mirrored product table for RTL layout with refined sub-item formatting."""
    
#     # Set font for headers
#     pdf.set_font('Amiri', 'B', 12)

#     # Define headers in reverse order for RTL
#     headers = [_reshape_text(header) for header in ["الإجمالي", "سعر الوحدة", "الكمية", "الوصف"]]
#     widths = [35, 35, 30, 90]  # Define column widths

#     # Add table headers (RTL order)
#     for i, header in enumerate(headers):
#         pdf.cell(widths[i], 10, header, 1, 0, "C")
#     pdf.ln()

#     # Set font for product details
#     pdf.set_font('Amiri', '', 12)

#     # Add product rows
#     for product in products:
#         pdf.set_fill_color(255)  # White background for product rows

#         # Main product row in RTL (mirrored layout)
#         pdf.cell(widths[0], 10, f"${product['Total']:.2f}", 1, 0, "R", fill=True)
#         pdf.cell(widths[1], 10, f"${product['Unit Price']:.2f}", 1, 0, "R", fill=True)
#         pdf.cell(widths[2], 10, str(product["Quantity"]), 1, 0, "C", fill=True)
#         pdf.cell(widths[3], 10, _reshape_text(product["Description"]), 1, 1, "R", fill=True)
#         pdf.ln(1)
#         # Sub-items (if any)
#         if "Sub-items" in product and product["Sub-items"]:
#             pdf.set_font('Amiri', '', 10)  # Smaller font for sub-items
#             pdf.set_fill_color(250)  # Subtle background for sub-items
#             for sub_item in product["Sub-items"]:
#                 pdf.cell(10)  # Indent sub-item
#                 pdf.cell(180, 8, _reshape_text(f"- {sub_item}"), ln=True, align="R", border=0, fill=True)
#             pdf.set_font('Amiri', '', 12)  # Reset to regular font size
#             pdf.ln(10)



# def _add_summary(pdf, subtotal, discount, total):
#     """Adds a summary section as a small table on the left side of the page."""
#     pdf.set_font('Amiri', 'B', 14)

#     # Set table position
#     pdf.set_xy(10, pdf.get_y() + 10)  # Position on the left with some vertical space

#     # Define column widths and row height
#     col1_width = 50  # Adjusted for the numeric values
#     col2_width = 40  # Adjusted for the labels
#     row_height = 10

#     # Draw the table rows with swapped columns
#     pdf.cell(col1_width, row_height, f"${subtotal:.2f}", 1, 0, "L")  # Numeric value in the first column
#     pdf.cell(col2_width, row_height, _reshape_text("الإجمالي الفرعي:"), 1, 1, "R")  # Label in the second column

#     pdf.cell(col1_width, row_height, f"${-discount:.2f}", 1, 0, "L")
#     pdf.cell(col2_width, row_height, _reshape_text("الخصم:"), 1, 1, "R")

#     pdf.cell(col1_width, row_height, f"${total:.2f}", 1, 0, "L")
#     pdf.cell(col2_width, row_height, _reshape_text("الإجمالي:"), 1, 1, "R")

# def _add_footer(pdf):
#     """Adds a footer with the page number."""
#     pdf.set_y(-20)
#     pdf.set_font('Amiri', '', 10)
#     pdf.cell(0, 10, _reshape_text(f"الصفحة {pdf.page_no()}"), align='C')


# def _reshape_text(text):
#     """Reshapes and reorders Arabic text for correct display."""
#     return get_display(reshape(text))


# def _log_status(message):
#     """Logs a status message to the console."""
#     print(message)


# def _add_footer(pdf):
#     """Adds a footer with the page number."""
#     pdf.set_y(-20)
#     pdf.set_font('Amiri', '', 10)
#     pdf.cell(0, 10, _reshape_text(f"الصفحة {pdf.page_no()}"), align='C')


# def _reshape_text(text):
#     """Reshapes and reorders Arabic text for correct display."""
#     return get_display(reshape(text))


# def _log_status(message):
#     """Logs a status message to the console."""
#     print(message)



# def _add_invoice_details(pdf, logo_path, company_name, invoice_id, date, due_date, client_name, client_contact, gray_color):
#     """Adds a refined RTL header with the company info below the logo."""

#     # Logo
#     logo_width = 45  # Adjust as needed
#     logo_x = 10
#     logo_y = 2
#     if logo_path:
#         try:
#             pdf.image(logo_path, x=logo_x, y=logo_y, w=logo_width)
#         except Exception as e:
#             print(f"Error adding logo: {e}")  # Or log the error


#     # Company Information (Left-Aligned, below logo)
#     current_y = logo_y + logo_width/2 + 18  # Start below the logo + some padding. Logo height assumed to be equal to width.

#     pdf.set_font("Amiri", "B", 18)
#     pdf.set_text_color(0)
#     pdf.set_xy(logo_x, current_y)  # Position below logo
#     pdf.cell(0, 10, _reshape_text(company_name), ln=1, align="L")


#     current_y += 10 # Add space between company name and next line
#     pdf.set_font("Amiri", "", 12)
#     pdf.set_xy(logo_x, current_y)
#     pdf.multi_cell(0, 8, _reshape_text("teleset DOGTAS LAZZONI MONTEL\nالهاتف: 0913273608"), align="L")

#     # Invoice Metadata (Right-Aligned, below logo, like the company info)
#     pdf.set_text_color(gray_color)
#     pdf.set_font("Amiri", "", 12)

#     right_x = pdf.w - 10
#     current_y = 15  # Start at the top right

#     invoice_metadata = [
#         _reshape_text(f"رقم الفاتورة: {invoice_id}"),
#         _reshape_text(f"تاريخ الفاتورة: {date}"),
#         _reshape_text(f"تاريخ الاستحقاق: {due_date}"),
#     ]

#     for line in invoice_metadata:
#         pdf.set_xy(right_x, current_y)
#         pdf.cell(0, 8, line, ln=1, align="R")
#         current_y += 8  # Increment y-coordinate for the next line

#     # Client Information (Right-Aligned, below Invoice Metadata)
#     pdf.set_text_color(0)
#     pdf.set_font("Amiri", "B", 12)
#     current_y += 3  # Add some space between metadata and client info

#     client_info = [
#         _reshape_text("الاخوة"),
#         _reshape_text(client_name),
#         _reshape_text(client_contact),
#     ]

#     for i, line in enumerate(client_info):
#         pdf.set_xy(right_x, current_y)
#         pdf.set_font("Amiri", "B" if i == 0 else "", 12)  # Bold only the first line
#         pdf.set_text_color(0 if i < 2 else gray_color)  # Gray for last line (client_contact)
#         pdf.cell(0, 8, line, ln=1, align="R")
#         current_y += 8

#     # Divider Line (Adjust y-coordinate)
#     pdf.set_draw_color(200)
#     current_y += 5  # Add space above the line
#     pdf.line(10, current_y, pdf.w - 10, current_y)
#     pdf.ln(10)  # Space below the line
#     pdf.set_text_color(0)