from django.forms.widgets import TextInput
from django.shortcuts import render
from . import util
from markdown2 import Markdown
from django.http import HttpResponseRedirect, request
from django import forms
from django.urls import reverse
from random import choice

class NewPageForm(forms.Form):
    newTitle = forms.CharField(label='Title', widget=forms.TextInput(attrs={'placeholder':'Enter Title'}))
    content = forms.CharField(label='Write a content in markdown', widget=forms.Textarea(attrs={'placeholder':'Enter markdown content', 'class': 'textarea'}))
    edited = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    markdowner = Markdown()
    
    if util.get_entry(entry):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdowner.convert(util.get_entry(entry)),
            "title": entry
    })
    else:
        return render(request, "encyclopedia/entry.html", {
            "error": f"Sorry, there's no {entry} page. Try again, please"
        })

def search(request):
    query = request.GET.get('q', '')
    
    if util.get_entry(query):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry': query }))
    else:
        matches = []
        for entry in util.list_entries():
            if query.lower() in entry.lower():
                matches.append(entry)
        return render(request, "encyclopedia/index.html", {
            'entries': matches,
            'search': True,
            'value': query
        })

#found info there https://docs.djangoproject.com/en/3.2/topics/forms/
def newPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            newTitle = form.cleaned_data["newTitle"]
            content = form.cleaned_data["content"]
            if (util.get_entry(newTitle) is None or form.cleaned_data["edited"] is True):
                util.save_entry(newTitle, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry': newTitle }))
            else:
                markdowner = Markdown()
                return render(request, "encyclopedia/existingPage.html", {
                    'exist': True
                })
        else:
            return render(request, "encyclopedia/newPage.html", {
                    'form': form,
                    'exist': False
                })
    else:
        form = NewPageForm()
        return render(request, "encyclopedia/newPage.html", {
            'form': form,
            'exist': False
        })

#found the idea here https://github.com/EgidioHPaixao/web50-projects-2020-x-wiki
def edit(request, entry):
    mdPage = util.get_entry(entry)
    if mdPage:
        form = NewPageForm()
        form.fields["newTitle"].initial = entry
        form.fields["newTitle"].widget = forms.HiddenInput()
        form.fields["content"].initial = mdPage
        form.fields["edited"].initial = True
        return render(request, "encyclopedia/newPage.html", {
            'form': form,
            'edited': form.fields["edited"].initial,
            'title': form.fields["newTitle"].initial
        })

def random(request):
    entries = util.list_entries()
    randomPage = choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': randomPage}))