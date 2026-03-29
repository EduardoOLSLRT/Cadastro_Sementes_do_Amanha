# Cadastro Sementes do Amanhã — API Flask

API REST para **cadastro de alunos**, **controle de frequência** e **transporte** da ONG **Sementes do Amanhã**.

## Stack

- **Backend:** Flask
- **ORM:** Flask-SQLAlchemy
- **Banco (uso real):** PostgreSQL via **Supabase**
- **Banco (desenvolvimento inicial/testes locais):** SQLite
- **Configuração:** `python-dotenv`
- **Migração futura:** Flask-Migrate (ainda não obrigatório no fluxo atual)

---

## Funcionalidades já implementadas

- **Health check**
- **Cadastro de usuários**
- **Login**
- **Cadastro de alunos**
- **Listagem de alunos**
- **Transporte (1:1 por aluno)**
- **Lista de chamada por turma**
- **Marcação de frequência**
- **Relatório mensal de presença**

---

## Estrutura do projeto

```text
Cadastro_Sementes_do_Amanha/
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ database.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  ├─ users.py
│  │  ├─ students.py
│  │  ├─ attendance.py
│  │  └─ transport.py
│  ├─ routes/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ users.py
│  │  ├─ students.py
│  │  ├─ attendance.py
│  │  └─ transport.py
│  └─ services/
│     ├─ __init__.py
│     └─ turma.py
├─ .env                  # NÃO versionar
├─ .env.example          # versionar
├─ app.py
├─ requirements.txt
└─ README.md