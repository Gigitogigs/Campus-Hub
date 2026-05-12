# 🎓 Campus-Hub

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-Backend-092E20.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Campus-Hub** is a multi-tenant, university-focused platform designed to serve as a centralized hub for student life. It provides a secure, isolated environment for students at specific universities to engage in campus-specific commerce, organization management, and events.

---

## 🌟 Core Features

### 🔐 User Identity & Authentication
- **Secure Registration:** A robust two-step registration process requiring email and OTP verification ensures a trusted user base.
- **Domain Validation:** Registration is restricted to users with valid student email addresses, automatically verified against their university's allowed domains.
- **Token-Based Login:** Built on Django REST Framework's (DRF) secure token authentication system.
- **Student Profiles:** Customizable profiles linked directly to a student's verified university.

### 🏢 Multi-Tenant Market Hub
- **Strict Data Isolation:** All hub data (listings, events, and organizations) is strictly scoped to the user's university, guaranteeing privacy and a localized experience.
- **Organizations:** Students can create and manage campus groups, clubs, or small businesses.
- **Hustle Listings (Marketplace):** A dedicated marketplace for students to buy, sell, or trade goods and services within their campus.
- **Event Management:** A centralized platform for organizations to post, promote, and manage campus events.

---

## 🛠️ Technology Stack

- **Backend Framework:** Python, Django, Django REST Framework (DRF)
- **Database:** PostgreSQL (configured via `django-environ`)
- **Authentication:** DRF Token Authentication & Custom OTP Verification

---

## 📡 API Endpoints Overview

The platform exposes a RESTful API organized into specific domains:

### Core Identity (`/api/v1/core/`)
- `POST /register/` - Register a new user account.
- `POST /verify-email/` - Verify email using the OTP sent during registration.
- `POST /login/` - Authenticate and receive a token.
- `POST /profile/` - Create a student profile.
- `GET, PATCH /profile/me/` - Retrieve or update the authenticated user's profile.
- `GET /universities/` - Retrieve the list of supported universities.

### Market Hub (`/api/v1/market/`)
- `GET, POST /organizations/` - List organizations or create a new one for your university.
- `GET, PUT, PATCH, DELETE /organizations/<slug>/` - Manage a specific organization.
- `GET, POST /hustles/` - Browse or create campus hustle (marketplace) listings.
- `GET, PUT, PATCH, DELETE /hustles/<slug>/` - Manage a specific hustle.
- `GET, POST /events/` - Discover or create campus events.
- `GET, PUT, PATCH, DELETE /events/<slug>/` - Manage a specific event.

---

## 🚀 Getting Started

Follow these instructions to get a local copy of the project up and running for development and testing.

### Prerequisites
- Python 3.10 or higher
- PostgreSQL

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gigitogigs/Campus-Hub.git
   cd Campus-Hub
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the project root directory. Use `.env.example` as a template (if available) or add the following:
   ```env
   SECRET_KEY='your-development-secret-key'
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL='postgres://user:password@host:port/dbname'
   # Add other required variables (e.g., Email backend config for OTPs)
   ```

5. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Running Tests

To ensure everything is working correctly, run the automated test suite:
```bash
python manage.py test
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. 
*(Please refer to `CONTRIBUTING.md` when created for specific guidelines).*

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.