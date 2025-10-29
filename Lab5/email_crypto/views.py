from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ComposeForm, DecryptForm
from .models import Message
from .utils.crypto import encrypt_message, decrypt_message, encrypt_bytes, decrypt_bytes
from django.core.files.base import ContentFile
import mimetypes
from django.http import HttpResponse

def compose(request):
    if request.method == "POST":
        form = ComposeForm(request.POST, request.FILES)
        if form.is_valid():
            sender = form.cleaned_data['sender_email']
            recipient = form.cleaned_data['recipient_email']
            personal = form.cleaned_data['personal_string']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']
            attachment = form.cleaned_data.get('attachment')

            # use recipient email as salt (stable per recipient)
            salt = recipient.encode('utf-8')

            encrypted_body = encrypt_message(body, personal, salt)

            m = Message.objects.create(
                sender_email=sender,
                recipient_email=recipient,
                subject=subject,
                encrypted_body=encrypted_body
            )

            if attachment:
                raw = attachment.read()  # читаємо байти оригінального файлу
                enc = encrypt_bytes(raw, personal, salt)  # шифруємо байти
                m.attachment_name = attachment.name  # зберігаємо ім'я з розширенням
                m.attachment_encrypted.save(attachment.name + '.enc', ContentFile(enc))  # зберігаємо зашифрований файл
                m.save()


            return redirect('email_crypto:outbox')  # or detail page
    else:
        form = ComposeForm()
    return render(request, 'email_crypto/compose.html', {'form': form})

def outbox(request):
    qs = Message.objects.all().order_by('-created_at')[:50]
    return render(request, 'email_crypto/outbox.html', {'messages': qs})

def detail(request, pk):
    m = get_object_or_404(Message, pk=pk)
    decrypt_result = None
    error = None
    if request.method == "POST":
        form = DecryptForm(request.POST)
        if form.is_valid():
            personal = form.cleaned_data['personal_string']
            recipient = form.cleaned_data['recipient_email']
            # ensure recipient matches (basic check)
            if recipient != m.recipient_email:
                error = "Вказаний email отримувача не співпадає."
            else:
                try:
                    plain = decrypt_message(m.encrypted_body, personal, recipient.encode('utf-8'))
                    decrypt_result = plain
                except Exception as e:
                    error = "Помилка розшифрування — перевірте персональний рядок."

    else:
        form = DecryptForm(initial={'recipient_email': m.recipient_email})
    return render(request, 'email_crypto/detail.html', {
        'message': m,
        'form': form,
        'decrypted': decrypt_result,
        'error': error
    })

def download_attachment(request, pk):
    m = get_object_or_404(Message, pk=pk)

    if request.method == "POST":
        personal = request.POST.get('personal_string')
        recipient = request.POST.get('recipient_email')

        if recipient != m.recipient_email:
            return render(request, 'email_crypto/download.html', {'error': 'Recipient mismatch', 'message': m})

        try:
            # читаємо байти з файлу
            encrypted_data = m.attachment_encrypted.read()
            raw = decrypt_bytes(encrypted_data, personal, recipient.encode('utf-8'))

            # визначаємо правильний MIME-type по оригінальному імені
            mime_type, _ = mimetypes.guess_type(m.attachment_name)
            if not mime_type:
                mime_type = 'application/octet-stream'

            resp = HttpResponse(raw, content_type=mime_type)
            resp['Content-Disposition'] = f'attachment; filename="{m.attachment_name}"'
            return resp

        except Exception as e:
            return render(request, 'email_crypto/download.html', {'error': f'Невірний ключ або файл пошкоджено ({e})', 'message': m})

    return render(request, 'email_crypto/download.html', {'message': m})
