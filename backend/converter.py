import fitz  # PyMuPDF
from ebooklib import epub
import os

def pdf_to_epub(pdf_path, output_path, title="Sin Título", author="Anónimo"):
    """
    Convierte PDF a EPUB con imágenes, texto y portada automática.
    """
    
    book = epub.EpubBook()
    book.set_identifier(f'id_{title.replace(" ", "_")}')
    book.set_title(title)
    book.set_language('es')
    book.add_author(author)

    doc = fitz.open(pdf_path)
    
    if len(doc) > 0:
        first_page = doc[0]
        pix = first_page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        image_bytes = pix.tobytes("jpg")
        
        book.set_cover("cover.jpg", image_bytes)
    
    chapters = []
    image_counter = 0

    for page_num, page in enumerate(doc):
        page_dict = page.get_text("dict")
        blocks = page_dict["blocks"]
        
        chapter_content = f"<h1>{title} - Página {page_num + 1}</h1>"
        has_content = False

        for block in blocks:
            if block["type"] == 0:
                text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        text += span["text"] + " "
                if text.strip():
                    chapter_content += f"<p>{text.strip()}</p>"
                    has_content = True

            elif block["type"] == 1:
                image_bytes = block["image"]
                ext = block["ext"]
                image_filename = f"img_{page_num}_{image_counter}.{ext}"
                image_counter += 1

                epub_img = epub.EpubImage()
                epub_img.file_name = image_filename
                epub_img.media_type = f"image/{ext}"
                epub_img.content = image_bytes
                book.add_item(epub_img)

                chapter_content += f'<p style="text-align:center"><img src="{image_filename}" style="max-width:100%"/></p>'
                has_content = True

        if has_content:
            c = epub.EpubHtml(title=f'Página {page_num+1}', file_name=f'chap_{page_num+1}.xhtml', lang='es')
            c.content = chapter_content
            book.add_item(c)
            chapters.append(c)

    book.toc = (tuple(chapters))
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    style = 'body { font-family: sans-serif; padding: 5%; } img { max-width: 100%; height: auto; } h1 { text-align: center; color: #333; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    book.spine = ['nav'] + chapters
    epub.write_epub(output_path, book, {})
    doc.close()
    return output_path