# Campus-Hub

Campus-Hub is a multi-tenant, university-focused platform designed to be a centralized hub for student life. It provides a secure and isolated environment for each university's students to engage in campus-specific commerce and events.

## Core Features

### User Identity & Authentication
- **Secure Registration:** A two-step registration process requiring email and OTP verification ensures all users are legitimate.
- **Domain Validation:** Users must register with a valid student email address, verified against their university's allowed domains.
- **Token-Based Login:** Secure authentication using DRF's built-in token system for verified users.
- **Student Profiles:** Users can create and manage their student profiles, linking them to a specific university.

### Multi-Tenant Market Hub
- **Data Isolation:** All market hub data (listings, events, organizations) is strictly scoped to the user's university, providing a secure, private environment for each institution.
- **Organizations:** Users can create and manage organizations, such as businesses or clubs.
- **Hustle Listings:** A marketplace for students to buy and sell goods and services within their campus.
- **Event Listings:** A platform for organizations to post and manage campus events.

## Technology Stack

*   **Backend:** Python, Django, Django REST Framework
*   **Database:** PostgreSQL (via `django-environ`)
*   **Authentication:** DRF Token Authentication

## API Endpoints

### Core Identity (`/api/v1/core/`)
- `POST /register/`: Register a new user.
- `POST /verify-email/`: Verify email with an OTP.
- `POST /login/`: Log in a verified user and receive an auth token.
- `POST /profile/`: Create a student profile.
- `GET, PATCH /profile/me/`: Retrieve or update the current user's student profile.
- `GET /universities/`: Get a list of all universities.

### Market Hub (`/api/v1/market/`)
- `GET, POST /organizations/`: List or create organizations for the user's university.
- `GET, PUT, PATCH, DELETE /organizations/<slug>/`: Manage a specific organization.
- `GET, POST /hustles/`: List or create hustle listings.
- `GET, PUT, PATCH, DELETE /hustles/<slug>/`: Manage a specific hustle listing.
- `GET, POST /events/`: List or create events.
- `GET, PUT, PATCH, DELETE /events/<slug>/`: Manage a specific event.

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites
- Python 3.10+
- PostgreSQL

### Installation
1.  Clone the repository:
    ```sh
    git clone https://github.com/your-username/Campus-Hub.git
    cd Campus-Hub
    ```
2.  Create and activate a virtual environment:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```
3.  Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```
4.  Set up your environment variables by creating a `.env` file in the project root. Use the `.env.example` as a template:
    ```env
    SECRET_KEY='your-secret-key'
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_URL='postgres://user:password@host:port/dbname'
    # ... other variables
    ```
5.  Run the database migrations:
    ```sh
    python manage.py migrate
    ```
6.  Start the development server:
    ```sh
    python manage.py runserver
    ```

## Running Tests
To run the automated test suite, use the following command:
```sh
python manage.py test
```

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**. Please refer to `CONTRIBUTING.md` (to be created) for guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for