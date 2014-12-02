from django.contrib import admin
from costtool import models as m
from costtool.models import Prices
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportMixin
 
class PriceResource(resources.ModelResource):
    class Meta:
        model = Prices

class PriceAdmin(ImportMixin):
    resource_class = PriceResource
    pass
