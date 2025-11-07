from django import forms
from .models import Book, Thread

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields ='__all__'

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = (
            'title',
            'content',
        )