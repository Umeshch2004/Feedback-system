# Lightweight Feedback System

A comprehensive internal feedback management system built with Flask, featuring AI-powered insights and analytics.

## Features

### Core Functionality
- **Role-based Authentication**: Separate dashboards for managers and employees
- **Feedback Management**: Submit, edit, and track feedback with sentiment analysis
- **Real-time Analytics**: Interactive charts showing feedback sentiment trends
- **Acknowledgment System**: Employees can acknowledge received feedback

### AI-Powered Features
- **Sentiment Analysis**: Automatic AI analysis of feedback sentiment and confidence scoring
- **Smart Tagging**: AI-generated tags for feedback categorization
- **Feedback Suggestions**: AI-powered feedback generation based on role and focus area
- **Writing Assistant**: AI feedback improvement and optimization
- **Performance Insights**: Comprehensive AI analysis of feedback history and trends

### Additional Features
- **Feedback Requests**: Employees can proactively request feedback from managers
- **Historical Analytics**: Timeline view of feedback trends and improvements
- **Responsive Design**: Mobile-friendly interface with dark theme
- **Data Export**: Performance metrics and insights generation

## Tech Stack

- **Backend**: Python Flask with SQLAlchemy ORM
- **Frontend**: Vanilla JavaScript with Bootstrap (Replit dark theme)
- **Database**: PostgreSQL (production) / SQLite (development)
- **AI**: OpenAI GPT-4o for sentiment analysis and content generation
- **Charts**: Chart.js for interactive data visualization
- **Deployment**: Docker containerization with Gunicorn

## Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)
- OpenAI API key

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd feedback-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables (if not using Replit)**
   ```bash
   # Only needed for local development - Replit provides these automatically
   export DATABASE_URL="postgresql://user:password@localhost/feedback_db"
   export OPENAI_API_KEY="your-openai-api-key"
   export SESSION_SECRET="your-secret-key"
   ```

4. **Initialize database**
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t feedback-system .
   ```

2. **Run with environment variables**
   ```bash
   docker run -p 5000:5000 \
     -e DATABASE_URL="your-database-url" \
     -e OPENAI_API_KEY="your-openai-api-key" \
     -e SESSION_SECRET="your-secret-key" \
     feedback-system
   ```

### Production Deployment

The application is configured for production deployment with:
- Gunicorn WSGI server with multiple workers
- PostgreSQL database with connection pooling
- Health checks for container orchestration
- Non-root user for security

## Demo Accounts

The system comes with pre-configured demo accounts:

### Managers
- **Username**: `john_manager` | **Password**: `password123`
- **Username**: `sarah_manager` | **Password**: `password123`

### Employees
- **Username**: `alice_employee` | **Password**: `password123`
- **Username**: `bob_employee` | **Password**: `password123`
- **Username**: `charlie_employee` | **Password**: `password123`

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### Dashboard
- `GET /manager/dashboard` - Manager dashboard with team overview
- `GET /employee/dashboard` - Employee dashboard with feedback timeline

### Feedback Management
- `GET /feedback/submit/<employee_id>` - Feedback submission form
- `POST /feedback/submit/<employee_id>` - Submit new feedback
- `GET /feedback/history/<employee_id>` - View feedback history
- `GET /feedback/edit/<feedback_id>` - Edit feedback form
- `POST /feedback/edit/<feedback_id>` - Update feedback
- `POST /feedback/acknowledge/<feedback_id>` - Acknowledge feedback

### AI Features
- `GET /ai/suggestions` - AI feedback suggestions page
- `POST /api/ai-suggestions` - Generate AI feedback suggestions
- `GET /ai/analyzer` - Feedback analysis page
- `POST /api/analyze-feedback` - Analyze feedback sentiment and extract tags
- `GET /ai/insights` - Performance insights page
- `POST /api/performance-insights` - Generate AI performance insights
- `GET /ai/improver` - Feedback writing assistant
- `POST /api/improve-feedback` - Improve feedback with AI

### Employee Features
- `GET /request-feedback` - Request feedback page
- `POST /request-feedback` - Submit feedback request

## Database Schema

### Users Table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `password_hash`
- `role` (manager/employee)
- `manager_id` (Foreign Key to Users)
- `created_at`

### Feedback Table
- `id` (Primary Key)
- `manager_id` (Foreign Key to Users)
- `employee_id` (Foreign Key to Users)
- `strengths` (Text)
- `areas_to_improve` (Text)
- `sentiment` (positive/neutral/negative)
- `tags` (Comma-separated)
- `created_at`
- `updated_at`
- `acknowledged`
- `acknowledged_at`

### Feedback Requests Table
- `id` (Primary Key)
- `employee_id` (Foreign Key to Users)
- `manager_id` (Foreign Key to Users)
- `focus_area`
- `specific_request` (Text)
- `priority` (low/normal/high)
- `status` (pending/in_progress/completed)
- `created_at`
- `completed_at`

## AI Integration

The system uses OpenAI's GPT-4o model for:

1. **Sentiment Analysis**: Analyzes feedback text to determine positive, neutral, or negative sentiment with confidence scoring
2. **Content Generation**: Creates feedback suggestions based on employee role and performance areas
3. **Tag Extraction**: Automatically generates relevant tags from feedback content
4. **Performance Insights**: Analyzes feedback history to provide actionable insights and recommendations
5. **Writing Enhancement**: Improves feedback clarity, professionalism, and actionability

## Design Decisions

### Architecture
- **Monolithic Flask Application**: Simple deployment and maintenance
- **SQLAlchemy ORM**: Type-safe database operations and relationship management
- **Session-based Authentication**: Lightweight and sufficient for internal tools
- **RESTful API Design**: Clear separation between frontend and backend operations

### UI/UX
- **Bootstrap Dark Theme**: Professional appearance matching Replit's design system
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Mobile-first Design**: Responsive layouts for all screen sizes
- **Accessibility**: Semantic HTML and proper ARIA labels

### Security
- **Password Hashing**: Werkzeug's secure password hashing
- **CSRF Protection**: Built into Flask forms
- **Role-based Access Control**: Strict permission checking on all routes
- **Input Validation**: Server-side validation for all user inputs

### AI Integration
- **Error Handling**: Graceful fallbacks when AI services are unavailable
- **Rate Limiting**: Considerate usage of OpenAI API
- **Data Privacy**: Minimal data sent to AI services

## Future Enhancements

- Email notifications for feedback requests and submissions
- Anonymous peer feedback system
- PDF export functionality
- Advanced analytics and reporting
- Integration with HR systems
- Multi-language support
- Advanced role management (team leads, HR, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with appropriate tests
4. Submit a pull request with detailed description

## License

This project is licensed under the MIT License.