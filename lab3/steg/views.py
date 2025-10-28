import os
from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse
from .forms import HideForm, ExtractForm
from .stego import hide_message, extract_message

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', '/tmp')


def hide_view(request):
    result = None  # спочатку нічого немає
    if request.method == 'POST':
        form = HideForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            message = form.cleaned_data['message']
            key = form.cleaned_data['key'] or None
            channels = tuple(int(c) for c in form.cleaned_data['channels'])
            
            # шляхи
            in_path = os.path.join(settings.MEDIA_ROOT, image.name)
            out_name = f"stego_{image.name}"
            out_path = os.path.join(settings.MEDIA_ROOT, out_name)
            
            # запис файлу
            with open(in_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            try:
                analysis = hide_message(in_path, out_path, message, key=key, use_channels=channels)
                # формуємо результат із повним і відносним шляхом
                result = {
                    'out_path': out_path,
                    'relative_path': os.path.join(settings.MEDIA_URL, out_name).replace('\\', '/'),
                    'analysis': analysis
                }
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = HideForm()

    return render(request, 'steg/hide.html', {'form': form, 'result': result})



def extract_view(request):
    extracted = None
    if request.method == 'POST':
        form = ExtractForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.cleaned_data['image']
            key = form.cleaned_data['key'] or None
            channels = tuple(int(c) for c in form.cleaned_data['channels'])
            in_path = os.path.join(MEDIA_ROOT, image.name)
            with open(in_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            try:
                extracted = extract_message(in_path, key=key, use_channels=channels)
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = ExtractForm()
    return render(request, 'steg/extract.html', {'form': form, 'extracted': extracted})