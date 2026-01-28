"""
URL configuration for hostelmate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index , name='index'),
    path('login/',views.login_user),
    path('register/',views.register_user),
    path('logout/',views.logout_user , name="logout"),
    path('owner_dashboard/',views.owner_dashboard),
    path('hostel/delete/<int:hostel_id>/', views.delete_hostel, name='delete_hostel'),
    path('hostel/update/<int:hostel_id>/', views.update_beds, name='update_beds'),
    path('request/<int:hostel_id>/', views.send_request, name='send_request'),
    path('request/accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('requests/', views.user_requests, name='user_requests'),
    path('search/', views.search_hostels, name='search_hostels'),
     path('hostel/<int:hostel_id>/', views.hostel_detail, name='hostel_detail'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

