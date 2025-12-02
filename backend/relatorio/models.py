from django.db import models

class Cliente(models.Model):
    nome = models.CharField(verbose_name='Cliente', max_length=200, unique=True)
    
    def __str__(self):
        return self.nome


class Relatorio(models.Model):
    hospital = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name='Hospital')
    observacao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Relatório - {self.hospital}"


class Imagem(models.Model):

    relatorio = models.ForeignKey(Relatorio, on_delete=models.CASCADE, related_name="imagens", null=True)
    imagem = models.ImageField(upload_to='relatorios/', blank=True, null=True)
    
    def __str__(self):
        return f"Imagem do relatório {self.relatorio_id}" #type: ignore
