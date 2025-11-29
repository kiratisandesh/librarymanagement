from django.db import models
from django.contrib.auth.models import User
from datetime import datetime,timedelta



class StudentExtra(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    enrollment = models.CharField(max_length=40)
    branch = models.CharField(max_length=40)
    #used in issue book
    def __str__(self):
        return self.user.first_name+'['+str(self.enrollment)+']'
    @property
    def get_name(self):
        return self.user.first_name
    @property
    def getuserid(self):
        return self.user.id


class Book(models.Model):
    catchoice= [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biographie'),
        ('history', 'History'),
        ]
    name=models.CharField(max_length=30)
    isbn=models.PositiveIntegerField(unique=True)
    author=models.CharField(max_length=40)
    category=models.CharField(max_length=30,choices=catchoice,default='education')
    
    total_copies = models.PositiveIntegerField(default=1) 
    available_copies = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return str(self.name)+"["+str(self.isbn)+']'
    
    # ADD THIS METHOD:
    def save(self, *args, **kwargs):
        # If this is a new book (no pk yet), set available_copies to total_copies
        if not self.pk:
            self.available_copies = self.total_copies
        super(Book, self).save(*args, **kwargs)
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0

    @property
    def review_count(self):
        return self.reviews.count()


def get_expiry():
    return datetime.today() + timedelta(days=15)

class IssuedBook(models.Model):
    enrollment=models.CharField(max_length=30)
    isbn=models.CharField(max_length=30)
    issuedate=models.DateField(auto_now=True)
    expirydate=models.DateField(default=get_expiry)
    statuschoice= [
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
        ]
    status=models.CharField(max_length=20,choices=statuschoice,default="Issued")
    def __str__(self):
        return self.enrollment
    


class Review(models.Model):  # Correct
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('book', 'user')
    
    def __str__(self):
        return f"{self.user.username} - {self.book.name} ({self.rating}★)"
    
    