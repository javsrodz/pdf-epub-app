import fitz  # PyMuPDF
from ebooklib import epub
import os

def pdf_to_epub(pdf_path, output_path, title="Sin Título", author="Anónimo"):
    doc = None
    try:
        # Intentar abrir el PDF
        doc = fitz.open(pdf_path)
        
        # VALIDACIÓN 1: ¿Está encriptado?
        if doc.is_encrypted:
            raise ValueError("El archivo PDF está protegido con contraseña.")
            
        # VALIDACIÓN 2: ¿Tiene páginas?
        if len(doc) == 0:
            raise ValueError("El PDF parece estar vacío.")

        book = epub.EpubBook()
        book.set_identifier(f'id_{title.replace(" ", "_")}')
        book.set_title(title)
        book.set_language('es')
        book.add_author(author)

        # Generar portada con manejo de error específico
        try:
            first_page = doc[0]
            pix = first_page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            book.set_cover("cover.jpg", pix.tobytes("jpg"))
        except Exception as e:
            print(f"Aviso: No se pudo generar portada, usando genérica. Motivo: {e}")

        chapters = []
        image_counter = 0

        for page_num, page in enumerate(doc):
            try:
                page_dict = page.get_text("dict")
                blocks = page_dict["blocks"]
                chapter_content = f"<h1>{title} - Página {page_num + 1}</h1>"
                has_content = False

                for block in blocks:
                    if block["type"] == 0: # Texto
                        text = " ".join([span["text"] for line in block["lines"] for span in line["spans"]])
                        if text.strip():
                            chapter_content += f"<p>{text.strip()}</p>"
                            has_content = True
                    elif block["type"] == 1: # Imagen
                        try:
                            image_filename = f"img_{page_num}_{image_counter}.{block['ext']}"
                            epub_img = epub.EpubImage()
                            epub_img.file_name = image_filename
                            epub_img.media_type = f"image/{block['ext']}"
                            epub_img.content = block["image"]
                            book.add_item(epub_img)
                            chapter_content += f'<p style="text-align:center"><img src="{image_filename}" style="max-width:100%"/></p>'
                            image_counter += 1
                            has_content = True
                        except:
                            continue # Si una imagen falla, seguimos con el texto

                if has_content:
                    c = epub.EpubHtml(title=f'Pág {page_num+1}', file_name=f'chap_{page_num+1}.xhtml', lang='es')
                    c.content = chapter_content
                    book.add_item(c)
                    chapters.append(c)
            except Exception as e:
                print(f"Error procesando página {page_num}: {e}")
                continue

        # Finalización del libro
        book.toc = (tuple(chapters))
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", 
                            content='body { font-family: sans-serif; } img { max-width: 100%; }')
        book.add_item(nav_css)
        book.spine = ['nav'] + chapters
        
        epub.write_epub(output_path, book, {})
        return True

    except Exception as e:
        # Re-lanzamos el error para que app.py lo cachee
        raise Exception(f"Fallo en la conversión: {str(e)}")
    finally:
        if doc:
            doc.close()