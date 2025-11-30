from django.db.models import Q
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from . import forms,models
from django.contrib.auth.models import Group
from django.contrib import auth
from django.contrib.auth.decorators import login_required,user_passes_test
from datetime import date
from django.core.mail import send_mail
from librarymanagement.settings import EMAIL_HOST_USER
from django.db import IntegrityError, transaction
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Count
from django.shortcuts import redirect, render, get_object_or_404  # Add get_object_or_404 here
from django.contrib import messages


# --- NEW LOGIC FOR HOMEPAGE (Book Exploring Feature) ---
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    # Fetch books with available copies
    books = models.Book.objects.filter(available_copies__gt=0)
    
    # Apply search filter if query exists
    if search_query:
        books = books.filter(
            Q(name__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    books = books.order_by('name')
    
    context = {
        'books': books,
        'search_query': search_query
    }
    
    return render(request, 'library/index.html', context)

def book_detail_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    reviews = book.reviews.all().order_by('-created_at')
    
    user_review = None
    if request.user.is_authenticated:
        user_review = book.reviews.filter(user=request.user).first()
    
    context = {
        'book': book,
        'reviews': reviews,
        'user_review': user_review,
        'avg_rating': book.average_rating,
        'review_count': book.review_count
    }
    return render(request, 'library/book_detail.html', context)


@login_required(login_url='studentlogin')
def add_review_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    existing_review = models.Review.objects.filter(book=book, user=request.user).first()
    
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('book_detail', book_id=book_id)
    else:
        form = forms.ReviewForm(instance=existing_review)
    
    return render(request, 'library/add_review.html', {'form': form, 'book': book})


# Student view to browse all available books
@login_required(login_url='studentlogin')
def student_browse_books_view(request):
    books = models.Book.objects.filter(available_copies__gt=0).order_by('name')
    return render(request, 'library/student_browse_books.html', {'books': books})


# Student requests a book directly
@login_required(login_url='studentlogin')
def student_request_book_view(request, book_id):
    if not is_student(request.user):
        messages.error(request, 'Only students can request books.')
        return redirect('afterlogin')
    
    book = get_object_or_404(models.Book, id=book_id)
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
    
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('studentlogin')
    
    # Check if book is available
    if book.available_copies <= 0:
        messages.error(request, 'Sorry, this book is currently unavailable.')
        return redirect('student_browse_books')
    
    # Check if student already has this book
    existing_issue = models.IssuedBook.objects.filter(
        enrollment=student.enrollment,
        isbn=book.isbn,
        status='Issued'
    ).first()
    
    if existing_issue:
        messages.warning(request, 'You have already borrowed this book.')
        return redirect('student_browse_books')
    
    try:
        with transaction.atomic():
            # Decrease available copies
            book.available_copies -= 1
            book.save()
            
            # Create issued book record
            issued_book = models.IssuedBook()
            issued_book.enrollment = student.enrollment
            issued_book.isbn = str(book.isbn)
            issued_book.save()
            
            messages.success(request, f'Successfully borrowed "{book.name}"!')
            return redirect('viewissuedbookbystudent')
            
    except Exception as e:
        messages.error(request, f'Error borrowing book: {str(e)}')
        return redirect('student_browse_books')


# Book detail view for students with reviews
@login_required(login_url='studentlogin')
def student_book_detail_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    reviews = book.reviews.all().order_by('-created_at')
    
    user_review = None
    can_review = False
    
    if is_student(request.user):
        student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
        if student:
            # Check if student has borrowed this book
            has_borrowed = models.IssuedBook.objects.filter(
                enrollment=student.enrollment,
                isbn=book.isbn
            ).exists()
            can_review = has_borrowed
            user_review = book.reviews.filter(user=request.user).first()
    
    context = {
        'book': book,
        'reviews': reviews,
        'user_review': user_review,
        'can_review': can_review,
        'avg_rating': book.average_rating,
        'review_count': book.review_count
    }
    return render(request, 'library/student_book_detail.html', context)


# Add or edit review
@login_required(login_url='studentlogin')
def add_review_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    
    if not is_student(request.user):
        messages.error(request, 'Only students can review books.')
        return redirect('afterlogin')
    
    student = models.StudentExtra.objects.filter(user_id=request.user.id).first()
    if not student:
        messages.error(request, 'Student profile not found.')
        return redirect('studentlogin')
    
    # Check if student has borrowed this book
    has_borrowed = models.IssuedBook.objects.filter(
        enrollment=student.enrollment,
        isbn=book.isbn
    ).exists()
    
    if not has_borrowed:
        messages.warning(request, 'You can only review books you have borrowed.')
        return redirect('student_book_detail', book_id=book_id)
    
    existing_review = models.Review.objects.filter(book=book, user=request.user).first()
    
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully!')
            return redirect('student_book_detail', book_id=book_id)
    else:
        form = forms.ReviewForm(instance=existing_review)
    
    return render(request, 'library/add_review.html', {'form': form, 'book': book})

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/studentclick.html')

def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'library/adminclick.html')

def studentsignup_view(request):
    form1=forms.StudentUserForm()
    form2=forms.StudentExtraForm()
    mydict={'form1':form1,'form2':form2}
    if request.method=='POST':
        form1=forms.StudentUserForm(request.POST)
        form2=forms.StudentExtraForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user=form1.save()
            user.set_password(user.password)
            user.save()
            f2=form2.save(commit=False)
            f2.user=user
            f2.save() 

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')
    return render(request,'library/studentsignup.html',context=mydict)


def is_admin(user):
    return user.is_active and (user.is_superuser or user.is_staff)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

# --- CRITICAL ACCESS CONTROL FIXES START HERE (Explicit Error Handling) ---
def admin_login_check(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        
        if user is not None:
            if is_admin(user):
                auth.login(request, user)
                return redirect('afterlogin')
            else:
                error_msg = "This account is registered as a Student. Please use the Student Login portal."
                return render(request, 'library/adminlogin.html', {'error_message': error_msg})
        
        return render(request, 'library/adminlogin.html', {'error_message': 'Invalid credentials.'})
    
    return LoginView.as_view(template_name='library/adminlogin.html')(request)


def student_login_check(request):
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
        if user is not None:
            if is_student(user):
                auth.login(request, user)
                return redirect('afterlogin')
            else:
                error_msg = "This is the Student Login portal. Please use the Administrator Login."
                return render(request, 'library/studentlogin.html', {'error_message': error_msg})
        
        return render(request, 'library/studentlogin.html', {'error_message': 'Invalid credentials.'})
    
    return LoginView.as_view(template_name='library/studentlogin.html')(request)
# --- CRITICAL ACCESS CONTROL FIXES END HERE ---


def afterlogin_view(request):
    if is_admin(request.user):
        return render(request,'library/adminafterlogin.html')
    
    elif(is_student(request.user)):
        return render(request,'library/studentafterlogin.html')

# --- NEW FEATURE: View All Available Books (Shared Access) ---
@login_required(login_url='adminlogin')
def all_available_books_view(request):
    # Filters to show only books with at least one available copy
    books = models.Book.objects.filter(available_copies__gt=0).order_by('name')
    
    # Dynamic template selection based on user role (Admin vs Student)
    if is_admin(request.user):
        template_name = 'library/viewbook.html' 
    elif is_student(request.user):
        template_name = 'library/student_view_available_books.html' 
    else:
        return redirect('home_view')

    return render(request, template_name, {'books':books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def editbook_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    form = forms.BookForm(instance=book)
    
    if request.method == 'POST':
        form = forms.BookForm(request.POST, instance=book)
        if form.is_valid():
            try:
                form.save()
                return redirect('viewbook')
            except IntegrityError:
                return render(request, 'library/editbook.html', {
                    'form': form, 
                    'book': book,
                    'error': 'Book with this ISBN already exists.'
                })
    
    return render(request, 'library/editbook.html', {'form': form, 'book': book})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def deletebook_view(request, book_id):
    book = get_object_or_404(models.Book, id=book_id)
    
    if request.method == 'POST':
        book.delete()
        return redirect('viewbook')
    
    return render(request, 'library/deletebook.html', {'book': book})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    form=forms.BookForm()
    if request.method=='POST':
        form=forms.BookForm(request.POST)
        if form.is_valid():
            try:
                # Save book and let the signal handler set available_copies
                form.save()
                return render(request,'library/bookadded.html')
            except IntegrityError:
                 return render(request,'library/addbook.html',{'form':form, 'error': 'Book with this ISBN already exists.'})
            except Exception as e:
                return render(request,'library/addbook.html',{'form':form, 'error': f'An unexpected error occurred: {e}'})

    return render(request,'library/addbook.html',{'form':form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    # Redirect legacy 'viewbook' URL to the new, integrated view
    return all_available_books_view(request)


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form=forms.IssuedBookForm()
    if request.method=='POST':
        form=forms.IssuedBookForm(request.POST)
        if form.is_valid():
            isbn = request.POST.get('isbn2')
            
            try:
                book = models.Book.objects.get(isbn=isbn)
                
                # --- INVENTORY CONTROL FIX: Check and decrement within a transaction ---
                if book.available_copies > 0:
                    with transaction.atomic(): 
                        book.available_copies -= 1
                        book.save()
                        
                        obj=models.IssuedBook()
                        obj.enrollment=request.POST.get('enrollment2')
                        obj.isbn=isbn
                        obj.save()
                        return render(request,'library/bookissued.html')
                else:
                    return render(request, 'library/issuebook.html', {'form':form, 'error': 'No available copies of this book.'})
            except models.Book.DoesNotExist:
                return render(request, 'library/issuebook.html', {'form':form, 'error': 'Book not found.'})
            except IntegrityError:
                 return render(request, 'library/issuebook.html', {'form':form, 'error': 'Database error during issue.'})

    return render(request,'library/issuebook.html',{'form':form})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks=models.IssuedBook.objects.all()
    li=[]
    for ib in issuedbooks:
        issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
        expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
        #fine calculation
        days=(date.today()-ib.issuedate)
        d=days.days
        fine=0
        if d>15:
            day=d-15
            fine=day*10


        books=list(models.Book.objects.filter(isbn=ib.isbn))
        students=list(models.StudentExtra.objects.filter(enrollment=ib.enrollment))
        i=0
        for l in books:
            t=(students[i].get_name,students[i].enrollment,books[i].name,books[i].author,issdate,expdate,fine,ib.status)
            i=i+1
            li.append(t)

    return render(request,'library/viewissuedbook.html',{'li':li})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students=models.StudentExtra.objects.all()
    return render(request,'library/viewstudent.html',{'students':students})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewreviews_view(request):
    reviews = models.Review.objects.all().order_by('-created_at')
    return render(request, 'library/viewreviews.html', {'reviews': reviews})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def deletereview_view(request, review_id):
    review = get_object_or_404(models.Review, id=review_id)
    
    if request.method == 'POST':
        book_name = review.book.name
        review.delete()
        messages.success(request, f'Review for "{book_name}" deleted successfully!')
        return redirect('viewreviews')
    
    return render(request, 'library/deletereview.html', {'review': review})


@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    student=models.StudentExtra.objects.filter(user_id=request.user.id)
    if not student.exists():
        return redirect('studentlogin')
        
    issuedbook=models.IssuedBook.objects.filter(enrollment=student[0].enrollment)

    li1=[]
    li2=[]
    for ib in issuedbook:
        try:
            book = models.Book.objects.get(isbn=ib.isbn)
            t=(request.user,student[0].enrollment,student[0].branch,book.name,book.author)
            li1.append(t)
            issdate=str(ib.issuedate.day)+'-'+str(ib.issuedate.month)+'-'+str(ib.issuedate.year)
            expdate=str(ib.expirydate.day)+'-'+str(ib.expirydate.month)+'-'+str(ib.expirydate.year)
            #fine calculation
            days=(date.today()-ib.issuedate)
            d=days.days
            fine=0
            if d>15:
                day=d-15
                fine=day*10
            t=(issdate,expdate,fine,ib.status,ib.id)
            li2.append(t)
        except models.Book.DoesNotExist:
            print(f"Warning: Book with ISBN {ib.isbn} not found for issued record {ib.id}")
            # Skip this record if book data is missing
            continue 

    return render(request,'library/viewissuedbookbystudent.html',{'li1':li1,'li2':li2})

@login_required(login_url='studentlogin')
def returnbook(request, id):
    issued_book = models.IssuedBook.objects.get(pk=id)
    
    # --- INVENTORY CONTROL FIX: Increment available_copies on return ---
    book = models.Book.objects.get(isbn=issued_book.isbn)
    with transaction.atomic():
        book.available_copies += 1
        book.save()
        
        issued_book.status = "Returned"
        issued_book.save()
        
    return redirect('viewissuedbookbystudent')
    
def aboutus_view(request):
    return render(request,'library/aboutus.html')

def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name)+' || '+str(email),message, EMAIL_HOST_USER, ['wapka1503@gmail.com'], fail_silently = False)
            return render(request, 'library/contactussuccess.html')
    return render(request, 'library/contactus.html', {'form':sub})



