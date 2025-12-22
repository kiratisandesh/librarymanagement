"""librarymanagement URL Configuration"""
from django.contrib import admin
from django.conf.urls import include
from django.urls import path
from library import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/',include('django.contrib.auth.urls') ),
    path('', views.home_view),

    # UPDATED: Single unified login
    path('login', views.unified_login_view, name='login'),
    
    # Keep these for backward compatibility (redirect to unified login)
    path('adminclick', views.unified_login_view),
    path('studentclick', views.unified_login_view),
    path('adminlogin', views.unified_login_view),
    path('studentlogin', views.unified_login_view),

    path('studentsignup', views.studentsignup_view),
    path('returnbook/<int:id>/', views.returnbook, name='returnbook'),

    path('logout', LogoutView.as_view(template_name='library/index.html'), name='logout'),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),

    path('addbook', views.addbook_view),
    path('viewbook', views.viewbook_view, name='viewbook'),
    path('issuebook', views.issuebook_view),
    path('viewissuedbook', views.viewissuedbook_view),
    path('viewstudent', views.viewstudent_view),
    path('viewissuedbookbystudent', views.viewissuedbookbystudent,name='viewissuedbookbystudent'),

    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),

    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),
    path('book/<int:book_id>/review/', views.add_review_view, name='add_review'),
    path('editbook/<int:book_id>/', views.editbook_view, name='editbook'),
    path('deletebook/<int:book_id>/', views.deletebook_view, name='deletebook'),

    path('student/books/', views.student_browse_books_view, name='student_browse_books'),
    path('student/book/<int:book_id>/', views.student_book_detail_view, name='student_book_detail'),
    path('student/request/<int:book_id>/', views.student_request_book_view, name='student_request_book'),
        
    path('viewreviews', views.viewreviews_view, name='viewreviews'),
    path('deletereview/<int:review_id>/', views.deletereview_view, name='deletereview'),
]