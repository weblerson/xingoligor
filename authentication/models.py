from django.db import models
from django.contrib.auth.models import User

class TokenAtivacao(models.Model):
    token = models.CharField(max_length=64)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    usado = models.BooleanField(default=False)

    def __str__(self):
        return f"Token de ativação de {self.usuario.username}"

class TokenRecuperacao(models.Model):
    token = models.CharField(max_length=64)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    solicitado = models.BooleanField(default=False)

    def __str__(self):
        return f"Token de recuperação de {self.usuario.username}"