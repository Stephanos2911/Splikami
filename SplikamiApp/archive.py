from PIL import Image
import pytesseract, io, fitz, time
from .models import Page
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

def time_function(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time} seconds.")
        return result
    return wrapper
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
    thumbnail_io.seek(0)
    document.page_count = total_pages
    document.thumbnail.save(f"{document.title}_thumbnail.jpg", ContentFile(thumbnail_io.getvalue()), save=False)
    document.save()

    # Close and cleanup resources right after use
    first_image.close()
    first_pixmap = None
    gc.collect()

    def process_page(pageNum):
        page = doc.load_page(pageNum)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), colorspace='rgb', alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)

        # Save the full image directly without creating extra copies
        img_io = io.BytesIO()
        image.save(img_io, format='JPEG', quality=80)
        img_io.seek(0)
        image_key = f"documents/{document.id}/{document.title}_page_{pageNum + 1}.jpg"
        default_storage.save(image_key, ContentFile(img_io.getvalue()))

        # Create thumbnail from the same PIL image directly
        page_thumbnail_io = io.BytesIO()
        thumb_width = int(image.width * 75 / 300)
        thumb_height = int(image.height * 75 / 300)
        image.thumbnail((thumb_width, thumb_height))
        image.save(page_thumbnail_io, format='JPEG', quality=25)
        page_thumbnail_io.seek(0)
        thumbnail_key = f"documents/{document.id}/{document.title}_page_{pageNum + 1}_thumbnail.jpg"
        default_storage.save(thumbnail_key, ContentFile(page_thumbnail_io.getvalue()))

        # Perform OCR (on the in-memory downsampled image)
        extracted_text = pytesseract.image_to_string(image.convert('L'))
        if isinstance(extracted_text, tuple):
            extracted_text = extracted_text[0]

        # Save the Page object
        page_obj = Page(
            document=document,
            text=extracted_text,
            page_number=pageNum + 1,
        )
        page_obj.image.save(f"{document.title}_page_{pageNum + 1}.jpg", ContentFile(img_io.getvalue()), save=False)
        page_obj.thumbnail.save(f"{document.title}_page_{pageNum + 1}_thumbnail.jpg", ContentFile(page_thumbnail_io.getvalue()), save=False)
        page_obj.save()

        # Free memory after processing the page
        image.close()
        page = None
        pixmap = None
        img_io = None
        page_thumbnail_io = None
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
    uploaded_file.seek(0)  # Ensure the file pointer is at the start
    file_content = uploaded_file.read()  # Read the file content into memory
    image = Image.open(io.BytesIO(file_content))  # Open the image from the in-memory content

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
    page.image.save(f"{document.title}.png", ContentFile(img_io.getvalue()), save=False)
    page.thumbnail.save(f"{document.title}_thumbnail.png", ContentFile(thumbnail_io.getvalue()), save=False)
    page.save()

    # Set the document's thumbnail
    document.thumbnail.save(f"{document.title}_thumbnail.png", ContentFile(thumbnail_io.getvalue()), save=False)
    document.save()

    # Clean up
    image.close()
    thumbnail_io = None
    img_io = None
    gc.collect()