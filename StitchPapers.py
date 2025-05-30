from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger, PdfReader
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

def estimate_index_pages(index_entries):
    """Estimate how many pages the index will take"""
    # Rough calculation: assume each entry takes approximately 2 lines on average
    # and we can fit about 30-35 lines per page with title and margins
    lines_per_entry = 2
    lines_per_page = 30
    total_lines = len(index_entries) * lines_per_entry + 3  # +3 for title and spacing
    return max(1, (total_lines + lines_per_page - 1) // lines_per_page)

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

# First, collect all papers and calculate their page counts
paper_info = []
title_pdf_paths = []

for date, title, pdf_path in papers:
    title_page_path = create_title_page(title)
    title_pages = count_pdf_pages(title_page_path)
    content_pages = count_pdf_pages(pdf_path)
    
    paper_info.append({
        'title': title,
        'title_page_path': title_page_path,
        'content_path': pdf_path,
        'title_pages': title_pages,
        'content_pages': content_pages
    })
    title_pdf_paths.append(title_page_path)

# Calculate page numbers accounting for index pages
index_entries = []
estimated_index_pages = estimate_index_pages([(info['title'], 0) for info in paper_info])
page_counter = estimated_index_pages  # Start after the index pages

for info in paper_info:
    # Page number is 1-based and starts after index
    index_entries.append((info['title'], page_counter + 1))
    page_counter += info['title_pages'] + info['content_pages']

# Create the actual index page with correct page numbers
index_page_path = create_index_page(index_entries)
actual_index_pages = count_pdf_pages(index_page_path)

# If our estimation was wrong, recalculate
if actual_index_pages != estimated_index_pages:
    # Recalculate page numbers with actual index page count
    index_entries = []
    page_counter = actual_index_pages
    
    for info in paper_info:
        index_entries.append((info['title'], page_counter + 1))
        page_counter += info['title_pages'] + info['content_pages']
    
    # Recreate index page with corrected numbers
    os.remove(index_page_path)
    index_page_path = create_index_page(index_entries)

# Now merge everything
merger = PdfMerger()

# Add index page first
merger.append(index_page_path)

# Add all papers with their title pages
for info in paper_info:
    merger.append(info['title_page_path'])
    merger.append(info['content_path'])

merger.write(output_path)
merger.close()

# Clean up
for f in title_pdf_paths + [index_page_path]:
    os.remove(f)

print(f"✅ Combined PDF created: {output_path}")
print(f"📄 Index pages: {actual_index_pages}")
print(f"📚 Total papers: {len(papers)}")
print(f"📖 Total pages: {page_counter}")