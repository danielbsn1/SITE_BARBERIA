# SITE_BARBERIA
---
# 📖 Documentação - Sistema de Agendamento Barbearia

## Visão Geral

Este sistema é uma aplicação web para agendamento de horários em uma barbearia, com painel administrativo (caixa) e controle de pagamentos.  
Foi desenvolvido em **Python** usando **Flask** e **SQLAlchemy**.

---

## Funcionalidades

- Listagem de serviços e preços
- Agendamento online de horários
- Pagamento de agendamento
- Login de administrador
- Painel do caixa com resumo de ganhos
- API para horários disponíveis

---

## Estrutura de Pastas

```
├── barbeariapp.py           # Código principal da aplicação Flask
├── barbearia.db             # Banco de dados SQLite (criado automaticamente)
└── templates/               # Templates HTML
    ├── index.html
    ├── agendar.html
    ├── pagamento.html
    ├── login.html
    ├── caixa.html
    └── agendamentos.html
```

---

## Como Executar

1. **Instale as dependências:**
   ```
   pip install flask flask_sqlalchemy
   ```

2. **Execute o programa:**
   ```
   python barbeariapp.py
   ```

3. **Acesse no navegador:**
   ```
   http://localhost:5000
   ```

---

## Usuário Administrador

- **Usuário:** `admin`
- **Senha:** `admin123`

---

## Rotas Principais

- `/`  
  Página inicial com lista de serviços.

- `/agendar`  
  Formulário para agendamento de horário.

- `/pagamento/<agendamento_id>`  
  Página de pagamento do agendamento.

- `/login`  
  Login do administrador.

- `/caixa`  
  Painel do caixa (apenas para admin logado).

- `/api/horarios_disponiveis?data=YYYY-MM-DD`  
  API que retorna horários livres para uma data.

---

## Observações

- O banco de dados é criado automaticamente na primeira execução.
- O admin e os serviços iniciais são cadastrados automaticamente.
- Os templates HTML devem estar na pasta templates.

---

## Tecnologias

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Jinja2 (templates)



