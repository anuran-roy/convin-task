from django.urls import path
from . import views as calendar_views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path("init/", calendar_views.GoogleCalendarInitView.as_view()),
    path("redirect/", calendar_views.GoogleCalendarRedirectView.as_view()),
]
