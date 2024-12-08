# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.utils.html import escape
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Course, Document, Page, Collection, Rubric, Subject
from .models import Event as EventModel
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .forms import ContactForm, CustomUserCreationForm
from icalendar import Calendar, Event
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.contrib.postgres.search import SearchVector
from django.views.decorators.cache import cache_page

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
            
        if user is None:
            return JsonResponse({'error': 'Inloggen mislukt. Controleer uw gebruikersnaam/wachtwoord of neem contact op met een beheerder om uw account te activeren.'}, status=400)
        login(request, user)
        # Redirect to the page the user was on before logging in
        next_page = request.POST.get('next', '/')
        if not url_has_allowed_host_and_scheme(next_page, allowed_hosts={request.get_host()}):
            next_page = '/'
        return redirect(next_page)
     
    return JsonResponse({'error': 'Invalid request method'}, status=405)
    
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # set is active to false to prevent login for unverified users
            user.save()
            return HttpResponse(status=200)
        else:
            return JsonResponse(form.errors, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def online_courses(request):
    # Get all courses with only the title and description, sorted by date added (latest first)
    all_courses = Course.objects.only('title', 'description').order_by('-date_added')
    
    if request.user.is_authenticated:
        # Get the courses the user is enrolled in, sorted by date added
        user_courses = Course.objects.filter(students=request.user).only('title', 'description', 'link', 'pdf').order_by('-date_added')
    
        # Get the courses the user is NOT enrolled in, sorted by date added
        available_courses = all_courses.exclude(id__in=user_courses.values_list('id', flat=True))
        
        context = {
            'all_courses': available_courses,
            'user_courses': user_courses
        }
    else:
        # If the user is not authenticated, return all courses with only title and description, sorted by date added
        context = {
            'all_courses': all_courses
        }

    return render(request, 'SplikamiApp/online_courses.html', context)

def open_course(request, course_id):
    # If the user is not logged in, redirect to the courses overview
    if not request.user.is_authenticated:
        return redirect(reverse('online_courses'))

    # Get the course, limiting the fields retrieved
    course = get_object_or_404(
        Course.objects.only('id', 'title', 'pdf', 'link', 'students'),
        id=course_id
    )

    # Check if the user is enrolled in the course
    if request.user not in course.students.all():
        # Redirect to the courses overview if the user is not enrolled
        return redirect(reverse('online_courses'))

    # Redirect to the external link if it exists, otherwise render the PDF view
    if course.link:
        return redirect(course.link)
    else:
        return render(request, 'SplikamiApp/course_pdf.html', {'course': course})
    
## Archive
@csrf_exempt
@login_required(login_url='/?login_required=true')
def archive(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = request.POST
    else:
        # Get filters from GET parameters using names
        data = {
            'rubric': request.GET.get('rubric'),
            'subject': request.GET.get('subject'),
            'collections': request.GET.get('collections'),
            'q': request.GET.get('q', ''),
            'page': request.GET.get('page', 1),
            'sort': request.GET.get('sort', 'publish_date'),
            'order': request.GET.get('order', 'desc'),
        }

    # Get parameters
    rubric_name = data.get('rubric')
    subject_name = data.get('subject')
    collection_name = data.get('collections')
    query = data.get('q', '')
    page_number = data.get('page', 1)
    sort_field = data.get('sort', 'publish_date')
    sort_order = data.get('order', 'desc')

    documents = Document.objects.select_related('collection').only(
        'id', 'title', 'thumbnail', 'publish_date', 'page_count', 'collection__name'
    )

    # Apply filters
    if rubric_name:
        documents = documents.filter(rubric__name__iexact=rubric_name)
    if subject_name:
        documents = documents.filter(subject__name__iexact=subject_name)
    if collection_name:
        documents = documents.filter(collection__name__iexact=collection_name)

    # Apply search filter
    if query:
        documents = documents.filter(title__icontains=query)

    # Get total number of results after applying filters
    total_results = documents.count()

    # Apply sorting
    if sort_field in ['publish_date', 'title']:
        if sort_order == 'asc':
            documents = documents.order_by(sort_field)
        else:
            documents = documents.order_by('-' + sort_field)
    else:
        documents = documents.order_by('-publish_date')  # Default sorting

    # Paginate the documents
    paginator = Paginator(documents, 9)
    page_obj = paginator.get_page(page_number)

    # Cache rubrics, subjects, and collections
    rubrics = cache.get('rubrics')
    if not rubrics:
        rubrics = list(Rubric.objects.only('id', 'name').all())
        cache.set('rubrics', rubrics, 3600)  # Cache for 1 hour

    subjects = cache.get('subjects')
    if not subjects:
        subjects = list(Subject.objects.only('id', 'name').all())
        cache.set('subjects', subjects, 3600)

    collections = cache.get('collections')
    if not collections:
        collections = list(Collection.objects.only('id', 'name').all())
        cache.set('collections', collections, 3600)

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Render the document list and pagination components
        html = render_to_string('SplikamiApp/_document_list.html', {'documents': page_obj}, request=request)
        pagination_html = render_to_string('SplikamiApp/_pagination.html', {'documents': page_obj}, request=request)
        return JsonResponse({
            'html': html, 
            'pagination_html': pagination_html, 
            'total_results': total_results
        })
    else:
        # Initial page load with documents included in context
        context = {
            'documents': page_obj,
            'rubrics': rubrics,
            'subjects': subjects,
            'collections': collections,
            'total_results': total_results,
            'current_filters': {
                'rubric': rubric_name,
                'subject': subject_name,
                'collection': collection_name,
            },
        }
        return render(request, 'SplikamiApp/archive.html', context)

def highlight_match(text, query):
    # Escape HTML and highlight the match
    escaped_query = escape(query)
    highlighted = text.replace(escaped_query, f'<strong>{escaped_query}</strong>')
    return highlighted

def archive_search(request):
    query = request.GET.get('q', '')
    if query:
        # Search in documents' titles
        document_results = Document.objects.filter(title__icontains=query)

        # Search in pages' text content
        page_results = Page.objects.filter(text__icontains=query).select_related('document')

        # Combine the results
        results = []
        for doc in document_results:
            results.append({
                'type': 'document',
                'id': doc.id,
                'title': highlight_match(doc.title, query),
                'thumbnail_url': doc.thumbnail.url if doc.thumbnail else None,
                'publish_date': doc.publish_date,
                'page_count': doc.page_count,
            })

        for page in page_results:
            # Find the match and create a snippet
            match_start = page.text.lower().find(query.lower())
            snippet_start = max(match_start - 50, 0)
            snippet_end = min(match_start + len(query) + 50, len(page.text))
            snippet = page.text[snippet_start:snippet_end]
            snippet = highlight_match(snippet, query)
            results.append({
                'type': 'page',
                'document_id': page.document.id,
                'page_number': page.page_number,
                'title': f"{page.document.title} - Pagina {page.page_number}",
                'snippet': f"...{snippet}...",
                'thumbnail_url': page.thumbnail.url if page.thumbnail else None, 
            })

        # return the results as an html component 
        html = render_to_string('SplikamiApp/_search_results.html', {'results': results})

        return JsonResponse({'html': html})

    return JsonResponse({'html': ''})

@login_required
def view_document(request, id, page=1):
    # Include rubrics and subjects in the query
    document = get_object_or_404(
        Document.objects.only('id', 'title', 'thumbnail', 'page_count'),
        pk=id
    )
    pages = document.pages.only('page_number', 'image', 'thumbnail', 'text').order_by('page_number')

    pages_data = [
        {
            'page_number': page.page_number,
            'image': page.image.url,
            'thumbnail': page.thumbnail.url,
            'text_snippet': page.text[:100] if page.text else ''  # Get the first 100 characters of the text
        }
        for page in pages
    ]
    
    pages_json = json.dumps(pages_data, cls=DjangoJSONEncoder)

    # Generate a range of page numbers
    pages_range = range(1, len(pages) + 1)

    return render(request, 'SplikamiApp/view_document.html', {
        'document': document,
        'pages_json': pages_json,
        'current_page': page,
        'pages_range': pages_range
    })

def contact_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'Bedankt voor uw bericht. We nemen spoedig contact met u op.'})
        return JsonResponse({'message': 'Er is iets misgegaan tijdens het verzenden, check het formulier nog een keer.'})

