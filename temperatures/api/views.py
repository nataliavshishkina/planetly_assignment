from django.db.models import Max, Subquery

from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view

from api.models import TemperatureEntry


class TemperatureEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureEntry
        fields = '__all__'
        #extra_kwargs = {'country': {'required': False}}


class TemperatureEntryViewSet(ModelViewSet):
    """
    Implements standard API actions for temperatures entries.
    Also implements /update_by_date_and_city action for updating entry by city and date.

    Examples:
    * POST /api/temperature_entries/ - creates new entry
    * PUT /api/temperature_entries/update_by_date_and_city/ - updates the average temperatue and the uncetainty by city and date

    More examples (autogenerated by REST framework):
    * GET /api/temperature_entries/ - lists all entries
    * DELETE /api/temperature_entries/{id} - removes entry by id
    * PUT /api/temperature_entries/{id} - updates entry by id
    """
    queryset = TemperatureEntry.objects.all()
    serializer_class = TemperatureEntrySerializer

    @action(detail=False, methods=['PUT', 'PATCH'])
    def update_by_date_and_city(self, request):
        """
        Updates entry temperatures by date and city (and other fields).
        """
        serializer = TemperatureEntrySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        updating_fields = ['average_temperature',
                           'average_temperature_uncertainity']
        updating_data = {k: v for k, v in data.items() if k in updating_fields}
        filter_data = {k: v for k,
                       v in data.items() if k not in updating_fields}

        # Perform a basic (non-atomic) check that there is only one matching object
        updating_objects = TemperatureEntry.objects.all().filter(**filter_data)
        if len(updating_objects) == 0:
            return Response("Entry not found", status.HTTP_404_NOT_FOUND)
        if len(updating_objects) > 1:
            return Response("More than 1 matching entries found, specify additional fields: country or coordinates",
                            status.HTTP_400_BAD_REQUEST)

        # Update
        for k, v in updating_data.items():
            setattr(updating_objects[0], k, v)
        updating_objects[0].save()

        return Response(TemperatureEntrySerializer(updating_objects[0]).data)


@api_view(['GET'])
def top_cities(request, n, date_from, date_to):
    """
    Returns top N cities with highest average temperature in specified date range.

    Example:
    * GET /api/top_cities/10/from/2010-01-01/to/2010-12-01/ - top 10 cities in 2010
    """
    # Define ids of the cities
    qs_cities = TemperatureEntry.objects\
        .filter(date__gte=date_from, date__lte=date_to, average_temperature__isnull=False)\
        .values('id')\
        .order_by('city', '-average_temperature')\
        .distinct('city')

    # Order them (alternatively this can be also done on the client using pandas)
    qs_final = TemperatureEntry.objects.\
        filter(id__in=qs_cities).\
        values().\
        order_by('-average_temperature', 'city')[:n]
    # The case when there can be top 2 cities with the same avg temperature is not handled yet,
    # but to ensure the request will alwazs returen the same result order by city is applied as well
    res = list(qs_final)

    return Response(res)
