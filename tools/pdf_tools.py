"""
PDF Tools for Aeonforge Phase 2 - Business Logic & API Integration
Includes PDF generation and fillable form tools with human-in-the-loop approval
"""

import os
from typing import Dict, Any, Optional
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from PyPDF2 import PdfReader, PdfWriter
from .approval_system import get_user_approval, pause_for_user_input

def create_business_document(document_type: str, output_path: str, data: Dict[str, Any] = None) -> str:
    """
    Creates a business document (invoice, report, contract, etc.) with human approval.
    
    Args:
        document_type: Type of document to create (invoice, report, contract, etc.)
        output_path: Path where the PDF will be saved
        data: Dictionary containing document data (optional)
        
    Returns:
        Success/failure message
    """
    # Pause for human approval before creating the document
    if not get_user_approval(
        f"Create {document_type} PDF document",
        f"Document will be created at: {output_path}\nData provided: {bool(data)}"
    ):
        return f"Document creation cancelled by user."
    
    try:
        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Add title
        title = document_type.title().replace('_', ' ')
        story.append(Paragraph(f"<b>{title}</b>", styles['Title']))
        story.append(Spacer(1, 12))
        
        # Add content based on document type
        if document_type.lower() == 'invoice':
            story.extend(_create_invoice_content(data or {}, styles))
        elif document_type.lower() == 'report':
            story.extend(_create_report_content(data or {}, styles))
        elif document_type.lower() == 'contract':
            story.extend(_create_contract_content(data or {}, styles))
        else:
            # Generic document
            story.extend(_create_generic_content(data or {}, styles))
        
        # Build the PDF
        doc.build(story)
        
        return f"Successfully created {document_type} PDF at: {output_path}"
        
    except Exception as e:
        return f"Error creating PDF document: {e}"

def fill_pdf_form(template_path: str, output_path: str, form_data: Dict[str, str] = None) -> str:
    """
    Fills a fillable PDF form with data, with human approval for the data to be filled.
    
    Args:
        template_path: Path to the fillable PDF template
        output_path: Path where the filled PDF will be saved
        form_data: Dictionary of field names and values (optional)
        
    Returns:
        Success/failure message
    """
    if not os.path.exists(template_path):
        return f"Template file not found: {template_path}"
    
    try:
        # Read the template
        reader = PdfReader(template_path)
        writer = PdfWriter()
        
        # Get form fields if no data provided
        if not form_data:
            form_data = _collect_form_data_from_user(reader)
            
        if not form_data:
            return "No form data provided. Operation cancelled."
        
        # Show data and ask for approval
        data_summary = "\n".join([f"  {field}: {value}" for field, value in form_data.items()])
        
        if not get_user_approval(
            "Fill PDF form with the following data",
            f"Template: {template_path}\nOutput: {output_path}\n\nData to fill:\n{data_summary}"
        ):
            return "Form filling cancelled by user."
        
        # Fill the form
        for page in reader.pages:
            writer.add_page(page)
        
        # Update form fields
        writer.update_page_form_field_values(writer.pages[0], form_data)
        
        # Save the filled form
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        return f"Successfully filled PDF form. Output saved to: {output_path}"
        
    except Exception as e:
        return f"Error filling PDF form: {e}"

def _collect_form_data_from_user(reader: PdfReader) -> Dict[str, str]:
    """
    Collects form data from the user for fillable PDF fields.
    
    Args:
        reader: PdfReader object of the template
        
    Returns:
        Dictionary of field names and user-provided values
    """
    form_data = {}
    
    try:
        # Get form fields
        if reader.metadata and '/AcroForm' in reader.trailer['/Root']:
            fields = reader.get_form_text_fields()
            
            if not fields:
                print("No fillable fields found in the PDF template.")
                return {}
            
            print("Found the following fillable fields in the PDF:")
            for field_name in fields.keys():
                print(f"  - {field_name}")
            
            # Ask user for data for each field
            for field_name in fields.keys():
                value = pause_for_user_input(f"Enter value for field '{field_name}':")
                if value.strip():
                    form_data[field_name] = value
                    
    except Exception as e:
        print(f"Error reading form fields: {e}")
        
    return form_data

