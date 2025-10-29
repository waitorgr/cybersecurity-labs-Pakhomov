from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    secret_info = models.TextField(blank=True)  # поле, яке демонструватиме «приховані» дані

    def __str__(self):
        return f"{self.name} <{self.email}>"
