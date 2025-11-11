# SITE_BARBERIA

Sistema web de agendamento para barbearia — backend em Flask + SQLAlchemy e frontend com templates Jinja2.

---

## 🔎 Visão geral

Aplicação para gerenciar serviços, agendamentos, pagamentos e um painel administrativo (caixa). Pensada para execução local com SQLite.

---

## ✅ Funcionalidades

- Listagem de serviços e preços
- Agendamento online (validação de horários)
- Painel do administrador (login)
- Caixa: registrar entradas e fechar (zera saldo)
- API REST para operações (agendamentos, serviços, caixa)

---

## Requisitos

- Python 3.10+ (testado em 3.11/3.13)
- pip

Recomenda-se criar um virtualenv:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Se não existir requirements.txt:
```powershell
pip install flask flask_sqlalchemy
```

---

## Estrutura do projeto

c:\Users\Usuário\Documents\SITE_BARBERIA
- Barbareia/Back-end/barbeariapp.py  — app Flask
- Barbareia/Back-end/barbearia.db    — banco (SQLite)
- Barbeaira/Front-end/templates/...  — templates Jinja2
- Barbeaira/Front-end/static/...     — CSS / JS / imagens

Exemplo de templates:
- templates/clientes/Home.html
- templates/clientes/agenda.html
- templates/admin/caixa.html

---

## Como rodar (desenvolvimento)

1. Ative o virtualenv
2. Na pasta Back-end:
```powershell
cd "c:\Users\Usuário\Documents\SITE_BARBERIA\Barbearia\Back-end"
python barbeariapp.py
```
3. Acesse no navegador:
```
http://127.0.0.1:5000
```

---

## Comandos úteis

- Remover banco atual:
```powershell
Remove-Item "c:\Users\Usuário\Documents\SITE_BARBERIA\Barbearia\Back-end\barbearia.db" -ErrorAction SilentlyContinue
```
- Testar endpoint via curl (PowerShell):
```powershell
curl http://127.0.0.1:5000/api/servicos
curl -X POST http://127.0.0.1:5000/api/caixa/adicionar -H "Content-Type: application/json" -d '{"valor":50}'
```

---

## Rotas principais (resumo)

Páginas:
- GET /            — home
- GET /agenda      — formulário de agendamento
- GET /meus-agendamentos — busca por telefone
- GET /caixa       — painel do caixa (admin)

API:
- GET  /api/servicos
- GET  /api/agendamentos
- GET  /api/agendamentos/cliente/<telefone>
- POST /api/agendamentos           — cria agendamento
- DELETE /api/agendamentos/<id>    — cancela agendamento
- GET  /api/caixa/saldo
- POST /api/caixa/adicionar
- POST /api/caixa/fechar

---

## Admin (teste)

- Usuário: `admin`  
- Senha: `admin123`  
(Se utilizar seed automático, ajuste conforme necessidade.)

---

## Banco de dados / seed

O app cria as tabelas automaticamente na primeira execução (db.create_all()) e inclui seed de serviços e caixa (se configurado). Se alterar modelos, remova o arquivo `barbearia.db` para recriar.

---

## Boas práticas e próximos passos

- Extrair CSS comum para `static/css/theme.css` e unificar variáveis CSS
- Adicionar testes unitários (pytest) para rotas API
- Implementar paginação e autenticação robusta (Flask-Login / Flask-JWT)
- Fazer backup/rotina de persistência para produção (usar PostgreSQL)

---

## Licença e contribuição

Projeto simples para uso local/educacional. Para PRs ou ajustes, adicione instruções no arquivo `CONTRIBUTING.md`.

---

Se desejar, eu:
- gero o arquivo `theme.css` e atualizo os CSS para um padrão visual único, ou
- crio um `requirements.txt` e script de setup (PowerShell) automático.

Qual opção prefere?



