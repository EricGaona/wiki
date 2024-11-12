import markdown2
import random
from django.shortcuts import render, redirect
from django.urls import reverse
from . import util
from django.http import HttpResponse

def index(request):
    print(request.method)
    print(request.path)
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })
# from here everything was added by me

def entry_page(request, title):
    print(request.method)  # this is for the console
    print(request.path)
    # Get the content of the requested entry
    content = util.get_entry(title)
    
    if content is None:
        # If no entry is found, render an error page
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page was not found."
        })
    
    # Convert Markdown content to HTML using markdown2
    html_content = markdown2.markdown(content)
    # If the entry exists, render the entry page
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get('q')  # Get the search query from the form
    
    if query:
        # Check if the query matches an existing encyclopedia entry
        content = util.get_entry(query)
        
        if content:
            # If an exact match is found, redirect to the entry page
            return redirect('entry_page', title=query)
         
        
        # If no exact match, look for partial matches
        all_entries = util.list_entries()  # Get a list of all entries
        matching_entries = [entry for entry in all_entries if query.lower() in entry.lower()]
        
        # Render a search results page with matching entries
        return render(request, 'encyclopedia/search_results.html', {
            'query': query,
            'matching_entries': matching_entries
        })
    
    # If no query is provided, return to the index or show an error
    return render(request, 'encyclopedia/search_results.html', {
        'query': query,
        'matching_entries': []
    })

def create_page(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # Check if the page with this title already exists
        if util.get_entry(title):
            return render(request, "encyclopedia/create_page.html", {
                "error": "An entry with this title already exists. Please choose a different title."
            })

        # Save the new entry and redirect to the new entry page
        util.save_entry(title, content)
        return redirect(reverse("entry_page", args=[title]))

    return render(request, "encyclopedia/create_page.html")


def edit_page(request, title):
    # Fetch the current content of the entry
    content = util.get_entry(title)
    
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "The requested page does not exist."
        })
    
    if request.method == "POST":
        # Get the updated content from the form
        updated_content = request.POST.get("content")

        # Save the updated content
        util.save_entry(title, updated_content)

        # Redirect to the updated entry page
        return redirect(reverse("entry_page", args=[title]))

    # Render the edit form pre-populated with the current content
    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "content": content
    })

def random_page(request):
    # Get a list of all encyclopedia entries
    entries = util.list_entries()

    if entries:
        # Choose a random entry from the list
        random_entry = random.choice(entries)

        # Redirect to the randomly selected entry's page
        return redirect(reverse("entry_page", args=[random_entry]))
    else:
        return render(request, "encyclopedia/error.html", {
            "message": "No entries found in the encyclopedia."
        })