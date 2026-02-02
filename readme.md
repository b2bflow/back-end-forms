# Projeto Lead Capture Backend – API Flask com MongoDB e JWT

Este projeto é uma **API backend para captação de leads**, construída com **Flask**, seguindo uma **arquitetura em camadas (Clean / Hexagonal-inspired)**, com foco em **escalabilidade, separação de responsabilidades e segurança**.

A aplicação permite:

* Cadastro de leads
* Bloqueio de múltiplos cadastros por sessão
* Validação de origem do frontend
* Geração de token de sessão com expiração baseada na data de agendamento

---

## 🚀 Tecnologias Utilizadas

* **Python 3.12**
* **Flask** – Framework web
* **MongoDB** – Banco de dados NoSQL
* **MongoEngine** – ODM
* **PyJWT** – Tokens JWT
* **python-dotenv** – Variáveis de ambiente
* **Docker / Docker Compose** – Infraestrutura local

---

## 🚀 Requisitos

* Python 3.10+
* Pip
* Docker e Docker Compose
* Git (opcional)

---

## 📦 Criando Ambiente Virtual

### 🔹 Linux / macOS / WSL

```bash
python3 -m venv venv
source venv/bin/activate
```

### 🔹 Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Para desativar:

```bash
deactivate
```

---

## 📚 Instalando Dependências

Com a venv ativa:

```bash
pip install -r requirements.txt
```

---

## 🐳 Subindo o MongoDB com Docker

```bash
docker-compose up -d
```

Serviços disponíveis:

* MongoDB → `mongodb://localhost:27017`
* Mongo Express → `http://localhost:8081`

---

## ⚙️ Variáveis de Ambiente (.env)

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_ENV=development
FLASK_DEBUG=1

MONGO_URI=mongodb://localhost:27017/lead_capture_db

JWT_SECRET_KEY=super-secret-jwt-key
CLIENT_TOKEN=frontend-secret-token
```

---

## 📁 Estrutura do Projeto

```text
lead-capture-backend/
├── app/
│   ├── __init__.py
│   ├── controllers/
│   │   └── lead_controller.py
│   ├── routes/
│   │   └── lead_routes.py
│   ├── services/
│   │   └── lead_service.py
│   ├── repository/
│   │   └── lead_repository.py
│   ├── interfaces/
│   │   ├── services/
│   │   └── repositories/
│   ├── models/
│   │   └── tables/
│   │       └── lead_model.py
│   ├── dto/
│   │   └── lead_response_dto.py
│   ├── security/
│   │   ├── session_token.py
│   │   ├── lead_session_guard.py
│   │   └── client_token_guard.py
│   └── handlers/
│       └── error_handler.py
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md
```

---

## 🔐 Segurança Implementada

### 1️⃣ Token de Sessão do Lead (JWT)

* Gerado após o cadastro
* Expira na data do agendamento (`scheduling_day`)
* Impede que o lead se cadastre mais de uma vez

Header esperado:

```http
X-Session-Token: <jwt>
```

---

### 2️⃣ Token de Origem do Frontend

Garante que apenas frontends confiáveis chamem a API.

Header esperado:

```http
X-Client-Token: frontend-secret-token
```

---

## 🧩 Decorators de Segurança

* `@validate_client_token`
* `@validate_lead_session`

Aplicados diretamente no controller, mantendo a regra fora das rotas.

---

## 📤 Exemplo de Payload de Cadastro

```json
{
  "name": "Testando",
  "email": "teste.1@example.com",
  "phone": "+5511998765432",
  "business_name": "Lead Capture Tecnologia",
  "business_tracking": "Google Ads",
  "job_position": "CTO",
  "invoicing": "50k-100k",
  "collaborators": "11-50",
  "scheduling_day": "2026-01-25T14:00:00"
}
```

---

## 📥 Resposta para o Frontend

Contrato mínimo:

```json
{
  "lead": {
    "name": "Testando",
    "business_name": "Lead Capture Tecnologia",
    "scheduling_day": "2026-01-25T14:00:00"
  },
  "token": "<jwt>"
}
```

---

## ▶️ Executando a Aplicação

```bash
flask run --debug
```

API disponível em:

```
http://127.0.0.1:5000
```
---

## 📌 Referências Oficiais

* Flask → [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
* MongoEngine → [https://mongoengine-odm.readthedocs.io/](https://mongoengine-odm.readthedocs.io/)
* PyJWT → [https://pyjwt.readthedocs.io/](https://pyjwt.readthedocs.io/)
* Docker → [https://docs.docker.com/](https://docs.docker.com/)
* python-dotenv → [https://saurabh-kumar.com/python-dotenv/](https://saurabh-kumar.com/python-dotenv/)

---

Desenvolvido para fins de **captação de leads com segurança e escalabilidade**.
