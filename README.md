# Online Appointment Booking System for Service Providers
**Author: Krum Yakimov**

## Introduction
This project was developed for my final exam in the [Web Applications with Flask](https://softuni.bg/trainings/4762/web-applications-with-flask-september-2024) course at **SoftUni**. It aims to showcase the principles of structuring Flask RESTful applications while ensuring clean, maintainable, and reusable code. The project includes models, authentication and authorization mechanisms, schemas, and various access levels, along with several API endpoints.

## Project Description
The Online Appointment Booking System is designed to provide a robust backend solution for managing appointments in various service industries (e.g., salons, clinics, tutors). This system allows service providers to automate appointment bookings and manage schedules, while customers can easily book time slots for different services online. 

### Key Features
- **User Management**: 
  - Clients can register, log in, and manage their profiles.
  - Service providers can register and manage their profiles.
  
- **Appointment Management**: 
  - Clients can book, edit, and cancel appointments.
  - Service providers can confirm, reject, and manage appointments.

- **Inquiry Management**: 
  - Service providers can submit inquiries to apply for inclusion in the system.
  - Inquiries can be reviewed and approved or rejected by administrators.

- **Service Management**: 
  - Service providers can manage the services they offer, including categories and subcategories.

- **Integration with Third-Party Services**:
  - **AWS S3** to allow service providers to upload photos showcasing their businesses (e.g., salons, offices). This enables service providers to maintain an online presence and helps clients make informed decisions based on visual representations of services.

  - **AWS SES** for sending notifications via email. This functionality facilitates smooth communication between clients and service providers regarding appointment confirmations, cancellations, and updates.


### Future Functionality
- Automated reminders and follow-up emails.
- Integration with external calendar services (Google Calendar, etc.)
- Secure payment integration with Stripe or Square to handle deposits or full payments at booking.
- Integration with Facebook, Instagram.
- Video integrations (Teleport for virtual appointments).
- Enhanced reporting and analytics features for service providers.
- Inventory management (for salons selling products).
- Mobile application support for better accessibility.

## Installation Instructions
### Prerequisites
- Python 3.11 or higher
- PostgreSQL or SQLite (depending on your configuration)
- AWS account for SES and S3 services

### Steps to Install

1. Clone the repository:
   ```bash
   git clone https://github.com/KrumYakimov/FlaskAppointmentBookingAPI.git
   ```
   or, if using SSH:
   ```bash
   git clone git@github.com:KrumYakimov/FlaskAppointmentBookingAPI.git
   ```
   
2. Create a virtual environment and activate it:
   - For macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - For Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up PostgreSQL:
   - Make sure PostgreSQL is installed and running.
   - Create a database for Development environment:
     ```sql
     CREATE DATABASE appointment_booking_db;
     ```
   - Create a database for Testing environment:
     ```sql
     CREATE DATABASE appointment_booking_test;
     ```
5. Set up environment variables in a `.env` file:
   ```plaintext
   DB_USER=<your_database_username>           # Database username
   DB_PASSWORD=<your_database_password>       # Database password
   DB_HOST=<your_database_host>                # Database host (e.g., localhost)
   DB_PORT=<your_database_port>                # Database port (e.g., 5432 for PostgreSQL)
   DB_NAME=appointment_booking_db              # Main database name
   TEST_DB_NAME=appointment_booking_test       # Test database name
   SECRET_KEY=<your_secret_key>                # Secret key for session management
   CONFIG_ENV="config.<your_environment>"      # Configuration environment (e.g., DevelopmentConfig)
   TOKEN_EXPIRATION_HOURS=24                   # JWT token expiration time in hours
   AWS_ACCESS_KEY=<your_aws_access_key>       # AWS access key
   AWS_SECRET=<your_aws_secret_key>           # AWS secret key
   AWS_BUCKET=<your_aws_bucket>                # S3 bucket name for uploads
   AWS_REGION=<your_aws_region>                # AWS region (e.g., us-east-1)
   EMAIL_SENDER=<your_aws_email_sender>       # Email sender address for notifications

### Running the Application
1. Initialize the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

2. Start the Flask server:
   ```bash
   flask run
   ```

### Testing
1. To run the unit tests:
   ```bash
   pytest tests/
   ```

## API Documentation with Swagger UI

This project includes an interactive API documentation interface using Swagger UI. Swagger UI provides a visual representation of the API endpoints, making it easier for developers to understand how to interact with the API.

### Accessing Swagger UI

Once your Flask application is running, you can access the Swagger UI at the following URL:

```
http://127.0.0.1:5000/static/swagger-ui/index.html
```

### Swagger JSON Specification

The API's Swagger JSON specification can be accessed directly at:

```
http://127.0.0.1:5000/swagger.json
```

### Additional Information

For more details on how to configure the Swagger UI or to modify the Swagger JSON specification, refer to the Swagger UI [documentation](https://swagger.io/tools/swagger-ui/docs/usage/installation/).
``

## API Endpoint

### User Management API

#### 1. Client Registration
- **Endpoint**: `POST /clients`
- **Description**: Register a new client with email, password, first name, last name, and phone number.
- **Request Body**:
  ```json
  {
      "email": "string",
      "password": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string"
  }
  ```
- **Responses**:
  - `201 Created`: Successfully registered.
  - `409 Conflict`: The provided information doesn't meet our data management policy. Please verify and try again.
  - `400 Bad Request`: Possible error messages include:
  ```json
  {
      "message": "Invalid payload: {'email': ['Not a valid email address.', 'Invalid email format.'], 'first_name': ['First name must be between 2 and 50 characters.'], 'phone': ['Phone number must start with 0 and contain exactly 10 to 15 digits.'], 'password': ['Your password needs to be at least 8 characters long.', 'Your password should include at least one special character (e.g., !, @, #, $, etc.).', 'Too common!']}"
  }
  ```
   ```json
  {
      "message": "Invalid payload: {'email': ['Email is required.'], 'first_name': ['First name is required.'], 'last_name': ['Last name is required.'], 'phone': ['Phone number is required.'], 'password': ['Missing data for required field.']}"
  }
  ```
   ```json
  {
      "message": "The provided information doesn't meet our data management policy. Please verify and try again."
  }
  ```

#### 2. User Login
- **Endpoint**: `POST /login`
- **Description**: Authenticate a user by email and password.
- **Request Body**:
  ```json
  {
      "email": "string",
      "password": "string"
  }
  ```
- **Responses**:
  - `200 OK`: Returns a token for authenticated access.
  - `401 Unauthorized`: Possible error messages include:
  ```json
  {
    "message": "Invalid payload: {'email': ['Not a valid email address.', 'Invalid email format.']}"
  }
  ```
  ```json
  {
   "message": "Invalid username or password"
  }
  ```

#### 3. Change Password
- **Endpoint**: `POST /change-password`
- **Description**: Change the user's password.
- **Request Body**:
  ```json
  {
      "old_password": "string",
      "new_password": "string"
  }
  ```
- **Responses**:
  - `200 OK`: Password changed successfully.
  - `400 Bad Request`: Possible error messages include:
  ```json
  {
    "message": "Invalid payload: {'_schema': ['New password cannot be the same as the old password.']"
  }
  ```
#### 4. Client Profile
- **Endpoint**: `GET /clients/profile`
- **Description**: Retrieve the authenticated client's profile.
- **Responses**:
  - `200 OK`: Returns client profile data.
  - `401 Unauthorized`: User not authenticated.

#### 5. Client Editing
- **Endpoint**: `PUT /clients/profile/edit`
- **Description**: Update the client's profile.
- **Request Body**:
  ```json
  {
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string"
  }
  ```
- **Responses**:
  - `200 OK`: Profile updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `409 Conflict`: The provided information doesn't meet our data management policy. Please verify and try again.
  - `400 Bad Request`: Possible error messages include:
  ```json
  {
      "message": "Invalid payload: {'email': ['Not a valid email address.', 'Invalid email format.'], 'first_name': ['First name must be between 2 and 50 characters.'], 'phone': ['Phone number must start with 0 and contain exactly 10 to 15 digits.']}"
  }
  ```

#### 6. Client Deactivation
- **Endpoint**: `PUT /clients/profile/deactivate`
- **Description**: Deactivate the authenticated client's profile.
- **Responses**:
  - `200 OK`: Client profile deactivated successfully.
  - `401 Unauthorized`: User not authenticated.

#### 7. User Registration
- **Endpoint**: `/users`
- **Method**: `POST`
- **Description**: Registers a new user in the system.
- **Request Body**:
  ```json
  {
      "email": "example@mail.com",
      "password": "examplePassword!",
      "first_name": "First",
      "last_name": "Last",
      "phone": "1234567890"
  }
  ```
- **Responses**:
  - `201 Created`: User successfully registered.
  - `400 Bad Request`: {"message": "string"}
  - `409 Conflict`: The provided information doesn't meet our data management policy. Please verify and try again.

#### 8. User Profile
- **Endpoint**: `"/users/profile", "/users/profile/{status}", "/users/profile/{id}"`
- **Method**: `GET`
- **Description**: Retrieves the profile information of the user.
- **Responses**:
  - `200 OK`: Returns user profile data.
  - `401 Unauthorized`: User not authorized.
  - `404 Not Found`: User does not exist.

#### 9. User Editing
- **Endpoint**: `/users/{id}/edit/`
- **Method**: `PUT`
- **Description**: Updates the specified user's profile information.
- **Request Body**:
  ```json
  {
      "email": "string",
      "first_name": "string",
      "last_name": "string",
      "phone": "string"
  }
  ```
- **Responses**:
  - `200 OK`: User account successfully updated.
  - `404 Not Found`: User does not exist.
  - `401 Unauthorized`: User not authorized.
  - `400 Bad Request`: {"message": "string"}
  
#### 10. User Deactivation
- **Endpoint**: `/users/{id}/deactivate`
- **Method**: `PUT`
- **Description**: Deactivates a user account, preventing future logins.
- **Responses**:
  - `200 OK`: User account successfully deactivated.
  - `404 Not Found`: User does not exist.
  - `401 Unauthorized`: User not authorized.

### Inquiry Management API

#### 1. Inquiry Registration
- **Endpoint**: `POST /inquiries`
- **Description**: Register a new inquiry for a salon.
- **Request Body**:
  ```json
  {
      "salon_name": "sting",
      "city": "sting",
      "email": "sting",
      "first_name": "sting",
      "last_name": "sting",
      "phone": "sting"
  }
  ```
- **Responses**:
  - `201 Created`: Inquiry created successfully.
  - `400 Bad Request`: {"message": "string"}

#### 2. Inquiries
- **Endpoint**: `GET "/approver/inquiries", "/approver/inquiries/{status}"`
- **Description**: Retrieve pending inquiries.
- **Responses**:
  - `200 OK`: Returns list of pending inquiries.
  - `401 Unauthorized`: User not authorized.

#### 3. Inquiry Approval
- **Endpoint**: `PUT /approver/inquiries/{id}/approval`
- **Description**: Approve an inquiry.
- **Responses**:
  - `200 OK`: Inquiry approved successfully.
  - `404 Not Found`: Inquiry not found.
  - `401 Unauthorized`: User not authorized.

#### 4. Inquiry Rejection
- **Endpoint**: `PUT /approver/inquiries/{id}/rejection`
- **Description**: Reject an inquiry.
- **Responses**:
  - `200 OK`: Inquiry rejected successfully.
  - `404 Not Found`: Inquiry not found.
  - `401 Unauthorized`: User not authorized.

#### 5. Inquiry No Show Status
- **Endpoint**: `PUT /approver/inquiries/{id}/no-show`
- **Description**: Mark an inquiry as no-show.
- **Responses**:
  - `200 OK`: Inquiry marked as no-show.
  - `404 Not Found`: Inquiry not found.
  - `401 Unauthorized`: User not authorized.


### Provider Management API

#### 1. Provider Registration
- **Endpoint**: `POST /provider`
- **Description**: Register a new service provider.
- **Request Body**:
  ```json
  {
      "company_name": "string",
      "trade_name": "string",
      "uic": "string",
      "photo": "string",
      "photo_extension": "string",
      "inquiry_id": 15,
      "country": "string",
      "district": "string",
      "city": "string",
      "neighborhood": "string",
      "street": "string",
      "street_number": "string",
      "block_number": "string",
      "apartment": "string",
      "floor": "string",
      "postal_code": "string",
      "latitude": "number",
      "longitude": "number"
  }
  ```
- **Responses**:
  - `201 Created`: Provider registered successfully.
  - `400 Bad Request`: {"message": "string"}.
  - `401 Unauthorized`: User not authorized.

#### 2. Provider Editing
- **Endpoint**: `PUT /provider/{id}/edit`
- **Description**: Update the provider's information.
- **Request Body**:
  ```json
  {
      "company_name": "string",
      "trade_name": "string",
      "country": "string",
      "district": "string",
      "city": "string",
      "neighborhood": "string",
      "street": "string",
      "street_number": "string",
      "block_number": "string",
      "apartment": "string",
      "floor": "string",
      "postal_code": "string",
      "latitude": "number",
      "longitude": "number"
  }
  ```
- **Responses**:
  - `200 OK`: Provider updated successfully.
  - `404 Not Found`: Provider not found.
  - `400 Bad Request`: {"message": "string"}.
  - `401 Unauthorized`: User not authorized.

#### 3. Provider Profile
- **Endpoint**: `GET "/providers/profile", "/providers/profile/{status}", "/providers/profile/{id}"`
- **Description**: Retrieve provider profile.
- **Responses**:
  - `200 OK`: Returns provider profile data.
  - `404 Not Found`: Provider not found.
  - `401 Unauthorized`: User not authorized.

#### 4. Provider Deactivate
- **Endpoint**: `PUT /provider/{id}/deactivate`
- **Description**: Deactivate a provider.
- **Responses**:
  - `200 OK`: Provider deactivated successfully.
  - `404 Not Found`: Provider not found.
  - `401 Unauthorized`: User not authorized.

### Service Management API

#### 1. Service Registration
- **Endpoint**: `POST /services`
- **Description**: Register a new service.
- **Request Body**:
  ```json
  {
      "name": "test_1",
      "price": "decimal",
      "duration": "integer",
      "service_subcategory_id": "integer",
      "service_provider_id": "integer",
      "staff_id": "integer"
  }
  ```
- **Responses**:
  - `201 Created`: Service registered successfully.
  - `400 Bad Request`: {"message": "string"}
  - `401 Unauthorized`: User not authorized.

#### 2. Service Profile
- **Endpoint**: `GET "/services/profile", "/services/profile/{status}", "/services/profile/{id}"`
- **Description**: Retrieve the list of services.
- **Responses**:
  - `200 OK`: Returns the list of services.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: No services found.

#### 3. Service Editing
- **Endpoint**: `PUT /services/{id}/edit`
- **Description**: Update service information.
- **Request Body**:
  ```json
  {
      "name": "string",
      "price": "decimal",
      "duration": "integer",
      "staff_id": "integer"
  }
  ```
- **Responses**:
  - `200 OK`: Service updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Service not found.
  - `400 Bad Request`: {"message": "string"}

#### 4. Service Deactivate
- **Endpoint**: `PUT /services/{id}/deactivate`
- **Description**: Deactivate a service.
- **Responses**:
  - `200 OK`: Service deactivated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Service not found.

### Category Management API

#### 1. Category Registration
- **Endpoint**: `POST /categories`
- **Description**: Register a new service category.
- **Request Body**:
  ```json
  {
      "name": "string"
  }
  ```
- **Responses**:
  - `201 Created`: Category registered successfully.
  - `401 Unauthorized`: User not authenticated.
  - `400 Bad Request`: Invalid input data.
   ```json
  {
    "message": "string"
  }
  ```

#### 2. Category Profile
- **Endpoint**: `GET "/categories/profile","/categories/profile/{status}", "/categories/profile/{id}"`
- **Description**: Retrieve the list of categories.
- **Responses**:
  - `200 OK`: Returns the list of categories.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: No categories found.

#### 3. Category Editing
- **Endpoint**: `PUT /categories/{id}/edit`
-

 **Description**: Update a category's information.
- **Request Body**:
  ```json
  {
      "name": "string"
  }
  ```
- **Responses**:
  - `200 OK`: Category updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Category not found.
  - `400 Bad Request`: Invalid input data.

#### 4. Category Deactivate
- **Endpoint**: `PUT /categories/{id}/deactivate`
- **Description**: Deactivate a category.
- **Responses**:
  - `200 OK`: Category deactivated successfully.
  - `404 Not Found`: Category not found.

### SubCategory Management API

#### 1. SubCategory Registration
- **Endpoint**: `POST /subcategories`
- **Description**: Register a new service subcategory.
- **Request Body**:
  ```json
  {
      "name": "string",
      "category_id": "integer"
  }
  ```
- **Responses**:
  - `201 Created`: Subcategory registered successfully.
  - `401 Unauthorized`: User not authenticated.
  - `400 Bad Request`: {"message": "string"}

#### 2. SubCategory Profile
- **Endpoint**: `GET "/subcategories/profile", "/subcategories/profile/{status}>","/subcategories/profile/{id}>"`
- **Description**: Retrieve the list of subcategories.
- **Responses**:
  - `200 OK`: Returns the list of subcategories.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: No subcategories found.

#### 3. SubCategory Editing
- **Endpoint**: `PUT /subcategories/{id}/edit`
- **Description**: Update a subcategory's information.
- **Request Body**:
  ```json
  {
      "name": "string"
  }
  ```
- **Responses**:
  - `200 OK`: Subcategory updated successfully.
  - `404 Not Found`: Subcategory not found.
  - `401 Unauthorized`: User not authenticated.
  - `400 Bad Request`: {"message": "string"}

#### 4. SubCategory Deactivate
- **Endpoint**: `PUT /subcategories/{id}/deactivate`
- **Description**: Deactivate a subcategory.
- **Responses**:
  - `200 OK`: Subcategory deactivated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Subcategory not found.

### Working Hour Management API

#### 1. Working Hour Registration
- **Endpoint**: `POST /working_hours/register`
- **Description**: Register working hours for providers and staff.
- **Request Body**:
  ```json
  {
      "provider_id": "integer",
      "employees": [
          {
              "employee_id": "integer",
              "working_hours": [
                  {
                      "day_of_week": "integer",
                      "start_time": "HH:MM",
                      "end_time": "HH:MM",
                      "provider_id": "integer",
                      "employee_id": "integer"
                  },
                  ...
              ]
          },
          ...
      ]
  }
  ```
- **Responses**:
  - `201 Created`: Working hours registered successfully.
  - `400 Bad Request`: Invalid input data.
  - `400 Bad Request`: {"message": "string"}
  ```json
  {
    "message": "string"
  }
  ```

#### 2. Working Hour Profile
- **Endpoint**: `GET "/working_hours/profile",
        "/working_hours/profile/provider/{provider_id}",
        "/working_hours/profile/employee/{employee_id}"`
- **Description**: Retrieve working hours for a specific employee.
- **Responses**:
  - `200 OK`: Returns the employee's working hours.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Employee not found.

#### 3. Working Hour Editing
- **Endpoint**: `PUT /working_hours/{id}/edit`
- **Description**: Update a specific working hour entry.
- **Request Body**:
  ```json
  {
      "day_of_week": "integer",
      "start_time": "HH:MM",
      "end_time": "HH:MM",
      "provider_id": "integer",
      "employee_id": "integer"
  }
  ```
- **Responses**:
  - `200 OK`: Working hour updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Working hour not found.
  - `400 Bad Request`: {"message": "string"}

#### 4. Working Hour Deactivate
- **Endpoint**: `PUT /working_hours/{id}/deactivate`
- **Description**: Deactivate a specific working hour entry.
- **Responses**:
  - `200 OK`: Working hour deactivated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Working hour not found.

### Appointment Management API

#### 1. Available Slots
- **Endpoint**: `GET /appointments/available_slots/{staff_id}/{service_id}/{date}`
- **Description**: Retrieve available appointment slots for a specific staff member and service on a given date.
- **Responses**:
  - `200 OK`: Returns available slots.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: No slots available.

#### 2. Customer Appointment Booking
- **Endpoint**: `POST /appointments`
- **Description**: Book an appointment for a specific service.
- **Request Body**:
  ```json
  {
      "service_id": "integer",
      "staff_id": "integer",
      "appointment_time": "YYYY-MM-DDTHH:MM:SS",
  }
  ```
- **Responses**:
  - `201 Created`: Appointment booked successfully.
  - `401 Unauthorized`: User not authenticated.
  - `400 Bad Request`: Invalid input data.
   ```json
  {
    "message": "string"
  }
  ```

#### 3. Customer Appointments
- **Endpoint**: `GET /appointments/info`
- **Description**: Retrieve all appointments for the authenticated user.
- **Responses**:
  - `200 OK`: Returns the list of appointments.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: No appointments found.

#### 4. Customer Appointment Editing
- **Endpoint**: `PUT /appointments/{id}/edit`
- **Description**: Edit an existing appointment.
- **Request Body**:
  ```json
  {
      "appointment_time": "YYYY-MM-DDTHH:MM:SS"
  }
  ```
- **Responses**:
  - `200 OK`: Appointment updated successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 5. Customer Appointment Cancellation
- **Endpoint**: `DELETE /appointments/{id}/cancel`
- **Description**: Cancel an existing appointment.
- **Responses**:
  - `200 OK`: Appointment cancelled successfully.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 6. Staff Appointment Confirmation
- **Endpoint**: `PUT /appointments/{id}/confirm`
- **Description**: Confirm an appointment as staff.
- **Responses**:
  - `200 OK`: Appointment confirmed.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 7. Staff Appointment Rejection
- **Endpoint**: `PUT /appointments/{id}/reject`
- **Description**: Reject an appointment as staff.
- **Responses**:
  - `200 OK`: Appointment rejected.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 8. Staff Appointment No Show
- **Endpoint**: `PUT /appointments/{id}/no_show`
- **Description**: Mark an appointment as no-show.
- **Responses**:
  - `200 OK`: Appointment marked as no-show.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 9. Staff Appointment Cancellation
- **Endpoint**: `PUT /appointments/{id}/cancel`
- **Description**: Mark an appointment as cancel.
- **Responses**:
  - `200 OK`: Appointment marked as cancel.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.

#### 10. Staff Appointment Completion
- **Endpoint**: `PUT /appointments/{id}/complete`
- **Description**: Mark an appointment as completed.
- **Responses**:
  - `200 OK`: Appointment marked as completed.
  - `401 Unauthorized`: User not authenticated.
  - `404 Not Found`: Appointment not found.
  
## General Bad Request Error Handling

- **Status Code**: `400 Bad Request`
- **Description**: This status code indicates that the server could not understand the request due to invalid syntax or data. The response will typically include a message detailing the specific validation error(s) that occurred.

### Possible Error Messages:

- **Invalid Input**: When the provided data does not conform to the expected format or constraints.
  - **Example**: "Invalid email format. Please provide a valid email address."

- **Missing Required Fields**: When the request body is missing one or more required fields.
  - **Example**: "The 'password' field is required."

- **Out of Range Values**: When numeric values fall outside the expected range.
  - **Example**: "Duration must be a positive integer."

- **Invalid Enumeration Values**: When an invalid value is provided for an enumerated field.
  - **Example**: "Role must be one of: 'CLIENT', 'ADMIN', 'SERVICE_PROVIDER'."

- **Format Errors**: When the data format is incorrect (e.g., date format, number format).
  - **Example**: "Start time must be in HH:MM format."


## Contributing
Feel free to open issues or submit pull requests if you have suggestions for improvements.

## License
This project is licensed under the MIT License.

## Acknowledgments
- ### Special thanks to the course teacher **Ines Ivanova** for her guidance and insights.

