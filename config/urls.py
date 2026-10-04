from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("movies.urls")),

    path(
        "accounts/",
        include("accounts.urls")
    ),

    path(
        "booking/",
        include("bookings.urls")
    ),
    path(
    "booking/",
    include("bookings.urls")
),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )