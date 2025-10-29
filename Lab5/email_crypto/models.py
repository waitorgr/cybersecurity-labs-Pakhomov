from django.db import models

class Message(models.Model):
    sender_email = models.EmailField()
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    encrypted_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Збережене оригінальне ім'я файлу, включно з розширенням (наприклад, "image.png")
    attachment_name = models.CharField(max_length=255, blank=True, null=True)

    # Файл зберігається у директорії 'media/encrypted/' після шифрування
    attachment_encrypted = models.FileField(upload_to='encrypted/', blank=True, null=True)

    def __str__(self):
        return f"{self.sender_email} -> {self.recipient_email} @ {self.created_at}"
