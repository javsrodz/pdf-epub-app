import fitz  # PyMuPDF
from ebooklib import epub
import os

def pdf_to_epub(pdf_path, output_path, title="Sin Título", author="Anónimo"):
    """
    Convierte PDF a EPUB respetando texto e imágenes en su orden de aparición.
    """
    
    book = epub.EpubBook()
    book.set_identifier(f'id_{title}')
    book.set_title(title)
    book.set_language('es')
    book.add_author(author)

    # Abrimos el PDF
    doc = fitz.open(pdf_path)
    
    chapters = []
    image_counter = 0  

    for page_num, page in enumerate(doc):
        
        page_dict = page.get_text("dict")
        blocks = page_dict["blocks"]
        
        chapter_content = f"<h1>Página {page_num + 1}</h1>"
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
                ext = block["ext"] # png, jpeg, etc.
                
                image_filename = f"image_{page_num}_{image_counter}.{ext}"
                image_counter += 1

                epub_img = epub.EpubImage()
                epub_img.file_name = image_filename
                epub_img.media_type = f"image/{ext}"
                epub_img.content = image_bytes
                
                book.add_item(epub_img)

                chapter_content += f'<p style="text-align:center"><img src="{image_filename}" alt="Imagen del PDF" style="max-width:100%"/></p>'
                has_content = True

        if has_content:
            chapter_title = f'Página {page_num + 1}'
            chapter_filename = f'chap_{page_num + 1}.xhtml'
            
            c = epub.EpubHtml(title=chapter_title, file_name=chapter_filename, lang='es')
            c.content = chapter_content
            
            book.add_item(c)
            chapters.append(c)

    book.toc = (tuple(chapters))
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    style = 'body { font-family: Helvetica, Arial, sans-serif; } img { max-width: 100%; }'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    book.spine = ['nav'] + chapters
    epub.write_epub(output_path, book, {})
    
    doc.close()
    return output_path