# -*- coding: utf-8 -*-
"""
Created on Tue May 20 10:30:42 2025
- Add page numbers

@author: Rahul Venugopal
"""

import fitz  # PyMuPDF

def add_page_numbers(input_pdf, output_pdf,
                     start_page=8,
                     font_size=12,
                     font_color=(70/255, 130/255, 180/255),
                     margin_top=20,
                     margin_right=40,
                     font_name="helv"):
    doc = fitz.open(input_pdf)

    for i in range(start_page - 1, len(doc)):
        page = doc[i]
        width = page.rect.width

        # Top-right corner position
        x = width - margin_right
        y = margin_top

        page.insert_text(
            (x, y),
            str(i + 1),
            fontsize=font_size,
            color=font_color,
            fontname=font_name,
            render_mode=0
        )

    doc.save(output_pdf)
    doc.close()


# Example usage
add_page_numbers(
    input_pdf="AllPapers.pdf",
    output_pdf="output_with_pagenumbers.pdf",
    start_page=8,
    font_size=16  # <-- Change this value as needed
)

