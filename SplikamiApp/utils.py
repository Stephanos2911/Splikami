import time

def time_function(func):
    """Decorator to measure execution time of a function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time} seconds.")
        return result
    return wrapper

def get_upload_path(instance, filename, prefix='', suffix=''):
    """Generic file path generator for Archive files"""
    if hasattr(instance, 'document'):
        # For Page model
        doc = instance.document
        doc_id = doc.id
        doc_title = doc.title
    else:
        # For Document model
        doc_id = instance.id
        doc_title = instance.title
        
    base_path = f'Documents/{doc_title}_{doc_id}'
    if prefix:
        base_path = f'{base_path}/{prefix}'
    return f'{base_path}/{suffix or filename}'

def document_thumbnail_path(instance, filename):
    return get_upload_path(instance, filename, suffix='thumbnail.jpg')

def page_file_path(instance, filename):
    suffix = f'page_{instance.page_number}'
    suffix += '_thumbnail.jpg' if 'thumbnail' in filename else '.jpg'
    return get_upload_path(instance, filename, prefix='pages', suffix=suffix)