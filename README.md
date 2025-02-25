# Coderr API

## Overview

The Coderr API is a RESTful web service built with Django and Django REST Framework (DRF). It serves as the backend for the Coderr web application, providing endpoints for managing offers, orders, reviews, and user authentication.

## Features

-   **User Authentication:** Register new users, login, and manage user profiles.
-   **Offers Management:** Create, retrieve, update, and delete offers along with detailed offer information.
-   **Orders Management:** Place orders based on offer details, track order status, and retrieve order statistics.
-   **Reviews:** Submit and manage reviews for business users (with the restriction that a customer may only submit one review per business user).
-   **API Schema & Documentation:** Automatically generated OpenAPI 3.0 schema with interactive documentation via Swagger UI and Redoc.
-   **Filtering, Ordering, and Pagination:** Supports filtering offers by creator, price, and delivery time, as well as ordering and pagination.

## Technologies Used

-   Python 3.12 (recommended)
-   Django
-   Django REST Framework (DRF)
-   drf-spectacular (for API schema and documentation)
-   Django Filters

## Installation

1. **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd Coderr_backend_v1.0.0
    ```
    
2. **Create a Virtual Environment:**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Apply Migrations:**
    ```bash
    python manage.py migrate
    ```
5. **(Optional) Create a Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

## Running the Server

To start the development server, run:

```bash
python manage.py runserver
```

Access the API at `http://127.0.0.1:8000/api/` and view the API documentation via:

-   **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
-   **Redoc:** `http://127.0.0.1:8000/api/schema/redoc/`

## Running Tests

Run the test suite with:

```bash
python manage.py test
```

## API Endpoints Overview

Based on the provided OpenAPI schema, the key endpoints are:

### Base Information

-   **GET /api/base-info/**
    -   **Description:** Retrieve general platform statistics.
    -   **Response:** JSON containing:
        -   `review_count`: Total number of reviews.
        -   `average_rating`: Average review score (rounded to one decimal).
        -   `business_profile_count`: Number of business profiles.
        -   `offer_count`: Total number of offers.

### Order Counts

-   **GET /api/order-count/{business_user_id}/**
    -   **Description:** Retrieve the count of in-progress orders for a business user.
-   **GET /api/completed-order-count/{business_user_id}/**
    -   **Description:** Retrieve the count of completed orders for a business user.

### Offers

-   **GET /api/offers/**
    -   **Description:** List offers with support for filtering (by creator, price, delivery time), ordering, pagination, and search.
-   **POST /api/offers/**
    -   **Description:** Create a new offer.
-   **GET /api/offers/{id}/**
    -   **Description:** Retrieve a specific offer.
-   **PUT/PATCH/DELETE /api/offers/{id}/**
    -   **Description:** Update or delete an offer.

### Offer Details

-   **GET /api/offerdetails/{id}/**
    -   **Description:** Retrieve detailed information about an offer detail.

### Orders

-   **GET /api/orders/**
    -   **Description:** List orders.
-   **POST /api/orders/**
    -   **Description:** Create a new order based on an offer detail.
-   **GET /api/orders/{id}/**
    -   **Description:** Retrieve a specific order.
-   **PUT/PATCH/DELETE /api/orders/{id}/**
    -   **Description:** Update or delete an order.

### Reviews

-   **GET /api/reviews/**
    -   **Description:** List reviews.
-   **POST /api/reviews/**
    -   **Description:** Create a new review.
-   **GET/PATCH/DELETE /api/reviews/{id}/**
    -   **Description:** Retrieve, update, or delete a review.

### User Profiles

-   **GET /api/profile/{id}/**
    -   **Description:** Retrieve a user’s profile.
-   **PUT/PATCH/DELETE /api/profile/{id}/**
    -   **Description:** Update or delete a user’s profile.
-   **GET /api/profiles/business/**
    -   **Description:** List all business profiles.
-   **GET /api/profiles/customer/**
    -   **Description:** List all customer profiles.

### Authentication

-   **POST /api/registration/**
    -   **Description:** Register a new user and receive an authentication token.
-   **POST /api/login/**
    -   **Description:** Authenticate a user and receive an authentication token.

## Security

The API uses token-based authentication. To access protected endpoints, include the token in the `Authorization` header with the prefix `Token`:

```
Authorization: Token your_token_here
```

## API Schema & Documentation

The API follows the OpenAPI 3.0 specification. The schema and interactive documentation can be accessed at:

-   **Swagger UI:** `http://127.0.0.1:8000/api/schema/swagger-ui/`
-   **Redoc:** `http://127.0.0.1:8000/api/schema/redoc/`

## Step-by-Step Explanation

1. **User Authentication:**

    - Users register via `/api/registration/` and login via `/api/login/`. The token-based authentication is used for all secured endpoints.

2. **Offers Management:**

    - Offers can be created, retrieved, updated, and deleted using endpoints under `/api/offers/`. When creating an offer, detailed information (offer details) is processed and aggregated.

3. **Orders Management:**

    - Orders are placed based on offer details using the `/api/orders/` endpoints. There are also specialized endpoints to retrieve the count of open or completed orders for a business user.

4. **Reviews:**

    - Reviews can be submitted via `/api/reviews/`. The system ensures that a customer may only submit one review per business user. Reviews can also be updated or deleted by the review creator or an admin.

5. **User Profiles:**

    - User profiles can be retrieved, updated, or deleted via `/api/profile/{id}/`. Separate list endpoints are provided for business profiles (`/api/profiles/business/`) and customer profiles (`/api/profiles/customer/`).

6. **Documentation:**
    - The API documentation is automatically generated from the code (using drf-spectacular) and is available through interactive interfaces (Swagger UI and Redoc).

## License

You may use this code solely for non-commercial educational purposes. Any commercial use, distribution, or modification requires the author's explicit written consent..
