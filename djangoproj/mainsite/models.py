from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location=settings.POSTER_PATH, base_url= settings.POSTER_URL)

class Show(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length = 120)
    plot = models.CharField(max_length = 400, default = "To Add")
    image = models.ImageField(storage = fs, upload_to = 'posters/', blank = True, null=True)
    recentdate = models.DateField(auto_now=False, auto_now_add=False)
    episodes = models.IntegerField()
    year = models.IntegerField(default = 0)
    category = models.CharField(max_length = 10, blank =  True)
    airing = models.BooleanField(default = False, blank = True)
    path = models.CharField(max_length = 80)
    max_episode = models.SmallIntegerField(null=True, blank = True)

    __original_episode = None

    def __init__(self, *args, **kwargs):
        super(Show, self).__init__(*args, **kwargs)
        self.__original_episode = self.episodes

    def save (self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        elif self.episodes != self.__original_episode:
            self.recentdate =timezone.now()
        super(Show, self).save(*args,**kwargs)

    def delete(self, using=None, keep_parents=False):
    # assuming that you use same storage for all files in this model:
        storage = self.image.storage

        if storage.exists(self.image.name):
            storage.delete(self.image.name)

        super().delete()

    def __str__(self):
        return f"Show <{self.title} - {self.id}>"

class Requests(models.Model): 
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length = 120)
    plot = models.CharField(max_length = 400)
    image = models.ImageField(storage = fs, upload_to = 'reqposters/', blank = True, null=True)
    reqdate = models.DateField(auto_now_add = True)
    requser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    webid = models.CharField(max_length = 60)
    isfilled = models.BooleanField(default=False)
    isrejected = models.BooleanField(default=False)
    def __str__(self):
        return f"Request <{self.title} - {self.id}>"

    def delete(self, using=None, keep_parents=False):
    # assuming that you use same storage for all files in this model:
        storage = self.image.storage

        if storage.exists(self.image.name):
            storage.delete(self.image.name)

        super().delete()

class Votes(models.Model):
    id = models.AutoField(primary_key=True)
    request = models.ForeignKey('Requests', on_delete=models.CASCADE)
    voteuser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True)
    

# Create your models here.
