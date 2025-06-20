// js/api.js

/**
 * API Service for CyberEd Pro
 * Provides a centralized interface for all API calls with:
 * - Caching
 * - Timeout handling
 * - Retry mechanism
 * - Consistent error handling
 */
class ApiService {
    constructor() {
        this.baseUrl = 'http://127.0.0.1:8000/api/v1';
        this.defaultTimeout = 10000; // 10 seconds
        this.maxRetries = 3;

        // Cache configuration
        this.cache = {
            userProfile: { data: null, timestamp: null, duration: Infinity }, // Until invalidated
            coursesList: { data: null, timestamp: null, duration: 120000 }, // 2 minutes
            courseDetails: {}, // Individual course caching
            enrollments: { data: null, timestamp: null, duration: 300000 } // 5 minutes
        };
    }

    /**
     * Get authorization headers
     * @returns {Object} Headers object with authorization if available
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };

        const token = localStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    /**
     * Fetch with timeout
     * @param {string} url - URL to fetch
     * @param {Object} options - Fetch options
     * @param {number} timeout - Timeout in ms
     * @returns {Promise} - Promise with response
     */
    async fetchWithTimeout(url, options, timeout = this.defaultTimeout) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });

            clearTimeout(id);
            return response;
        } catch (error) {
            clearTimeout(id);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * Fetch with retry
     * @param {string} url - URL to fetch
     * @param {Object} options - Fetch options
     * @param {number} retries - Number of retries
     * @returns {Promise} - Promise with response
     */
    async fetchWithRetry(url, options, retries = this.maxRetries) {
        let lastError;

        for (let i = 0; i < retries; i++) {
            try {
                return await this.fetchWithTimeout(url, options);
            } catch (error) {
                console.log(`Retry attempt ${i + 1}/${retries} failed:`, error.message);
                lastError = error;

                // Only retry on network errors or 5xx responses
                if (!error.response || (error.response && error.response.status < 500)) {
                    throw error;
                }

                // Exponential backoff
                await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
            }
        }

        throw lastError;
    }

    /**
     * Main request method
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @param {boolean} useCache - Whether to use cache for GET requests
     * @returns {Promise} - Promise with JSON data
     */
    async request(endpoint, options = {}, useCache = true) {
        const url = `${this.baseUrl}${endpoint}`;
        const method = options.method || 'GET';

        // Try to return from cache for GET requests if enabled
        if (method === 'GET' && useCache) {
            const cachedData = this.getCachedData(endpoint);
            if (cachedData) {
                return cachedData;
            }
        }

        try {
            const response = await this.fetchWithRetry(url, options);

            // Handle non-2xx responses
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw {
                    status: response.status,
                    message: errorData.detail || response.statusText,
                    response
                };
            }

            // Handle empty response
            if (response.status === 204) {
                return null;
            }

            const data = await response.json();

            // Cache successful GET requests
            if (method === 'GET' && useCache) {
                this.setCachedData(endpoint, data);
            }

            // Invalidate cache for mutation operations
            if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
                this.invalidateCacheByEndpoint(endpoint);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Get cached data if still valid
     * @param {string} endpoint - API endpoint
     * @returns {Object|null} - Cached data or null
     */
    getCachedData(endpoint) {
        // User profile cache
        if (endpoint === '/users/me') {
            const { data, timestamp, duration } = this.cache.userProfile;
            if (data && timestamp && Date.now() - timestamp < duration) {
                return data;
            }
        }

        // Courses list cache
        if (endpoint === '/courses/') {
            const { data, timestamp, duration } = this.cache.coursesList;
            if (data && timestamp && Date.now() - timestamp < duration) {
                return data;
            }
        }

        // Course details cache
        if (endpoint.match(/^\/courses\/\d+$/)) {
            const courseId = endpoint.split('/')[2];
            const courseCache = this.cache.courseDetails[courseId];
            if (courseCache && courseCache.data && courseCache.timestamp &&
                Date.now() - courseCache.timestamp < 300000) { // 5 minutes
                return courseCache.data;
            }
        }

        // Enrollments cache
        if (endpoint === '/enrollments/') {
            const { data, timestamp, duration } = this.cache.enrollments;
            if (data && timestamp && Date.now() - timestamp < duration) {
                return data;
            }
        }

        return null;
    }

    /**
     * Set cached data
     * @param {string} endpoint - API endpoint
     * @param {Object} data - Data to cache
     */
    setCachedData(endpoint, data) {
        // User profile cache
        if (endpoint === '/users/me') {
            this.cache.userProfile.data = data;
            this.cache.userProfile.timestamp = Date.now();
        }

        // Courses list cache
        if (endpoint === '/courses/') {
            this.cache.coursesList.data = data;
            this.cache.coursesList.timestamp = Date.now();
        }

        // Course details cache
        if (endpoint.match(/^\/courses\/\d+$/)) {
            const courseId = endpoint.split('/')[2];
            this.cache.courseDetails[courseId] = {
                data,
                timestamp: Date.now()
            };
        }

        // Enrollments cache
        if (endpoint === '/enrollments/') {
            this.cache.enrollments.data = data;
            this.cache.enrollments.timestamp = Date.now();
        }
    }

    /**
     * Invalidate cache based on endpoint
     * @param {string} endpoint - API endpoint
     */
    invalidateCacheByEndpoint(endpoint) {
        // Invalidate user cache on user updates
        if (endpoint.includes('/users/')) {
            this.cache.userProfile.data = null;
            this.cache.userProfile.timestamp = null;
        }

        // Invalidate course caches on course changes
        if (endpoint.includes('/courses/')) {
            this.cache.coursesList.data = null;
            this.cache.coursesList.timestamp = null;

            // If it's a specific course, invalidate that course's cache
            const match = endpoint.match(/^\/courses\/(\d+)/);
            if (match) {
                const courseId = match[1];
                if (this.cache.courseDetails[courseId]) {
                    delete this.cache.courseDetails[courseId];
                }
            }
        }

        // Invalidate enrollments cache on enrollment changes
        if (endpoint.includes('/enrollments/')) {
            this.cache.enrollments.data = null;
            this.cache.enrollments.timestamp = null;
        }
    }

    /**
     * Manually invalidate all caches
     */
    invalidateAllCaches() {
        this.cache.userProfile.data = null;
        this.cache.userProfile.timestamp = null;
        this.cache.coursesList.data = null;
        this.cache.coursesList.timestamp = null;
        this.cache.courseDetails = {};
        this.cache.enrollments.data = null;
        this.cache.enrollments.timestamp = null;
    }

    // API methods for user management

    /**
     * Register new user
     * @param {Object} userData - User registration data
     * @returns {Promise} - Registered user data
     */
    async register(userData) {
        return this.request('/users/register', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
    }

    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise} - Login response with token
     */
    async login(email, password) {
        return this.request('/users/login', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ username: email, password })
        });
    }

    /**
     * Get current user profile
     * @returns {Promise} - User profile data
     */
    async getCurrentUser() {
        return this.request('/users/me', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Update current user profile
     * @param {Object} userData - User data to update
     * @returns {Promise} - Updated user data
     */
    async updateCurrentUser(userData) {
        return this.request('/users/me', {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
    }

    /**
     * Get all users (admin only)
     * @returns {Promise} - List of users
     */
    async getUsers() {
        return this.request('/users/', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Get specific user by ID (admin only)
     * @param {number} userId - User ID
     * @returns {Promise} - User data
     */
    async getUser(userId) {
        return this.request(`/users/${userId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Update user (admin only)
     * @param {number} userId - User ID
     * @param {Object} userData - User data to update
     * @returns {Promise} - Updated user data
     */
    async updateUser(userId, userData) {
        return this.request(`/users/${userId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(userData)
        });
    }

    /**
     * Delete user (admin only)
     * @param {number} userId - User ID
     * @returns {Promise} - Deleted user data
     */
    async deleteUser(userId) {
        return this.request(`/users/${userId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    // API methods for course management

    /**
     * Get all courses
     * @returns {Promise} - List of courses
     */
    async getCourses() {
        return this.request('/courses/', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Create a new course (instructor/admin only)
     * @param {Object} courseData - Course data
     * @returns {Promise} - Created course data
     */
    async createCourse(courseData) {
        return this.request('/courses/', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(courseData)
        });
    }

    /**
     * Get specific course
     * @param {number} courseId - Course ID
     * @returns {Promise} - Course data
     */
    async getCourse(courseId) {
        return this.request(`/courses/${courseId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Update course (instructor/admin only)
     * @param {number} courseId - Course ID
     * @param {Object} courseData - Course data to update
     * @returns {Promise} - Updated course data
     */
    async updateCourse(courseId, courseData) {
        return this.request(`/courses/${courseId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(courseData)
        });
    }

    /**
     * Delete course (instructor/admin only)
     * @param {number} courseId - Course ID
     * @returns {Promise} - Deleted course data
     */
    async deleteCourse(courseId) {
        return this.request(`/courses/${courseId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    /**
     * Get course modules
     * @param {number} courseId - Course ID
     * @returns {Promise} - List of modules
     */
    async getCourseModules(courseId) {
        return this.request(`/courses/${courseId}/modules`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Add module to course
     * @param {number} courseId - Course ID
     * @param {Object} moduleData - Module data
     * @returns {Promise} - Created module data
     */
    async addCourseModule(courseId, moduleData) {
        return this.request(`/courses/${courseId}/modules`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(moduleData)
        });
    }

    /**
     * Get module lessons
     * @param {number} moduleId - Module ID
     * @returns {Promise} - List of lessons
     */
    async getModuleLessons(moduleId) {
        return this.request(`/modules/${moduleId}/lessons`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Add lesson to module
     * @param {number} moduleId - Module ID
     * @param {Object} lessonData - Lesson data
     * @returns {Promise} - Created lesson data
     */
    async addModuleLesson(moduleId, lessonData) {
        return this.request(`/modules/${moduleId}/lessons`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(lessonData)
        });
    }

    // API methods for enrollment management

    /**
     * Get user enrollments
     * @returns {Promise} - List of enrollments
     */
    async getEnrollments() {
        return this.request('/enrollments/', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Enroll in a course
     * @param {Object} enrollmentData - Enrollment data
     * @returns {Promise} - Created enrollment data
     */
    async createEnrollment(enrollmentData) {
        return this.request('/enrollments/', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(enrollmentData)
        });
    }

    /**
     * Get enrollment details
     * @param {number} enrollmentId - Enrollment ID
     * @returns {Promise} - Enrollment data
     */
    async getEnrollment(enrollmentId) {
        return this.request(`/enrollments/${enrollmentId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Update enrollment status
     * @param {number} enrollmentId - Enrollment ID
     * @param {Object} enrollmentData - Enrollment data to update
     * @returns {Promise} - Updated enrollment data
     */
    async updateEnrollment(enrollmentId, enrollmentData) {
        return this.request(`/enrollments/${enrollmentId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(enrollmentData)
        });
    }

    /**
     * Withdraw from a course
     * @param {number} enrollmentId - Enrollment ID
     * @returns {Promise} - Deleted enrollment data
     */
    async deleteEnrollment(enrollmentId) {
        return this.request(`/enrollments/${enrollmentId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    // API methods for assessment management

    /**
     * Get all assessments
     * @returns {Promise} - List of assessments
     */
    async getAssessments() {
        return this.request('/assessments/', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Create a new assessment (instructor/admin only)
     * @param {Object} assessmentData - Assessment data
     * @returns {Promise} - Created assessment data
     */
    async createAssessment(assessmentData) {
        return this.request('/assessments/', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(assessmentData)
        });
    }

    /**
     * Get specific assessment
     * @param {number} assessmentId - Assessment ID
     * @returns {Promise} - Assessment data
     */
    async getAssessment(assessmentId) {
        return this.request(`/assessments/${assessmentId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Update assessment (instructor/admin only)
     * @param {number} assessmentId - Assessment ID
     * @param {Object} assessmentData - Assessment data to update
     * @returns {Promise} - Updated assessment data
     */
    async updateAssessment(assessmentId, assessmentData) {
        return this.request(`/assessments/${assessmentId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(assessmentData)
        });
    }

    /**
     * Delete assessment (instructor/admin only)
     * @param {number} assessmentId - Assessment ID
     * @returns {Promise} - Deleted assessment data
     */
    async deleteAssessment(assessmentId) {
        return this.request(`/assessments/${assessmentId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
    }

    /**
     * Start an assessment
     * @param {number} assessmentId - Assessment ID
     * @returns {Promise} - Assessment start data
     */
    async startAssessment(assessmentId) {
        return this.request(`/assessments/${assessmentId}/take`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    /**
     * Submit assessment answers
     * @param {number} assessmentId - Assessment ID
     * @param {Object} answerData - Assessment answers
     * @returns {Promise} - Assessment result data
     */
    async submitAssessment(assessmentId, answerData) {
        return this.request(`/assessments/${assessmentId}/submit`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(answerData)
        });
    }

    // API methods for forum management

    /**
     * Get all forum topics
     * @returns {Promise} - List of topics
     */
    async getForumTopics() {
        return this.request('/forums/topics', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Create a new forum topic
     * @param {Object} topicData - Topic data
     * @returns {Promise} - Created topic data
     */
    async createForumTopic(topicData) {
        return this.request('/forums/topics', {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(topicData)
        });
    }

    /**
     * Get specific forum topic
     * @param {number} topicId - Topic ID
     * @returns {Promise} - Topic data
     */
    async getForumTopic(topicId) {
        return this.request(`/forums/topics/${topicId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Add reply to a forum topic
     * @param {number} topicId - Topic ID
     * @param {Object} replyData - Reply data
     * @returns {Promise} - Created reply data
     */
    async addForumReply(topicId, replyData) {
        return this.request(`/forums/topics/${topicId}/replies`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(replyData)
        });
    }

    // API methods for progress tracking

    /**
     * Get user progress in a course
     * @param {number} courseId - Course ID
     * @returns {Promise} - Course progress data
     */
    async getCourseProgress(courseId) {
        return this.request(`/progress/courses/${courseId}`, {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Mark lesson as complete
     * @param {number} lessonId - Lesson ID
     * @returns {Promise} - Completion data
     */
    async completeLesson(lessonId) {
        return this.request(`/progress/lessons/${lessonId}`, {
            method: 'POST',
            headers: this.getHeaders()
        });
    }

    /**
     * Get user assessment results
     * @returns {Promise} - Assessment results data
     */
    async getAssessmentResults() {
        return this.request('/progress/assessments', {
            method: 'GET',
            headers: this.getHeaders()
        });
    }

    /**
     * Mock data for development and testing when backend is unavailable
     * @param {string} endpoint - API endpoint
     * @returns {Object} - Mock data
     */
    getMockData(endpoint) {
        if (endpoint.includes('/courses/')) {
            return {
                id: 1,
                title: "CompTIA Security+ Certification",
                description: "Complete preparation for the Security+ exam with hands-on labs and practice tests.",
                image_url: "assets/images/course-security-plus.jpg",
                duration: 120,
                difficulty: "intermediate",
                price: 199.99,
                instructor_id: 2,
                certification_type: "Security+",
                modules: [
                    { id: 1, title: "Security Fundamentals", order: 1 },
                    { id: 2, title: "Network Security", order: 2 },
                    { id: 3, title: "Identity Management", order: 3 },
                ]
            };
        }

        if (endpoint === '/users/me') {
            return {
                id: 1,
                email: "student@example.com",
                first_name: "Demo",
                last_name: "Student",
                role: "student",
                is_active: true
            };
        }

        if (endpoint === '/enrollments/') {
            return [
                { id: 1, user_id: 1, course_id: 1, status: "active", enrollment_date: "2023-06-01" },
                { id: 2, user_id: 1, course_id: 2, status: "completed", enrollment_date: "2023-04-15" }
            ];
        }

        return null;
    }
}

// Export as default
const api = new ApiService();
export default api;