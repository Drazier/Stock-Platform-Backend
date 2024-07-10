from django.contrib import admin

# Register your models here.

from .models import User, Strategy, TickerSymbol

admin.site.register(User)
admin.site.register(Strategy)

@admin.register(TickerSymbol)
class TickerSymbolAdmin(admin.ModelAdmin):
    list_display=("ticker","symbol_name","uuid")
    search_fields=("ticker","symbol_name")
    
    
