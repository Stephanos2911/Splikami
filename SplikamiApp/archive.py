from PIL import Image
import pytesseract, io, fitz, gc
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.apps import apps
from .utils import time_function

@time_function
def handle_pdf(uploaded_file, document):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    total_pages = doc.page_count

    # Process document thumbnail and metadata
    first_page = doc.load_page(0)
    first_pixmap = first_page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), colorspace='rgb', alpha=False)
    first_image = Image.frombytes("RGB", (first_pixmap.width, first_pixmap.height), first_pixmap.samples)
    thumbnail_io = io.BytesIO()
    first_image.thumbnail((first_image.width * 75 / 300, first_image.height * 75 / 300))
    first_image.save(thumbnail_io, format='JPEG', quality=25)
    
    # Set thumbnail data to document
    document.page_count = total_pages
    document._thumbnail_data = ContentFile(thumbnail_io.getvalue())
    document.save()

    # Close and cleanup resources right after use
    first_image.close()
    first_pixmap = None
    gc.collect()

    def process_page(pageNum):
        # Get the Page model using get_model to avoid circular import
        Page = apps.get_model('SplikamiApp', 'Page')
        page = doc.load_page(pageNum)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), colorspace='rgb', alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

        # Prepare image data
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG', quality=80)
        
        # Prepare thumbnail data
        thumb_io = io.BytesIO()
        image.thumbnail((image.width * 75 / 300, image.height * 75 / 300))
        image.save(thumb_io, format='JPEG', quality=25)

        # Extract text
        extracted_text = pytesseract.image_to_string(image.convert('L'))
        if isinstance(extracted_text, tuple):
            extracted_text = extracted_text[0]

        # Create and save page object with the correct file data
        page_obj = Page(
            document=document,
            text=extracted_text,
            page_number=pageNum + 1,
        )
        # Attach the file data to be handled by the model's save method
        page_obj._image_data = ContentFile(img_io.getvalue())
        page_obj._thumbnail_data = ContentFile(thumb_io.getvalue())
        page_obj.save()

        # Free memory after processing the page
        image.close()
        page = None
        pixmap = None
        img_io = None
        thumb_io = None
        gc.collect()

    # Process pages concurrently
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_page, pageNum) for pageNum in range(total_pages)]
        for future in as_completed(futures):
            future.result()

    # Free up PDF resources
    doc.close()

@time_function
def handle_image(uploaded_file, document):
    # Get the Page model using get_model to avoid circular import
    Page = apps.get_model('SplikamiApp', 'Page')
    uploaded_file.seek(0) 
    file_content = uploaded_file.read()
    image = Image.open(io.BytesIO(file_content)) 

    # Save the original image
    img_io = io.BytesIO()
    image.save(img_io, format='PNG')
    img_io.seek(0)
    extracted_text = pytesseract.image_to_string(image.convert('L'))
    if isinstance(extracted_text, tuple):
        extracted_text = extracted_text[0]

    # Create thumbnail
    thumbnail_io = io.BytesIO()
    image.thumbnail((image.width * 75 / 300, image.height * 75 / 300))
    image.save(thumbnail_io, format='PNG', quality=25)
    thumbnail_io.seek(0)

    document.page_count = 1
    document.save()

    # Create the page object
    page = Page(
        document=document,
        text=extracted_text,
        page_number=1,
    )
    # Attach the file data to be handled by the model's save method
    page._image_data = ContentFile(img_io.getvalue())
    page._thumbnail_data = ContentFile(thumbnail_io.getvalue())
    page.save()

    # Set the document's thumbnail
    document._thumbnail_data = ContentFile(thumbnail_io.getvalue())
    document.save()

    # Clean up
    image.close()
    thumbnail_io = None
    img_io = None
    gc.collect()