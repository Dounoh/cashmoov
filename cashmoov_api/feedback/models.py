from django.db import models
from cashmoov_api.common.models import Base


class Feedback(Base):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, null=True)
    email = models.EmailField()
    message = models.TextField()
    
    def __str__(self):
        return self.first_name + " " + self.last_name