def _create_invoice_content(data: Dict[str, Any], styles) -> list:
    """Creates content for an invoice document."""
    story = []
    
    # Invoice details
    story.append(Paragraph("<b>INVOICE</b>", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    # Invoice info
    invoice_data = [
        ['Invoice #:', data.get('invoice_number', 'INV-001')],
        ['Date:', data.get('date', 'TBD')],
        ['Due Date:', data.get('due_date', 'TBD')],
    ]
    
    invoice_table = Table(invoice_data)
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Bill to section
    story.append(Paragraph("<b>Bill To:</b>", styles['Heading2']))
    story.append(Paragraph(data.get('bill_to', 'Customer Name\nCustomer Address'), styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Items table
    items = data.get('items', [
        {'description': 'Sample Item', 'quantity': 1, 'rate': 100.00, 'amount': 100.00}
    ])
    
    items_data = [['Description', 'Quantity', 'Rate', 'Amount']]
    for item in items:
        items_data.append([
            item.get('description', ''),
            str(item.get('quantity', 0)),
            f"${item.get('rate', 0):.2f}",
            f"${item.get('amount', 0):.2f}"
        ])
    
    items_table = Table(items_data)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(items_table)
    
    # Total
    total = sum(item.get('amount', 0) for item in items)
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Total: ${total:.2f}</b>", styles['Heading2']))
    
    return story

def _create_report_content(data: Dict[str, Any], styles) -> list:
    """Creates content for a report document."""
    story = []
    
    story.append(Paragraph(f"<b>{data.get('title', 'Business Report')}</b>", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("<b>Executive Summary</b>", styles['Heading2']))
    story.append(Paragraph(data.get('summary', 'Report summary goes here.'), styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Main Content
    sections = data.get('sections', [
        {'title': 'Overview', 'content': 'Overview content goes here.'},
        {'title': 'Analysis', 'content': 'Analysis content goes here.'},
        {'title': 'Conclusions', 'content': 'Conclusions go here.'}
    ])
    
    for section in sections:
        story.append(Paragraph(f"<b>{section['title']}</b>", styles['Heading2']))
        story.append(Paragraph(section['content'], styles['Normal']))
        story.append(Spacer(1, 12))
    
    return story

def _create_contract_content(data: Dict[str, Any], styles) -> list:
    """Creates content for a contract document."""
    story = []
    
    story.append(Paragraph(f"<b>{data.get('title', 'Service Agreement')}</b>", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Parties
    story.append(Paragraph("<b>Parties:</b>", styles['Heading2']))
    story.append(Paragraph(f"Client: {data.get('client', 'CLIENT NAME')}", styles['Normal']))
    story.append(Paragraph(f"Service Provider: {data.get('provider', 'SERVICE PROVIDER NAME')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Terms
    story.append(Paragraph("<b>Terms and Conditions:</b>", styles['Heading2']))
    terms = data.get('terms', [
        'Service will be provided as agreed.',
        'Payment terms: Net 30 days.',
        'This agreement is governed by applicable law.'
    ])
    
    for i, term in enumerate(terms, 1):
        story.append(Paragraph(f"{i}. {term}", styles['Normal']))
        story.append(Spacer(1, 6))
    
    return story

def _create_generic_content(data: Dict[str, Any], styles) -> list:
    """Creates generic document content."""
    story = []
    
    # Add any provided data
    for key, value in data.items():
        if isinstance(value, str):
            story.append(Paragraph(f"<b>{key.title()}:</b> {value}", styles['Normal']))
            story.append(Spacer(1, 6))
    
    if not data:
        story.append(Paragraph("This is a generated document.", styles['Normal']))
        story.append(Paragraph("Content can be customized by providing data.", styles['Normal']))
    
    return story