from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.dateformat import DateFormat
from django.core.validators import validate_email

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    pdf = models.FileField(upload_to='courses/', null=True, blank=True, help_text='Pdf van de cursus, laat dit veld leeg als de cursus op een externe website staat.')
    link = models.URLField(null=True, blank=True, help_text='link naar de externe cursus')
    students = models.ManyToManyField(User, related_name='courses')
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    location = models.CharField(max_length=255, help_text='exacte locatie of Online')
    url = models.URLField(blank=True, null=True, help_text='Url naar de online call indien het event online is')
    image = models.ImageField(upload_to='events/', blank=True, null=True, help_text='afbeelding voor het event')
    pdf = models.FileField(upload_to='events/', blank=True, null=True, help_text='PDF met event details')

    def __str__(self):
        return self.title

class Contact(models.Model):
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True, default='')
    email = models.EmailField()
    phone_number = models.CharField(max_length=15, blank=True, default='')
    subject = models.CharField(max_length=50)
    message = models.TextField(blank=True, default='')
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
class Collection(models.Model):
    name = models.CharField(max_length=255, help_text='naam van bijvoorbeeld een krant: Extra')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to='collection_thumbnails/', blank=True, null=True, help_text='afbeelding te zien in de collectie overzicht')

    def __str__(self):
        return self.name

class Rubric(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name    
    
class Document(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, help_text='Vul dit in indien je een los document toevoegd. Als dit document onderdeel van een collectie is kun je dit veld leeglaten: de titel word automatisch bepaald.')
    date_added = models.DateTimeField(default=timezone.now, db_index=True)
    publish_date = models.DateField(blank=True, null=True, db_index=True, help_text='datum van uitgave, publicatie datum')
    thumbnail = models.ImageField(upload_to='document_thumbnails/', blank=True, null=True)
    page_count = models.IntegerField(default=0)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    collection = models.ForeignKey(Collection, related_name='documents', on_delete=models.SET_NULL, null=True, blank=True)
    rubric = models.ManyToManyField(Rubric, related_name='documents', blank=True)
    subject = models.ManyToManyField(Subject, related_name='documents', blank=True)

    def save(self, *args, **kwargs):
        # If the document is part of a collection and has a publish date
        if self.collection and self.publish_date:
            formatted_date = DateFormat(self.publish_date).format('d F Y')
            self.title = f"{self.collection.name}, {formatted_date}"
        # If there's no collection, keep the manually entered title
        elif not self.collection and not self.title:
            self.title = "Untitled Document"
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title or "Untitled Document"
    
class Page(models.Model):
    document = models.ForeignKey(Document, related_name='pages', on_delete=models.CASCADE)
    text = models.CharField(max_length=10000, blank=True, null=True)
    image = models.ImageField(upload_to='pages/')
    thumbnail = models.ImageField(upload_to='page_thumbnails/')
    page_number = models.IntegerField(default=1, db_index=True)

    def __str__(self):
        return f"{self.document.title}, page {self.page_number}"
    
# Add email validation to the User model
User._meta.get_field('username').validators.append(validate_email)