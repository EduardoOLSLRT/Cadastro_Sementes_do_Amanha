# Cadastro Sementes do Amanhã — API Flask

API REST para **cadastro de atendidos**, **controle de frequência** e **transporte**.

- **Stack:** Flask · Flask‑SQLAlchemy · python‑dotenv · SQLite (DEV)
- **Modelagem:** `atendidos` (dimensão), `frequencias` (fato temporal 1:N), `transportes` (1:1)
- **Enums:** validados via `Enum` do SQLAlchemy (CHECK no SQLite)
- **Config:** `.env` (local, fora do Git) + `.env.example` (modelo no Git)

---

## 🚀 Começando

### 1) Pré-requisitos
- Python **3.14+**
- Pip atualizado
- (Opcional) CLI do **SQLite** para inspecionar tabelas

### 2) Clonar e entrar na pasta
```bash
git clone <URL-do-repo>
cd Cadastro_Sementes_do_Amanha