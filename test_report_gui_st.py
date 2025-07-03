import streamlit as st
import fitz  # PyMuPDF
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import random
import re

def extract_pdf_data(pdf_file):
    extracted_data = {
        "Company Name": None,
        "Order Date": None,
        "Invoice No": None,
        "Order No": None,
        "Products": []
    }
    counter = 1
    product_count = 0
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        text = "\n".join([page.get_text("text") for page in doc])
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for i, line in enumerate(lines):
            f "Shipped to :" in line or "Shipped to  :" in line:
                extracted_data["Company Name"] = lines[i + 1]
            if "Invoice No." in line:
                extracted_data["Invoice No"] = lines[i+1].split(":")[-1].strip()
            if "Order no:" in line:
                extracted_data["Order No"] = lines[i]
            if "Dated" in line:
                extracted_data["Order Date"] = lines[i+1].split(":")[-1].strip()
            if line.startswith(("1.", "2.", "3.")):
                product_details = {
                    "Product Name": line,
                    "Quantity": lines[i+2],
                    "Batch No": lines[i+5],
                    "No of Bags": lines[i+6]
                }
                product_count += 1
                extracted_data["Products"].append(product_details)
            if product_count >= counter:
                break
    return extracted_data

def generate_test_report(order_details, logo_path, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)

    # Verify logo file exists before trying to load it
    if not os.path.exists(logo_path):
        print(f"⚠️ Logo file not found: {logo_path}")
    else:
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, 220, 720, width=100, height=80)  # Adjust size and position
        except Exception as e:
            print(f"⚠️ Error loading logo: {e}")
            
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 710, "Atma Metchem Pvt. Ltd. ")  # Moved down
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 695, "BF-180, SECTOR-1, SALT LAKE, KOLKATA 700064, MOBILE - 9830692043/9830272025 ")  # Moved down
    # Move Title Down to Avoid Overlapping Logo
    c.setFont("Helvetica-Bold", 14)
    c.drawString(230, 670, "Test Report")  # Moved down

    c.setFont("Helvetica-Bold", 12)

    # Generate Randomized Values
    random_copper_value = round(random.uniform(24.70, 24.75), 2)
    random_ph_value = round(random.uniform(3.0, 3.4), 1)
    batch = re.search(r"batch no:\s*(\d+)",order_details["Products"][0]["Batch No"] )
    clean_product_name = re.sub(r"^\d+\.\s*", "", order_details["Products"][0]["Product Name"])
    if not order_details["Order No"]:
        OR_NO = "VERBAL"
    else:
        OR_NO = order_details["Order No"].split("Order no:")[-1].strip()
        OR_NO = OR_NO.split("dtd")[0].strip()

    # Consignee Information Table Data
    details = [
        ["Consignee:", order_details["Company Name"]],
        ["Item:", clean_product_name],
        ["Order No.:", OR_NO],
        ["Invoice No.:", f"{order_details['Invoice No']} {order_details['Order Date']}"],
        ["Quantity:", order_details["Products"][0]["Quantity"]],
        ["No. Of Bags:", order_details["Products"][0]["No of Bags"]],
        ["Certificate No.:", f"{order_details['Invoice No'][-3:]} dated {order_details['Order Date']}"],
        ["Manufacturing Date:", order_details["Products"][0]["Batch No"][-10:]]
    ]

    # Create Consignee Table
    details_table = Table(details, colWidths=[150, 300])
    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)  # Add gridlines
    ]))

    # Position Consignee Table
    y_position = 480  # Position below "Test Report"
    table_width, table_height = details_table.wrap(0, 0)  # Get the height of the table
    details_table.drawOn(c, 50, y_position)

    # Move Test Report Table Further Down Based on Table Height
    y_position -= table_height + 50  # Add extra spacing

    # Test Report Table Data
    table_data = [
        ["Sl No.", "Parameters", "Test Result\nBatch No:"f"{batch.group(1)}"],
        ["1", "Appearance", "Bluish White Fine Crystals free from\nforeign material with\nslight yellowish additives"],
        ["2", "Copper Sulphate", "98%"],
        ["3", "Copper as Cu", f"{random_copper_value}%"],
        ["4", "pH of 10% solution", f"{random_ph_value}"],
        ["5", "Solubility of 10% Solution", "Clear blue solution"],
        ["6", "Additives", "2%"],
        ["7", "Iron", "< 0.075%"]
    ]

    # Create Test Report Table
    table = Table(table_data, colWidths=[50, 200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Draw Test Report Table at Correct Position
    table.wrapOn(c, 50, y_position)
    table.drawOn(c, 50, y_position)

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 250, "** Additional additives are present for optimum coating.")
    c.drawString(50, 230, "** This is a computer-generated document & does not need a signature.")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(100, 100, "WORKS: P.O. GANGANAGAR, NORTH 24 PARAGANAS (WEST BENGAL) 700132")
    c.drawString(135, 90, "EMAIL: info@atmametchem.com, atmametchem_2006@yahoo.co.in")
    c.drawString(145, 80, "GST: 19AACCA5773F1ZL   CIN NO. U24119WB1992PTC056507")
    # Save PDF
    c.save()
    return output_path,

st.title("PDF Data Extractor & Test Report Generator")

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf:
    st.success("PDF uploaded successfully!")
    extracted_data = extract_pdf_data(uploaded_pdf)
    st.write("### Extracted Data:")
    st.json(extracted_data)

    
    if st.button("Generate Test Report"):
        clean_product_name = re.sub(r"^\d+\.\s*", "", extracted_data["Products"][0]["Product Name"])
        invoice_suffix = extracted_data["Invoice No"][-3:]
        report_path = f"test_report{clean_product_name}{invoice_suffix}.pdf"
        logo_path = "C:/Users/sunil/Downloads/WhatsApp Image 2025-03-19 at 12.34.13 PM.jpeg"  # Replace with actual logo path
        generate_test_report(extracted_data, logo_path, report_path)
        
        with open(report_path, "rb") as f:
            clean_product_name = re.sub(r"^\d+\.\s*", "", extracted_data["Products"][0]["Product Name"])
            invoice_suffix = extracted_data["Invoice No"][-3:]
            st.download_button("Download Test Report", f, file_name=f"Test_Report{clean_product_name}{invoice_suffix}.pdf", mime="application/pdf")
