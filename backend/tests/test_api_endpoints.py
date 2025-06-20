import requests
import json
import sys
from time import sleep

class APITester:
    def __init__(self, base_url="http://127.0.0.1:8000/api/v1"):
        self.base_url = base_url
        self.access_token = None
        self.admin_token = None
        self.instructor_token = None
        self.student_token = None
        self.created_ids = {
            "user": None,
            "course": None,
            "module": None,
            "lesson": None,
            "enrollment": None,
            "assessment": None,
            "topic": None,
            "reply": None
        }

    def make_request(self, method, endpoint, data=None, auth_token=None, params=None):
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == "PUT":
                response = requests.put(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, None, f"Unsupported method: {method}"

            if response.status_code < 400:
                return True, response, None
            else:
                return False, response, f"Error {response.status_code}: {response.text}"

        except Exception as e:
            return False, None, str(e)

    def print_section(self, title):
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80)

    def log_result(self, endpoint, method, status_code, success, error=None):
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status} | {method} {endpoint} | Status: {status_code}")
        if error and not success:
            print(f"  Error: {error}")

    def log_skipped(self, endpoint, method, reason):
        print(f"⏩ SKIPPED | {method} {endpoint} | Reason: {reason}")

    def setup_users(self):
        self.print_section("Setting up test users")

        # Try to register and login admin user
        self.register_and_login_user(
            email="admin@example.com",
            password="adminPassword123!",
            first_name="Admin",
            last_name="User",
            role="admin",
            token_attribute="admin_token"
        )

        # Try to register and login instructor user
        self.register_and_login_user(
            email="instructor@example.com",
            password="instructorPassword123!",
            first_name="Instructor",
            last_name="User",
            role="instructor",
            token_attribute="instructor_token"
        )

        # Try to register and login student user
        self.register_and_login_user(
            email="student@example.com",
            password="studentPassword123!",
            first_name="Student",
            last_name="User",
            role="student",
            token_attribute="student_token"
        )

        # Set default access token
        if self.student_token:
            self.access_token = self.student_token

    def register_and_login_user(self, email, password, first_name, last_name, role, token_attribute):
        # First try to login
        login_data = {
            "username": email,
            "password": password
        }

        success, response, error = self.make_request("POST", "/users/login", data=login_data)

        if success and response:
            # Login successful, store token
            token = response.json().get("access_token")
            setattr(self, token_attribute, token)
            self.log_result(f"/users/login ({role})", "POST", response.status_code, True)
            return

        # If login failed, try to register
        register_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "role": role
        }

        success, response, error = self.make_request("POST", "/users/register", data=register_data)

        if success:
            self.log_result(f"/users/register ({role})", "POST", response.status_code, True)
        elif "user with this email already exists" in str(error):
            # User exists but login failed - likely wrong password in test
            self.log_result(f"/users/register ({role})", "POST",
                            response.status_code if response else None,
                            False, "User exists but couldn't login")
        else:
            self.log_result(f"/users/register ({role})", "POST",
                            response.status_code if response else None,
                            False, error)
            return

        # Try login again after registration
        success, response, error = self.make_request("POST", "/users/login", data=login_data)

        if success and response:
            token = response.json().get("access_token")
            setattr(self, token_attribute, token)
            self.log_result(f"/users/login ({role})", "POST", response.status_code, True)
        else:
            self.log_result(f"/users/login ({role})", "POST",
                            response.status_code if response else None,
                            False, error)

    def test_user_endpoints(self):
        self.print_section("Testing User Management Endpoints")

        # Skip tests if student token is missing
        if not self.student_token:
            self.log_skipped("User Management Endpoints", "ALL", "No student token available")
            return

        # 1. Get current user profile
        success, response, error = self.make_request("GET", "/users/me", auth_token=self.student_token)
        self.log_result("/users/me", "GET", response.status_code if response else None, success, error)

        # 2. Update current user profile
        user_update = {
            "first_name": "Updated",
            "last_name": "Student"
        }
        success, response, error = self.make_request("PUT", "/users/me", data=user_update, auth_token=self.student_token)
        self.log_result("/users/me", "PUT", response.status_code if response else None, success, error)

        # Skip admin tests if admin token is missing
        if not self.admin_token:
            self.log_skipped("Admin User Endpoints", "ALL", "No admin token available")
            return

        # 3. Get all users (admin only)
        success, response, error = self.make_request("GET", "/users/", auth_token=self.admin_token)
        self.log_result("/users/", "GET", response.status_code if response else None, success, error)

        if success and response:
            # Save a user ID for further tests
            users = response.json()
            if users and len(users) > 0:
                self.created_ids["user"] = users[0].get("id")

        # 4. Get specific user (admin only)
        if self.created_ids["user"]:
            success, response, error = self.make_request("GET", f"/users/{self.created_ids['user']}", auth_token=self.admin_token)
            self.log_result(f"/users/{self.created_ids['user']}", "GET",
                            response.status_code if response else None, success, error)

            # 5. Update specific user (admin only)
            user_update = {
                "first_name": "Admin",
                "last_name": "Updated"
            }
            success, response, error = self.make_request("PUT", f"/users/{self.created_ids['user']}",
                                                         data=user_update, auth_token=self.admin_token)
            self.log_result(f"/users/{self.created_ids['user']}", "PUT",
                            response.status_code if response else None, success, error)

            # 6. Delete user - skip to preserve test users
            self.log_skipped(f"/users/{self.created_ids['user']}", "DELETE", "Preserving test user")
        else:
            self.log_skipped("User endpoints", "GET/PUT/DELETE", "No user ID available")

    def test_course_endpoints(self):
        self.print_section("Testing Course Management Endpoints")

        # 1. Create a new course (instructor/admin only)
        auth_token = self.instructor_token if self.instructor_token else self.admin_token
        if not auth_token:
            self.log_skipped("Course endpoints", "ALL", "No instructor or admin token available")
            return

        course_data = {
            "title": "Security+ Certification",
            "description": "Prepare for CompTIA Security+ certification",
            "certification_type": "Security+",
            "difficulty_level": "intermediate",
            "estimated_duration": 40,
            "is_published": True
        }

        success, response, error = self.make_request("POST", "/courses/",
                                                     data=course_data, auth_token=auth_token)

        if success and response:
            self.log_result("/courses/", "POST", response.status_code, True)
            course_id = response.json().get("id")
            print(f"Created course with ID: {course_id}")
            self.created_ids["course"] = course_id
        else:
            self.log_result("/courses/", "POST", response.status_code if response else None, False,
                            error if error else "Failed to create course")

        # 2. Get all courses
        success, response, error = self.make_request("GET", "/courses/", auth_token=self.access_token)
        self.log_result("/courses/", "GET", response.status_code if response else None, success, error)

        # Skip the rest if course creation failed
        if not self.created_ids["course"]:
            self.log_skipped("Remaining course endpoints", "ALL", "Course creation failed")
            return

        # 3. Get specific course
        success, response, error = self.make_request("GET", f"/courses/{self.created_ids['course']}",
                                                     auth_token=self.access_token)
        self.log_result(f"/courses/{self.created_ids['course']}", "GET",
                        response.status_code if response else None, success, error)

        # 4. Update course
        course_update = {
            "title": "Updated Security+ Course",
            "description": "Updated description for Security+ certification"
        }
        success, response, error = self.make_request("PUT", f"/courses/{self.created_ids['course']}",
                                                     data=course_update, auth_token=auth_token)
        self.log_result(f"/courses/{self.created_ids['course']}", "PUT",
                        response.status_code if response else None, success, error)

        # 5. Create a module
        module_data = {
            "title": "Introduction to Cybersecurity",
            "description": "Fundamental concepts of cybersecurity",
            "order_index": 1
        }
        success, response, error = self.make_request("POST", f"/courses/{self.created_ids['course']}/modules",
                                                     data=module_data, auth_token=auth_token)

        if success and response:
            self.log_result(f"/courses/{self.created_ids['course']}/modules", "POST", response.status_code, True)
            module_id = response.json().get("id")
            print(f"Created module with ID: {module_id}")
            self.created_ids["module"] = module_id
        else:
            self.log_result(f"/courses/{self.created_ids['course']}/modules", "POST",
                            response.status_code if response else None, False,
                            error if error else "Failed to create module")

        # 6. Get course modules
        success, response, error = self.make_request("GET", f"/courses/{self.created_ids['course']}/modules",
                                                     auth_token=self.access_token)
        self.log_result(f"/courses/{self.created_ids['course']}/modules", "GET",
                        response.status_code if response else None, success, error)

        # Skip lesson tests if module creation failed
        if not self.created_ids["module"]:
            self.log_skipped("Lesson endpoints", "ALL", "Module creation failed")
            return

        # 7. Create a lesson
        lesson_data = {
            "title": "Cybersecurity Basics",
            "content_type": "text",
            "content": "This is the content of the lesson about cybersecurity basics.",
            "order_index": 1
        }
        success, response, error = self.make_request("POST", f"/modules/{self.created_ids['module']}/lessons",
                                                     data=lesson_data, auth_token=auth_token)

        if success and response:
            self.log_result(f"/modules/{self.created_ids['module']}/lessons", "POST", response.status_code, True)
            lesson_id = response.json().get("id")
            print(f"Created lesson with ID: {lesson_id}")
            self.created_ids["lesson"] = lesson_id
        else:
            self.log_result(f"/modules/{self.created_ids['module']}/lessons", "POST",
                            response.status_code if response else None, False,
                            error if error else "Failed to create lesson")

        # 8. Get module lessons
        success, response, error = self.make_request("GET", f"/modules/{self.created_ids['module']}/lessons",
                                                     auth_token=self.access_token)
        self.log_result(f"/modules/{self.created_ids['module']}/lessons", "GET",
                        response.status_code if response else None, success, error)

        # 9. Delete course - skip to preserve for other tests
        self.log_skipped(f"/courses/{self.created_ids['course']}", "DELETE",
                         "Skipping deletion to preserve test course")

    def test_enrollment_endpoints(self):
        self.print_section("Testing Enrollment Endpoints")

        # Need a course to enroll in
        if not self.created_ids["course"]:
            self.log_skipped("Enrollment endpoints", "ALL", "No course available")
            return

        # Need student token for enrollment
        if not self.student_token:
            self.log_skipped("Enrollment endpoints", "ALL", "No student token available")
            return

        # 1. Enroll in a course
        enrollment_data = {
            "course_id": self.created_ids["course"]
        }

        success, response, error = self.make_request("POST", "/enrollments/",
                                                     data=enrollment_data, auth_token=self.student_token)

        if success and response:
            self.log_result("/enrollments/", "POST", response.status_code, True)
            enrollment_id = response.json().get("id")
            print(f"Created enrollment with ID: {enrollment_id}")
            self.created_ids["enrollment"] = enrollment_id
        else:
            self.log_result("/enrollments/", "POST",
                            response.status_code if response else None, False,
                            error if error else "Failed to create enrollment")

        # 2. Get user enrollments
        success, response, error = self.make_request("GET", "/enrollments/", auth_token=self.student_token)
        self.log_result("/enrollments/", "GET", response.status_code if response else None, success, error)

        # Skip the rest if enrollment creation failed
        if not self.created_ids["enrollment"]:
            self.log_skipped("Remaining enrollment endpoints", "ALL", "Enrollment creation failed")
            return

        # 3. Get enrollment details
        success, response, error = self.make_request("GET", f"/enrollments/{self.created_ids['enrollment']}",
                                                     auth_token=self.student_token)
        self.log_result(f"/enrollments/{self.created_ids['enrollment']}", "GET",
                        response.status_code if response else None, success, error)

        # 4. Update enrollment status
        enrollment_update = {
            "status": "completed"
        }
        success, response, error = self.make_request("PUT", f"/enrollments/{self.created_ids['enrollment']}",
                                                     data=enrollment_update, auth_token=self.student_token)
        self.log_result(f"/enrollments/{self.created_ids['enrollment']}", "PUT",
                        response.status_code if response else None, success, error)

        # 5. Delete enrollment (withdraw from course)
        success, response, error = self.make_request("DELETE", f"/enrollments/{self.created_ids['enrollment']}",
                                                     auth_token=self.student_token)
        self.log_result(f"/enrollments/{self.created_ids['enrollment']}", "DELETE",
                        response.status_code if response else None, success, error)

    def test_assessment_endpoints(self):
        self.print_section("Testing Assessment Endpoints")

        # Need instructor/admin privileges and a course
        if not self.instructor_token and not self.admin_token:
            self.log_skipped("Assessment endpoints", "ALL", "No instructor or admin token available")
            return

        if not self.created_ids["course"]:
            self.log_skipped("Assessment endpoints", "ALL", "No course available")
            return

        auth_token = self.instructor_token if self.instructor_token else self.admin_token

        # 1. Create a new assessment
        assessment_data = {
            "title": "Security+ Module 1 Quiz",
            "description": "Test your knowledge of basic security concepts",
            "course_id": self.created_ids["course"],
            "time_limit_minutes": 30,
            "passing_score": 70,
            "questions": [
                {
                    "text": "What is the primary goal of confidentiality in the CIA triad?",
                    "options": [
                        "Ensuring data is not modified",
                        "Ensuring data is available when needed",
                        "Preventing unauthorized access to data",
                        "Verifying the sender of data"
                    ],
                    "correct_option_index": 2,
                    "points": 10
                },
                {
                    "text": "Which of the following is an example of a technical control?",
                    "options": [
                        "Security policy",
                        "Firewall",
                        "Security awareness training",
                        "Physical barriers"
                    ],
                    "correct_option_index": 1,
                    "points": 10
                }
            ]
        }

        success, response, error = self.make_request("POST", "/assessments/",
                                                     data=assessment_data, auth_token=auth_token)

        if success and response:
            self.log_result("/assessments/", "POST", response.status_code, True)
            assessment_id = response.json().get("id")
            print(f"Created assessment with ID: {assessment_id}")
            self.created_ids["assessment"] = assessment_id
        else:
            self.log_result("/assessments/", "POST",
                            response.status_code if response else None, False,
                            error if error else "Failed to create assessment")

        # 2. Get all assessments
        success, response, error = self.make_request("GET", "/assessments/", auth_token=self.student_token)
        self.log_result("/assessments/", "GET", response.status_code if response else None, success, error)

        # Skip the rest if assessment creation failed
        if not self.created_ids["assessment"]:
            self.log_skipped("Remaining assessment endpoints", "ALL", "Assessment creation failed")
            return

        # 3. Get specific assessment
        success, response, error = self.make_request("GET", f"/assessments/{self.created_ids['assessment']}",
                                                     auth_token=self.student_token)
        self.log_result(f"/assessments/{self.created_ids['assessment']}", "GET",
                        response.status_code if response else None, success, error)

        # 4. Update assessment
        assessment_update = {
            "title": "Updated Security+ Quiz",
            "description": "Updated quiz description"
        }
        success, response, error = self.make_request("PUT", f"/assessments/{self.created_ids['assessment']}",
                                                     data=assessment_update, auth_token=auth_token)
        self.log_result(f"/assessments/{self.created_ids['assessment']}", "PUT",
                        response.status_code if response else None, success, error)

        # 5. Start an assessment
        success, response, error = self.make_request("POST", f"/assessments/{self.created_ids['assessment']}/take",
                                                     auth_token=self.student_token)
        self.log_result(f"/assessments/{self.created_ids['assessment']}/take", "POST",
                        response.status_code if response else None, success, error)

        # 6. Submit assessment answers
        submit_data = {
            "answers": [
                {"question_index": 0, "selected_option_index": 2},
                {"question_index": 1, "selected_option_index": 1}
            ]
        }
        success, response, error = self.make_request("POST", f"/assessments/{self.created_ids['assessment']}/submit",
                                                     data=submit_data, auth_token=self.student_token)
        self.log_result(f"/assessments/{self.created_ids['assessment']}/submit", "POST",
                        response.status_code if response else None, success, error)

        # 7. Delete assessment - skip to preserve for other tests
        self.log_skipped(f"/assessments/{self.created_ids['assessment']}", "DELETE",
                         "Skipping deletion to preserve test assessment")

    def test_forum_endpoints(self):
        self.print_section("Testing Forum Endpoints")

        # Need student token for forum
        if not self.student_token:
            self.log_skipped("Forum endpoints", "ALL", "No student token available")
            return

        # 1. Create a new forum topic
        topic_data = {
            "title": "Security+ Certification Tips",
            "content": "What are your best tips for passing the Security+ exam?"
        }

        success, response, error = self.make_request("POST", "/forums/topics",
                                                     data=topic_data, auth_token=self.student_token)

        if success and response:
            self.log_result("/forums/topics", "POST", response.status_code, True)
            topic_id = response.json().get("id")
            print(f"Created forum topic with ID: {topic_id}")
            self.created_ids["topic"] = topic_id
        else:
            self.log_result("/forums/topics", "POST",
                            response.status_code if response else None, False,
                            error if error else "Failed to create forum topic")

        # 2. Get all forum topics
        success, response, error = self.make_request("GET", "/forums/topics", auth_token=self.access_token)
        self.log_result("/forums/topics", "GET", response.status_code if response else None, success, error)

        # Skip the rest if topic creation failed
        if not self.created_ids["topic"]:
            self.log_skipped("Remaining forum endpoints", "ALL", "Forum topic creation failed")
            return

        # 3. Get specific forum topic
        success, response, error = self.make_request("GET", f"/forums/topics/{self.created_ids['topic']}",
                                                     auth_token=self.access_token)
        self.log_result(f"/forums/topics/{self.created_ids['topic']}", "GET",
                        response.status_code if response else None, success, error)

        # Need instructor token for reply
        if not self.instructor_token:
            self.log_skipped("Forum reply endpoint", "POST", "No instructor token available")
            return

        # 4. Add reply to a forum topic
        reply_data = {
            "content": "I recommend taking practice exams and focusing on hands-on labs."
        }
        success, response, error = self.make_request("POST", f"/forums/topics/{self.created_ids['topic']}/replies",
                                                     data=reply_data, auth_token=self.instructor_token)
        self.log_result(f"/forums/topics/{self.created_ids['topic']}/replies", "POST",
                        response.status_code if response else None, success, error)

    def test_progress_endpoints(self):
        self.print_section("Testing Progress Tracking Endpoints")

        # Need a course, module, and lesson
        if not self.created_ids["course"] or not self.created_ids["lesson"]:
            self.log_skipped("Progress endpoints", "ALL", "No course or lesson available")
            return

        # Need student token for progress
        if not self.student_token:
            self.log_skipped("Progress endpoints", "ALL", "No student token available")
            return

        # 1. Mark lesson as complete
        success, response, error = self.make_request("POST", f"/progress/lessons/{self.created_ids['lesson']}",
                                                     auth_token=self.student_token)
        self.log_result(f"/progress/lessons/{self.created_ids['lesson']}", "POST",
                        response.status_code if response else None, success, error)

        # 2. Get user progress in a course
        success, response, error = self.make_request("GET", f"/progress/courses/{self.created_ids['course']}",
                                                     auth_token=self.student_token)
        self.log_result(f"/progress/courses/{self.created_ids['course']}", "GET",
                        response.status_code if response else None, success, error)

        # 3. Get user assessment results
        success, response, error = self.make_request("GET", "/progress/assessments", auth_token=self.student_token)
        self.log_result("/progress/assessments", "GET", response.status_code if response else None, success, error)

    def run_all_tests(self):
        print("Starting API Endpoint Tests...")
        print(f"Base URL: {self.base_url}")

        try:
            # Setup test users and tokens
            self.setup_users()
            sleep(1)  # Short pause between test sections

            # Run all endpoint tests
            self.test_user_endpoints()
            sleep(1)

            self.test_course_endpoints()
            sleep(1)

            self.test_enrollment_endpoints()
            sleep(1)

            self.test_assessment_endpoints()
            sleep(1)

            self.test_forum_endpoints()
            sleep(1)

            self.test_progress_endpoints()

            # Summary
            self.print_section("Test Summary")
            print("API Testing completed.")
            print(f"Created entities IDs: {json.dumps(self.created_ids, indent=2)}")

        except Exception as e:
            print(f"Error running tests: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api/v1"
    tester = APITester(base_url)
    tester.run_all_tests()