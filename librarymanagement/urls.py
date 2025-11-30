"""librarymanagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from library import views
from django.contrib.auth.views import LoginView,LogoutView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls') ),
    path('', views.home_view),

    path('adminclick', views.adminclick_view),
    path('studentclick', views.studentclick_view),


    # path('adminsignup', views.adminsignup_view),
    path('studentsignup', views.studentsignup_view),
    path('adminlogin', LoginView.as_view(template_name='library/adminlogin.html')),
    path('studentlogin', LoginView.as_view(template_name='library/studentlogin.html')),
    path('returnbook/<int:id>/', views.returnbook, name='returnbook'),


    path('logout', LogoutView.as_view(template_name='library/index.html')),
    path('afterlogin', views.afterlogin_view),

    path('addbook', views.addbook_view),
    path('viewbook', views.viewbook_view, name='viewbook'),
    path('issuebook', views.issuebook_view),
    path('viewissuedbook', views.viewissuedbook_view),
    path('viewstudent', views.viewstudent_view),
    path('viewissuedbookbystudent', views.viewissuedbookbystudent,name='viewissuedbookbystudent'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

    # Add to urlpatterns in urls.py
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('book/<int:book_id>/review/', views.add_review_view, name='add_review'),
    path('editbook/<int:book_id>/', views.editbook_view, name='editbook'),
    path('deletebook/<int:book_id>/', views.deletebook_view, name='deletebook'),

    path('student/books/', views.student_browse_books_view, name='student_browse_books'),
    path('student/book/<int:book_id>/', views.student_book_detail_view, name='student_book_detail'),
    path('student/request/<int:book_id>/', views.student_request_book_view, name='student_request_book'),
    path('book/<int:book_id>/review/', views.add_review_view, name='add_review'),
        
    path('viewreviews', views.viewreviews_view, name='viewreviews'),
    path('deletereview/<int:review_id>/', views.deletereview_view, name='deletereview'),
]
