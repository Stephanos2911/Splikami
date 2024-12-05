import os
import json
import django
from django.core.files import File
from .models import Document, User, Collection, Rubric, Subject
from .archive import handle_pdf, handle_image

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SplikamiProject.settings')
django.setup()

def load_json_data(file_path):
    if not os.path.exists(file_path):
        print(f"JSON file {file_path} does not exist.")
        return []
    with open(file_path, 'r') as json_file:
        return json.load(json_file)

def seed_collections(json_file_path):
    collections_data = load_json_data(json_file_path)
    for collection_data in collections_data:
        Collection.objects.get_or_create(
            name=collection_data['name'],
            defaults={'description': collection_data.get('description')}
        )

def seed_rubrics(json_file_path):
    rubrics_data = load_json_data(json_file_path)
    for rubric_data in rubrics_data:
        Rubric.objects.get_or_create(
            name=rubric_data['name'],
            defaults={'description': rubric_data.get('description')}
        )

def seed_subjects(json_file_path):
    subjects_data = load_json_data(json_file_path)
    for subject_data in subjects_data:
        Subject.objects.get_or_create(
            name=subject_data['name']
        )

def validate_references(documents_data):
    for doc_data in documents_data:
        if 'collection' in doc_data:
            if not Collection.objects.filter(name=doc_data['collection']).exists():
                print(f"Collection '{doc_data['collection']}' does not exist.")
                return False
        if 'rubrics' in doc_data:
            for rubric in doc_data['rubrics']:
                if not Rubric.objects.filter(name=rubric).exists():
                    print(f"Rubric '{rubric}' does not exist.")
                    return False
        if 'subjects' in doc_data:
            for subject in doc_data['subjects']:
                if not Subject.objects.filter(name=subject).exists():
                    print(f"Subject '{subject}' does not exist.")
                    return False
    return True

def seed_documents(json_file_path, pdf_folder_path):
    documents_data = load_json_data(json_file_path)
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found.")
        return

    if not validate_references(documents_data):
        print("Validation failed. Ensure all collections, rubrics, and subjects exist before seeding documents.")
        return

    for doc_data in documents_data:
        filename = doc_data.get('filename')
        if not filename:
            print("No filename specified for a document.")
            continue

        file_path = os.path.join(pdf_folder_path, filename)
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            continue

        with open(file_path, 'rb') as file:
            document = Document(
                title=doc_data.get('title', os.path.splitext(filename)[0]),
                publish_date=doc_data.get('publish_date'),
                added_by=admin_user,
                collection=Collection.objects.filter(name=doc_data.get('collection')).first(),
            )
            document.save()

            if 'rubrics' in doc_data:
                rubrics = Rubric.objects.filter(name__in=doc_data['rubrics'])
                document.rubric.set(rubrics)
            if 'subjects' in doc_data:
                subjects = Subject.objects.filter(name__in=doc_data['subjects'])
                document.subject.set(subjects)

            if filename.lower().endswith('.pdf'):
                handle_pdf(uploaded_file=File(file), document=document)
            elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                handle_image(uploaded_file=File(file), document=document)
            print(f"Inserted document: {document.title}")

if __name__ == "__main__":
    base_path = os.path.join(os.path.dirname(__file__), 'seedData')
    seed_collections(os.path.join(base_path, 'collections.json'))
    seed_rubrics(os.path.join(base_path, 'rubrics.json'))
    seed_subjects(os.path.join(base_path, 'subjects.json'))
    seed_documents(os.path.join(base_path, 'documents.json'), base_path)