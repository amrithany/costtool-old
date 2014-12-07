from django.contrib import admin
from costtool import models as m
from costtool.models import UserProfile, Prices
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportMixin

class PriceResource(resources.ModelResource):
    class Meta:
        model = Prices

class PriceAdmin(ImportExportModelAdmin):
    resource_class = PriceResource
    pass
 
admin.site.register(m.Projects)
admin.site.register(m.Programs)
admin.site.register(m.Effectiveness)
admin.site.register(UserProfile)
admin.site.register(Prices)

