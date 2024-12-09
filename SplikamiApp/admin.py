from django.contrib import admin
from .models import Course, Event, Document, Contact, Page, Collection, Rubric, Subject
from django import forms
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.widgets import DateInput
from django.core.exceptions import ValidationError
from .archive import handle_pdf, handle_image
from django.utils.html import mark_safe
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import GroupAdmin
from django.contrib.admin import AdminSite
import threading
from django.core.cache import cache

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'id', 'description')  # Fields to display in the list view
    search_fields = ('title', 'id', 'description')  # Fields to search in the admin
    readonly_fields = ('date_added',)
    filter_horizontal = ('students',)  

    formfield_overrides = {
        models.ManyToManyField: {'widget': FilteredSelectMultiple("Students", is_stacked=False)},
    }

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "students":
            kwargs["required"] = False  # Ensure the field is not marked as required
            kwargs["queryset"] = User.objects.filter(is_active=True)  # Filter to only active users or any other condition
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start_time', 'location')
    search_fields = ('title', 'description', 'location')
    fields = ('title', 'description', 'start_time', 'location', 'url', 'image', 'pdf')

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'company', 'phone_number', 'subject', 'submitted_at')
    search_fields = ('name', 'email', 'subject', 'company', 'submitted_at')
    
#archive

# Inline admin for Page to be used within DocumentAdmin
class PageInline(admin.TabularInline):
    model = Page
    fields = ('page_str', 'page_number')  # Display the custom __str__ method alongside page_number
    readonly_fields = ('page_str', 'page_number')  # Make these fields read-only
    extra = 0
    can_delete = False
    show_change_link = True

    def page_str(self, obj):
        return str(obj)  # This calls the __str__ method of the Page model

    page_str.short_description = 'Page Info'  # Optional: Customize the column header

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('page_number')

class DocumentInline(admin.StackedInline):  
    model = Document
    fields = ('title', 'publish_date', 'rubric', 'subject')
    readonly_fields = ('title', 'publish_date', 'rubric', 'subjects')
    extra = 0
    can_delete = True
    show_change_link = True
    inlines = [PageInline]  # Embed the PageInline within DocumentInline

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('rubrics').prefetch_related('subjects').order_by('publish_date')

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'collection_thumbnail')  # Add the thumbnail to the list display
    search_fields = ('name',)
    readonly_fields = ('created_at', 'collection_thumbnail')  # Make thumbnail display read-only
    list_filter = ('created_at',)
    fields = ('name', 'description', 'thumbnail', 'collection_thumbnail', 'created_at')  # Add thumbnail to the form

    def collection_thumbnail(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" style="max-width: 150px;"/>')
        return "-"

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:  # Only include DocumentInline if the object already exists (i.e., is being edited)
            inline_instances = [DocumentInline(self.model, self.admin_site)]
        return inline_instances

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('collections') # Clear the cache for collections after saving a collection

# Admin configuration for rubric
class RubricAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('rubrics')  # Clear the cache for rubrics after saving a rubric

# Admin configuration for Subject
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.delete('subjects')  # Clear the cache for subjects after saving a subject
    
# Admin configuration for Document
class DocumentAdminForm(forms.ModelForm):
    uploaded_file = forms.FileField(required=False, help_text="Upload a PDF or an image file")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make uploaded_file required only when creating a new document
        if not self.instance.pk:  # If this is a new document
            self.fields['uploaded_file'].required = True

    class Meta:
        model = Document
        exclude = ('thumbnail', 'page_count', 'added_by', 'date_added')
        widgets = {
            'subject': FilteredSelectMultiple("Subjects", is_stacked=False),
            'rubric': FilteredSelectMultiple("Rubrics", is_stacked=False), 
            'publish_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'), 
        }

    def clean_uploaded_file(self):
        uploaded_file = self.cleaned_data.get('uploaded_file')
        if uploaded_file:
            # Get file extension and convert to lowercase
            file_ext = uploaded_file.name.lower().split('.')[-1]
            
            # Define allowed extensions and their corresponding MIME types
            ALLOWED_TYPES = {
                'pdf': 'application/pdf',
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'jpeg': 'image/jpeg'
            }
            
            if file_ext not in ALLOWED_TYPES:
                raise ValidationError(f'Invalid file extension. Allowed extensions are: {", ".join(ALLOWED_TYPES.keys())}')
            
            # Check MIME type
            file_type = uploaded_file.content_type
            if file_type not in ALLOWED_TYPES.values():
                raise ValidationError(f'Invalid file type. File appears to be {file_type}')
            
            # Cross-validate extension with MIME type
            expected_type = ALLOWED_TYPES[file_ext]
            if file_type != expected_type:
                raise ValidationError(f'File extension does not match its content type')
            
        return uploaded_file

class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    inlines = [PageInline]

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:  # Only include PageInline if the object already exists (i.e., is being edited)
            inline_instances = [PageInline(self.model, self.admin_site)]
        return inline_instances
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # If the document is being created for the first time
            obj.added_by = request.user
        
        uploaded_file = form.cleaned_data.get('uploaded_file')
        
        # Only process the file if one was uploaded
        if uploaded_file:
            obj.save()
            def background_task():
                if uploaded_file.name.lower().endswith('.pdf'):
                    handle_pdf(uploaded_file=uploaded_file, document=obj)
                elif uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    handle_image(uploaded_file=uploaded_file, document=obj)
            threading.Thread(target=background_task).start()
        
        super().save_model(request, obj, form, change)
        cache.delete('documents')
        
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('page_count', 'added_by', 'date_added', 'thumbnail')  
        return () 

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # If editing an existing object
            if 'uploaded_file' in form.base_fields:
                del form.base_fields['uploaded_file']
        return form

    def document_thumbnail(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" style="max-width: 150px;"/>')
        return "-"
    document_thumbnail.short_description = 'Thumbnail'

    list_display = ('title', 'collection', 'document_thumbnail', 'page_count')
    list_filter = ('collection', 'rubric', 'subject') 
    search_fields = ('title', 'collection__name', 'rubrics__name')

# Admin form for Page with customization options
class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        exclude = ('thumbnail',)
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
        }

class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    readonly_fields = ('document', 'page_number', 'thumbnail' ,'image')

    def document_str(self, obj):
        return str(obj)  

    document_str.short_description = 'Title'  
    list_display = ('document_str', 'document', 'page_number')
    search_fields = ('document__title',)
    list_filter = ('document', 'page_number')
    
admin_site = AdminSite()
admin_site.register(User, UserAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Course, CourseAdmin)
admin_site.register(Event, EventAdmin)
admin_site.register(Contact, ContactAdmin)
admin_site.register(Collection, CollectionAdmin)
admin_site.register(Rubric, RubricAdmin)
admin_site.register(Subject, SubjectAdmin)
admin_site.register(Document, DocumentAdmin)
admin_site.register(Page, PageAdmin)
