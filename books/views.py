from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Thread
from .forms import BookForm, ThreadForm

# Create your views here.

# Book Views
def index(request):
    books = Book.objects.all()
    return render(request, 'books/index.html', {'books': books})

def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('books:index')
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})

def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form})

def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('books:index')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

# Thread Views
def thread_create(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    if request.method == 'POST':
        form = ThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.book = book
            thread.save()
            return redirect('books:book_detail', pk=book.pk)
    else:
        form = ThreadForm()
    return render(request, 'books/thread_form.html', {'form': form, 'book': book})

def thread_detail(request, book_pk, pk):
    thread = get_object_or_404(Thread, pk=pk, book__pk=book_pk)
    return render(request, 'books/thread_detail.html', {'thread': thread})

def thread_update(request, book_pk, pk):
    thread = get_object_or_404(Thread, pk=pk, book__pk=book_pk)
    if request.method == 'POST':
        form = ThreadForm(request.POST, instance=thread)
        if form.is_valid():
            form.save()
            return redirect('books:thread_detail', book_pk=book_pk, pk=thread.pk)
    else:
        form = ThreadForm(instance=thread)
    return render(request, 'books/thread_form.html', {'form': form, 'thread': thread})

def thread_delete(request, book_pk, pk):
    thread = get_object_or_404(Thread, pk=pk, book__pk=book_pk)
    if request.method == 'POST':
        thread.delete()
        return redirect('books:book_detail', pk=book_pk)
    return render(request, 'books/thread_confirm_delete.html', {'thread': thread})
