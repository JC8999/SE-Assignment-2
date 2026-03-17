"""
URL configuration for tabletop_club project.

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
from django.contrib.auth.views import LogoutView
from django.urls import path
from tabletop_club_app import views

urlpatterns = [
    # authentication
    path('admin/', admin.site.urls),
    path('', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # primary pages
    path('admin_home/', views.home_admin, name='home_admin'),
    path('member_home/', views.home_member, name='home_member'),
    path('game_catalogue/', views.game_catalogue, name='game_catalogue'),
    path('members/', views.members, name='members'),
    path('rentals/', views.rentals, name='rentals'),
    path('my_rentals/', views.my_rentals, name='my_rentals'),

    # CRUD Forms
    path("create_member/", views.create_member, name="create_member"),
    path("create_board_game/", views.create_board_game, name="create_board_game"),
    path("edit_member/<int:pk>/", views.edit_member, name="edit_member"),
    path("edit_board_game/<int:pk>/", views.edit_board_game, name="edit_board_game"),
    path("delete_member/<int:pk>/", views.delete_member, name="delete_member"),
    path("delete_board_game/<int:pk>/", views.delete_board_game, name="delete_board_game"),
    path("rent_game/<int:pk>/", views.rent_game, name="rent_game"),
]
