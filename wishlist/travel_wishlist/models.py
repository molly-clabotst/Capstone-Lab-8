from django.db import models

# Create your models here.

class Place(models.Model):
    name = models.CharField(max_length=200)
    visited = models.BooleanField(default=False)
    user = models.ForeignKey('auth.User', null=False, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    date_visited = models.DateField(blank=True, null=False)
    photo = models.ImageField(upload_to='use_images/', blank=True, null=True)

    def __str__(self):
        return f'{self.name}, visited? {self.visited} on {self.date_visited}\nPhoto {photo_str}'