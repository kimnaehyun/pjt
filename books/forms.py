from django import forms
from .models import Book, Thread

class BookForm(forms.ModelForm):
    class Meta:
        model: Book

class ThreadForm(forms.ModelForm):
    class Meta:
        model: Thread
        fields = (
            'title',
            'content',
        )