## Events
def events(request):
    now = timezone.now()
    upcoming_events = EventModel.objects.filter(start_time__gte=now).order_by('start_time')
    past_events = EventModel.objects.filter(start_time__lt=now).order_by('-start_time')
    
    # Extract the first upcoming event
    first_upcoming_event = upcoming_events.first() if upcoming_events.exists() else None

    context = {
        'first_upcoming_event': first_upcoming_event,
        'upcoming_events': upcoming_events[1:],  # Exclude the first upcoming event from this list
        'past_events': past_events,
    }
    return render(request, 'SplikamiApp/events.html', context)

def generate_ics(request, event_id):
    event = EventModel.objects.get(pk=event_id)  # Access your Django model using EventModel
    cal = Calendar()
    cal_event = Event()  # This is the icalendar Event, not your Django model

    cal_event.add('summary', event.title)
    cal_event.add('dtstart', event.start_time)  # Only using start_time since end_time is removed
    cal_event.add('location', event.location)
    cal_event.add('description', event.description)

    cal.add_component(cal_event)

    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename={event.title}.ics'
    return response

# Simple static pages
@cache_page(60 * 60 * 24)
def home(request):
    return render(request, 'SplikamiApp/home.html')

@cache_page(60 * 60 * 24)
def education(request):
    return render(request, 'SplikamiApp/education.html')

@cache_page(60 * 60 * 24)  
def aboutus(request):
    return render(request, 'SplikamiApp/about.html')

def logout_view(request):
    logout(request)
    
    # Determine where to redirect after logout
    next_url = request.GET.get('next', '/')
    
    # If the user is on the archive page, redirect to the home page instead
    if next_url in ['/archive']:
        next_url = '/'
            
    return redirect(next_url)