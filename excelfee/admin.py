from django.contrib import admin
import excelfee.models

admin.site.register(excelfee.models.ExcelFile)
admin.site.register(excelfee.models.ExcelPurpose)
# admin.site.register(excelfee.models.InputDataGeneric)
# admin.site.register(excelfee.models.Cell)
admin.site.site_url = "/swagger/"
