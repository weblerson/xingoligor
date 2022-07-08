from django.contrib import admin
from .models import TokenAtivacao, TokenRecuperacao

# Register your models here.
admin.site.register(TokenAtivacao)
admin.site.register(TokenRecuperacao)