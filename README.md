# Flight Tracker Application

A web application that allows users to track flights between different airports, with real-time data provided by the Aviation Stack API. The application includes user authentication and a responsive UI.

## Features

- User authentication system
- Real-time flight data (via Aviation Stack API)
- Filter flights by origin, destination, airline, and status
- Responsive design
- REST API for flight data
- Containerized with Docker for easy deployment

## Technical Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Authentication:** Flask Session Management
- **API Integration:** Aviation Stack API
- **Containerization:** Docker
- **Remote Access:** SSH enabled

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Aviation Stack API key (optional, mock data available)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/flight-tracker.git
   cd flight-tracker
   ```

2. Start the application using Docker Compose:
   ```
   docker-compose up -d
   ```

3. Access the application at:
   ```
   http://localhost:8888
   ```

4. Login with default credentials:
   - Username: `david`
   - Password: `password`

### SSH Access

The application container has SSH enabled for administrative access:

```
ssh -p 2222 root@localhost
```

Default SSH password: `password`

## Environment Variables

You can configure the application using the following environment variables:

- `AVIATION_STACK_API_KEY`: Your Aviation Stack API key
- `FLASK_ENV`: Set to `production` for production deployment
- `FLASK_APP`: Set to `app.py`

## License

[MIT License](LICENSE)
