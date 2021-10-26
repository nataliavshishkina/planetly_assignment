from django.db import models


class TemperatureEntry(models.Model):
    date = models.DateField()
    average_temperature = models.FloatField(null=True)
    average_temperature_uncertainity = models.FloatField(null=True)
    city = models.CharField(max_length=200)
    country = models.CharField(max_length=200)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    class Meta:
        db_table = "Global_Land_Temperatures_By_City"

        # We include country in the unique constraint since there are cities in different countries.
        # For example, thre are Alexandria in Egypt and US.
        # But it doesn't work since there are two Haicheng in China.
        # A proper solution would require creating a separate Cities table 
        # and using foreign index in Global_Land_Temperatures_By_City.
        # unique_together = ('date', 'city', 'country')
