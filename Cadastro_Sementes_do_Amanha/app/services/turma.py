# app/services/turma.py
# Função de domínio que converte idade em faixa/turma.

from datetime import date

def calcular_turma(data_nascimento):
    """
    Retorna a turma pela idade (anos inteiros):
      - 05–09  -> "Turma 05–09"
      - 10–12  -> "Turma 10–12"
      - 13–16  -> "Turma 13–16"
      - fora   -> "Fora da faixa"
    """
    idade = (date.today() - data_nascimento).days // 365

    if 5 <= idade <= 9:
        return "Turma 05–09"
    if 10 <= idade <= 12:
        return "Turma 10–12"
    if 13 <= idade <= 16:
        return "Turma 13–16"
    return "Fora da faixa"