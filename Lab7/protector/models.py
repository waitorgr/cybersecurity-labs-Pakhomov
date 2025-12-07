from django.db import models

class FileRecord(models.Model):
    original_name = models.CharField(max_length=255)
    uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)
    container_image = models.ImageField(upload_to='containers/', null=True, blank=True)

    size_original = models.IntegerField(default=0)
    size_cipher = models.IntegerField(default=0)
    size_container = models.IntegerField(default=0)

    time_sign_ms = models.FloatField(default=0.0)
    time_encrypt_ms = models.FloatField(default=0.0)
    time_stego_ms = models.FloatField(default=0.0)

    nonce = models.BinaryField(null=True, blank=True)
    salt = models.BinaryField(null=True, blank=True)

    success_restore = models.BooleanField(default=False)
    signature_valid = models.BooleanField(default=False)

    signature_bytes = models.BinaryField(null=True, blank=True)
    cipher_bytes = models.BinaryField(null=True, blank=True)
    
    password = models.CharField(max_length=255, null=True, blank=True)
