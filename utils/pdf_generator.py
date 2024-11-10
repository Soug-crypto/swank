from fpdf import FPDF
import streamlit as st  # Import Streamlit for error handling

def generate_pdf(invoice_id, company_name, logo_path, date, due_date, client_name, client_contact, products, subtotal, discount, total):
    """Generates a PDF invoice."""
    try:
        print("Starting PDF generation...")  # Print at the beginning

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        gray_color = 150
        pdf.set_text_color(gray_color)

        # # Set UTF-8 encoding (for fpdf>=2.4.5)
        # pdf.set_doc_option("core_fonts_encoding", "utf-8")

        if logo_path:
            try:
                pdf.image(logo_path, x=150, y=10, w=50)
            except Exception as e:
                st.error(f"Error adding logo: {e}")  # Display error in Streamlit

        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(0)
        pdf.text(x=10, y=20, txt=company_name)
        pdf.set_text_color(gray_color)
        pdf.set_font("Helvetica", size=12)


        print("Adding invoice details...")

        pdf.set_xy(10, 30)
        pdf.cell(0, 5, f"Invoice ID: {invoice_id}", ln=1)
        pdf.cell(0, 5, f"Invoice Date: {date}", ln=1)
        pdf.cell(0, 5, f"Due Date: {due_date}", ln=1)


        print("Adding client information...")

        pdf.set_xy(10, 50)
        pdf.cell(0, 5, "Bill to:", ln=1)
        pdf.set_text_color(0)
        pdf.cell(0, 5, f"{client_name}", ln=1)
        pdf.set_text_color(gray_color)
        pdf.cell(0, 5, f"{client_contact}", ln=1)
        pdf.set_draw_color(gray_color)
        pdf.line(x1=10, y1=70, x2=200, y2=70)

        pdf.set_xy(10, 80)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0)
        pdf.cell(90, 10, "Description", 1, 0, "L")
        pdf.cell(30, 10, "Quantity", 1, 0, "C")
        pdf.cell(35, 10, "Unit Price", 1, 0, "R")
        pdf.cell(35, 10, "Total", 1, 1, "R")

        pdf.set_font("Helvetica", size=12)
        pdf.set_text_color(gray_color)


        print("Adding products...")

        for product in products:
            pdf.cell(90, 10, product["Description"], 1, 0, "L")
            pdf.cell(30, 10, str(product["Quantity"]), 1, 0, "C")
            pdf.cell(35, 10, f"${product['Unit Price']:.2f}", 1, 0, "R")
            pdf.cell(35, 10, f"${product['Total']:.2f}", 1, 1, "R")

            if product.get("Sub-items"):
                pdf.set_x(10)
                pdf.set_font("Helvetica", size=10)
                for sub_item in product["Sub-items"]:
                    pdf.cell(90, 5, f"- {sub_item}", 0, 1, "L")
                pdf.ln(2)


        pdf.set_y(pdf.get_y() + 15)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0)
        pdf.set_xy(120, pdf.get_y())
        pdf.cell(70, 10, f"Subtotal: ${subtotal:.2f}", 0, 1, "R")
        pdf.cell(70, 10, f"Discount: -${discount:.2f}", 0, 1, "R")
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(70, 10, f"Total: ${total:.2f}", 0, 1, "R")

        pdf_output = f"{invoice_id}.pdf"
        pdf.output(pdf_output)

        print(f"PDF generated: {pdf_output}")  # Print the generated file path

        return pdf_output


    except Exception as e:
        st.error(f"An error occurred during PDF generation: {e}") # Catch and display any PDF generation errors
        print(f"PDF generation error: {e}") # Print the error to the console

        return None # Return None to indicate failure