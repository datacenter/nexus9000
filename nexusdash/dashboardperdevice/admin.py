from django.contrib import admin

from .models import OSInfo
from .models import InterfacesStats
from .models import CpuStats
from .models import DirStats
from .models import MemStats
from .models import ModulesStats

admin.site.register(OSInfo)
admin.site.register(InterfacesStats)
admin.site.register(CpuStats)
admin.site.register(DirStats)
admin.site.register(MemStats)
admin.site.register(ModulesStats)