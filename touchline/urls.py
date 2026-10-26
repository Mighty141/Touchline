from django.contrib import admin
from django.urls import path
from portal import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("matches/", views.matches, name="matches"),
    path("matches/<int:match_id>/", views.match_detail, name="match_detail"),
    path("api/matches/", views.matches_api, name="matches_api"),
]
