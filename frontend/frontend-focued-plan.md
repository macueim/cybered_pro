
I am building a comprehensive Learning Management System (LMS) called CyberEd Pro that is designed specifically for cybersecurity education. The platform aims to provide an faster learning path for professionals and students seeking to advance their knowledge and obtain industry certifications within a three-month timeframe.
The site will allow teachers to add new courses, learners, interact with the core functionality of the application.

I want this LMS full-stack application to be user interface (UI) that is responsive.
I want this LMs site be similar to professional E-commerce Website like Amazon.com, featuring product in our case, coures
and allow view them and add them to cart.

Tips about the look of landing page: from left to right, top to bottom
- Header: start with logon, company name "CyberEd Pro", navigators: Home, about us, How it work, Cores, login, Cart
- Center: action calling bottoms: "I am an instructor", and other "I am a student"
- Footer: copyright, terms and conditions, and links to major social media like Facebook, Youtube, x, and others.
- Make this website to be more professional.



My main objective with this prompt is to create a frontend for already build backend of this application.


The site will have the following expected main users, admin, instructor, and student
The common use cases are:

- potential learner will visit the website, view available courses, add them to the cart, register, add payment, and check out
- The teacher or instructor will be able to perform CRUD operations on all system resources after login.
- An admin is responsible for controlling and managing this learning management system (LMS) with full rights to perform CRUD operations on 
all endpoints.

Examples of courses will be added to the website are, Security+, CEH, CISSP, and other cybersecurity courses.

- Instructor will be allowed to perform the following functionalities: courese Management, learning experience, 
user management, assessment system, communication, communication and collaboration, and analytics and reporting.

To build this LMS, the following technology stacks are used:

The application employs a modern technology stack comprising:

Frontend: HTML5, Tailwind CSS for responsive styling and design consistency, and Alpine for ineractivity and dynamic behavior
Database: postgreSQL

### Frontend Technologies:
- HTML5 for semantic markup and structure
- Tailwind CSS for responsive styling and design consistency
- Alpine.js for client-side interactivity and dynamic behavior


### Backend Technologies:
- **Python**: Core programming language
- **FastAPI**: RESTful API development
- **PostgreSQL**: Relational database for data persistence
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **JWT**: Authentication mechanism


### Core Functionality
1. User Management
   - User registration and authentication
   - Role-based access control (admin, instructor, student)
   - User profiles with learning progress tracking

2. Course Management
   - Course creation and organization
   - Module and lesson structuring
   - Content delivery (text, video, interactive elements)
   - Resource management (documents, links, tools)

3. Learning Experience
   - Interactive learning modules
   - Hands-on labs and virtual environments
   - Progress tracking and learning paths
   - Bookmarking and note-taking capabilities

4. Assessment System
   - Quizzes and tests with various question types
   - Practical exercises and challenges
   - Certification preparation and mock exams
   - Automated grading and feedback

5. Communication and Collaboration
   - Discussion forums
   - Direct messaging
   - Instructor feedback mechanisms
   - Study groups and peer collaboration

6. Analytics and Reporting
   - Learning progress dashboards
   - Performance analytics
   - Certification readiness indicators
   - Administrative reporting

### Non-functional Requirements
1. Performance
   - Fast page load times (<2 seconds)
   - Support for concurrent users (initially 500+)
   - Responsive design for all device types

2. Security
   - Secure authentication and authorization
   - Data encryption
   - Regular security audits
   - Compliance with educational data privacy standards

3. Scalability
   - Horizontal scaling capabilities
   - Modular architecture for future expansion
   - API-first design for integration possibilities

4. Accessibility
   - WCAG 2.1 AA compliance
   - Multi-language support
   - Keyboard navigation


I want to build a front-end for already built backend of this application that will use the following defined endpoint apis:
# User Management Endpoints:
# POST /api/v1/users/register - Register a new user
# POST /api/v1/users/login - User login
# GET /api/v1/users/me - Get current user profile
# PUT /api/v1/users/me - Update current user profile
# GET /api/v1/users/ - Get all users (admin only)
# GET /api/v1/users/{user_id} - Get specific user (admin only)
# PUT /api/v1/users/{user_id} - Update specific user (admin only)
# DELETE /api/v1/users/{user_id} - Delete user (admin only)

# Course Management Endpoints:
# GET /api/v1/courses/ - Get all courses
# POST /api/v1/courses/ - Create a new course (instructor/admin only)
# GET /api/v1/courses/{course_id} - Get specific course
# PUT /api/v1/courses/{course_id} - Update course (instructor/admin only)
# DELETE /api/v1/courses/{course_id} - Delete course (instructor/admin only)
# GET /api/v1/courses/{course_id}/modules - Get course modules
# POST /api/v1/courses/{course_id}/modules - Add module to course
# GET /api/v1/modules/{module_id}/lessons - Get module lessons
# POST /api/v1/modules/{module_id}/lessons - Add lesson to module

# Enrollment Endpoints:
# GET /api/v1/enrollments/ - Get user enrollments
# POST /api/v1/enrollments/ - Enroll in a course
# GET /api/v1/enrollments/{enrollment_id} - Get enrollment details
# PUT /api/v1/enrollments/{enrollment_id} - Update enrollment status
# DELETE /api/v1/enrollments/{enrollment_id} - Withdraw from a course

# Assessment Endpoints:
# GET /api/v1/assessments/ - Get all assessments
# POST /api/v1/assessments/ - Create a new assessment (instructor/admin only)
# GET /api/v1/assessments/{assessment_id} - Get specific assessment
# PUT /api/v1/assessments/{assessment_id} - Update assessment (instructor/admin only)
# DELETE /api/v1/assessments/{assessment_id} - Delete assessment (instructor/admin only)
# POST /api/v1/assessments/{assessment_id}/take - Start an assessment
# POST /api/v1/assessments/{assessment_id}/submit - Submit assessment answers

# Forum Endpoints:
# GET /api/v1/forums/topics - Get all forum topics
# POST /api/v1/forums/topics - Create a new forum topic
# GET /api/v1/forums/topics/{topic_id} - Get specific forum topic
# POST /api/v1/forums/topics/{topic_id}/replies - Add reply to a forum topic

# User Progress Tracking:
# GET /api/v1/progress/courses/{course_id} - Get user progress in a course
# POST /api/v1/progress/lessons/{lesson_id} - Mark lesson as complete
# GET /api/v1/progress/assessments - Get user assessment results


Don't create the code inside jupyter notebook. Show the code, one page at a time.





