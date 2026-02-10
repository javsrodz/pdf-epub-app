import fitz  # PyMuPDF
from ebooklib import epub
import os

def pdf_to_epub(pdf_path, output_path):
    """
    Convierte un archivo PDF a EPUB extrayendo el texto plano.
    """
    
    # 1. Crear el objeto libro EPUB
    book = epub.EpubBook()
    
    # Metadatos básicos (en un futuro, estos pueden venir del frontend)
    filename = os.path.basename(pdf_path)
    title = os.path.splitext(filename)[0]
    book.set_identifier(f'id_{title}')
    book.set_title(title)
    book.set_language('es')
    book.add_author('Usuario de la App')

    # 2. Abrir el PDF y extraer contenido
    doc = fitz.open(pdf_path)
    
    chapters = []
    
    # Iteramos por cada página del PDF
    for page_num, page in enumerate(doc):
        # Extraemos el texto respetando bloques (parrafos)
        text = page.get_text("text")
        
        # Limpieza básica: Si la página está vacía, la saltamos
        if not text.strip():
            continue

        # Crear un capítulo por página (o podrías agruparlos)
        chapter_title = f'Página {page_num + 1}'
        chapter = epub.EpubHtml(title=chapter_title, 
                                file_name=f'chap_{page_num + 1}.xhtml', 
                                lang='es')
        
        # Convertimos los saltos de línea en formato HTML básico para el EPUB
        # (Aquí es donde se puede mejorar mucho la lógica de formateo después)
        content_html = "<h1>" + chapter_title + "</h1>"
        paragraphs = text.split('\n')
        for p in paragraphs:
            if p.strip():
                content_html += f"<p>{p}</p>"
        
        chapter.content = content_html
        
        # Añadir capítulo al libro
        book.add_item(chapter)
        chapters.append(chapter)

    # 3. Definir la estructura del libro (Table of Contents)
    book.toc = (tuple(chapters))

    # Añadir archivos de navegación necesarios para EPUB (NCX y NAV)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Orden de lectura (Spine)
    book.spine = ['nav'] + chapters

    # 4. Guardar el archivo final
    epub.write_epub(output_path, book, {})
    
    return output_path

# --- Bloque de prueba (solo para ejecutar localmente y verificar) ---
if __name__ == "__main__":
    # Crea un archivo dummy o usa uno real para probar
    try:
        print("Iniciando conversión de prueba...")
        # pdf_to_epub("documento_prueba.pdf", "salida_prueba.epub")
        print("¡Conversión completada! Revisa la carpeta.")
    except Exception as e:
        print(f"Error: {e}")