from django.contrib import admin
from . models import User,entity_list,product,serials,batch,report,startenddates
admin.site.register(User)
admin.site.register(entity_list)
admin.site.register(product)
admin.site.register(serials)
admin.site.register(batch)
admin.site.register(report)
admin.site.register(startenddates)
# Register your models here.
