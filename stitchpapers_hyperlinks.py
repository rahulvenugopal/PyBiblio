from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from reportlab.lib.colors import indianred, grey
import tempfile
import os
import csv
from datetime import datetime
from reportlab.lib.utils import simpleSplit


# ---- CONFIG ---- #
csv_path = "Exported Items.csv"
output_path = "combined_papers_with_index.pdf"
font_size_title = 20
font_size_index = 12
max_title_width = 90
date_formats = ["%Y-%m-%d", "%d-%m-%Y", "%Y-%m", "%Y"]
# ---------------- #

def parse_date(date_str):
    if not date_str:
        return datetime.min
    date_str = date_str.strip()
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.min


from reportlab.pdfbase.pdfmetrics import stringWidth

def create_title_page(title, font_size=25, margin=1*inch):
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(tmp_fd)

    c = canvas.Canvas(tmp_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", font_size)
    from reportlab.lib.colors import indianred
    c.setFillColor(indianred)

    # Calculate usable width
    usable_width = width - 2 * margin

    # Dynamically wrap text based on rendered width
    def wrap_text(text, font, size, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test_line = current + (" " if current else "") + word
            if stringWidth(test_line, font, size) <= max_width:
                current = test_line
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    lines = wrap_text(title, "Helvetica-Bold", font_size, usable_width)

    total_height = len(lines) * (font_size + 10)
    y = height / 2 + total_height / 2

    for line in lines:
        text_width = stringWidth(line, "Helvetica-Bold", font_size)
        x = (width - text_width) / 2
        c.drawString(x, y, line)
        y -= font_size + 10

    c.showPage()
    c.save()
    return tmp_path

def count_pdf_pages(path):
    try:
        reader = PdfReader(path)
        return len(reader.pages)
    except:
        return 0

def create_index_page(index_entries):
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(tmp_fd)

    c = canvas.Canvas(tmp_path, pagesize=A4)
    width, height = A4
    left_margin = inch
    right_margin = inch
    usable_width = width - left_margin - right_margin
    top_margin = inch
    bottom_margin = inch

    font_size_title = 20
    font_size_index = 12
    line_spacing = font_size_index + 6  # Add extra spacing between lines

    # Draw the index title
    c.setFont("Helvetica-Bold", font_size_title)
    c.drawString(left_margin, height - top_margin, "Table of contents")

    y = height - top_margin - 1.5 * font_size_title
    c.setFont("Helvetica", font_size_index)
    c.setFillColor(grey)

    for idx, (title, page_number) in enumerate(index_entries, start=1):
        # Wrap text using actual width
        wrapped_lines = simpleSplit(f"{idx}. {title}", "Helvetica", font_size_index, usable_width - 60)
        
        for i, line in enumerate(wrapped_lines):
            if y < bottom_margin:
                c.showPage()
                y = height - top_margin
                c.setFont("Helvetica", font_size_index)
                c.setFillColor(grey)

            # Add dots and page number only to first line
            if i == 0:
                title_part = line
                dots_width = usable_width - c.stringWidth(title_part, "Helvetica", font_size_index) - 40
                dots = '.' * int(dots_width / c.stringWidth('.', "Helvetica", font_size_index))
                line_out = f"{title_part} {dots} {page_number}"
            else:
                line_out = " " * 4 + line

            c.drawString(left_margin, y, line_out)
            y -= line_spacing
        y -= 4  # Extra space between entries

    c.showPage()
    c.save()
    return tmp_path

def add_hyperlinks_to_pdf(pdf_path, index_entries, output_path):
    """Add hyperlinks to the index page after the PDF is fully assembled"""
    try:
        from PyPDF2 import PdfWriter, PdfReader
        from PyPDF2.generic import DictionaryObject, ArrayObject, FloatObject, NameObject, TextStringObject
        
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        # Copy all pages to writer
        for page in reader.pages:
            writer.add_page(page)
        
        # Add links to the first page (index page)
        if len(writer.pages) > 0:
            index_page = writer.pages[0]
            
            # Calculate approximate positions for each index entry
            # These values are estimates based on the layout in create_index_page
            width, height = A4
            left_margin = inch
            top_margin = inch
            font_size_index = 12
            line_spacing = font_size_index + 6
            
            y_start = height - top_margin - 1.5 * 20  # Start after title
            current_y = y_start
            
            for idx, (title, target_page) in enumerate(index_entries):
                # Create annotation for this line
                line_height = line_spacing
                
                # Create link annotation
                link_dict = DictionaryObject({
                    NameObject('/Type'): NameObject('/Annot'),
                    NameObject('/Subtype'): NameObject('/Link'),
                    NameObject('/Rect'): ArrayObject([
                        FloatObject(left_margin),
                        FloatObject(current_y - line_height),
                        FloatObject(width - inch),
                        FloatObject(current_y)
                    ]),
                    NameObject('/Dest'): ArrayObject([
                        writer.pages[target_page - 1].indirect_reference,  # Target page (0-indexed)
                        NameObject('/XYZ'),
                        FloatObject(0),
                        FloatObject(height),
                        FloatObject(0)
                    ]),
                    NameObject('/Border'): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(0)])
                })
                
                # Add annotation to index page
                if '/Annots' not in index_page:
                    index_page[NameObject('/Annots')] = ArrayObject()
                
                index_page['/Annots'].append(writer._add_object(link_dict))
                
                current_y -= line_spacing + 4  # Account for entry spacing
        
        # Write the output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
            
        return True
    except Exception as e:
        print(f"Warning: Could not add hyperlinks: {e}")
        # If hyperlink addition fails, just copy the original file
        import shutil
        shutil.copy2(pdf_path, output_path)
        return False

# Load and parse CSV
papers = []
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        title = row.get('Title', 'Untitled')
        file_field = row.get('File Attachments', '')
        pdf_path = file_field.split(';')[0] if file_field else ''
        date_str = row.get('Date') or row.get('Publication Year') or ''
        date = parse_date(date_str)
        if pdf_path:
            papers.append((date, title, pdf_path))

# Sort newest first
papers.sort(reverse=True, key=lambda x: x[0])

# First create the PDF without hyperlinks
merger = PdfMerger()
index_entries = []
page_counter = 1  # Start with 1 to account for index page
title_pdf_paths = []

for date, title, pdf_path in papers:
    title_page_path = create_title_page(title)
    title_pages = count_pdf_pages(title_page_path)
    content_pages = count_pdf_pages(pdf_path)

    # Add to index entries (target page is where title page will be)
    index_entries.append((title, page_counter + 1))  # +1 because index comes first

    merger.append(title_page_path)
    merger.append(pdf_path)

    page_counter += title_pages + content_pages
    title_pdf_paths.append(title_page_path)

# Create index page and insert at the beginning
index_page_path = create_index_page(index_entries)
merger.merge(0, index_page_path)  # Insert index at beginning

# Save to temporary file first
temp_output = output_path + '.temp'
merger.write(temp_output)
merger.close()

# Now add hyperlinks to the assembled PDF
hyperlinks_added = add_hyperlinks_to_pdf(temp_output, index_entries, output_path)

# Clean up
for f in title_pdf_paths + [index_page_path, temp_output]:
    if os.path.exists(f):
        os.remove(f)

if hyperlinks_added:
    print(f"✅ Combined PDF created with hyperlinked index: {output_path}")
else:
    print(f"✅ Combined PDF created (hyperlinks could not be added): {output_path}")