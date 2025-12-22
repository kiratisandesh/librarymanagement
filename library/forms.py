from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from . import models

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class StudentUserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        help_text='Must be a .ac.uk email address'
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email ends with .ac.uk
        if not email.endswith('.ac.uk'):
            raise ValidationError('Email must be from a .ac.uk domain (academic institution).')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered.')
        
        return email


class StudentExtraForm(forms.ModelForm):
    class Meta:
        model = models.StudentExtra
        fields = ['enrollment', 'branch']


class BookForm(forms.ModelForm):
    class Meta:
        model = models.Book
        fields = ['name', 'isbn', 'author', 'category', 'total_copies'] 


class IssuedBookForm(forms.Form):
    isbn2 = forms.ModelChoiceField(
        queryset=models.Book.objects.all(),
        empty_label="Name and isbn",
        to_field_name="isbn",
        label='Name and Isbn'
    )
    enrollment2 = forms.ModelChoiceField(
        queryset=models.StudentExtra.objects.all(),
        empty_label="Name and enrollment",
        to_field_name='enrollment',
        label='Name and enrollment'
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = models.Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} ⭐') for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Share your thoughts about this book...',
                'class': 'form-control'
            })
        }
        labels = {
            'rating': 'Your Rating',
            'review_text': 'Your Review (Optional)'
        }