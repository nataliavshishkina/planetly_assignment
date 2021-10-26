from django.conf.urls import include
from api import views
from django.urls import path
from rest_framework import routers


router = routers.DefaultRouter()
router.register('temperature_entries', views.TemperatureEntryViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('top_cities/<int:n>/from/<slug:date_from>/to/<slug:date_to>/', views.top_cities)
]
