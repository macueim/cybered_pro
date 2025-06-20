#!/usr/bin/env python3
# tests/test_api_endpoints.py

import requests
import json
import sys
from urllib.parse import urljoin
import argparse
import time


class EndpointTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')  # Remove trailing slash if present
        self.api_prefix = "/api/v1"
        self.headers = {"Content-Type": "application/json"}
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
            "forum_topic": None
        }
        self.success_count = 0
        self.failure_count = 0
        self.skipped_count = 0

    def log_result(self, endpoint, method, status_code, success, message=None):
        result = "SUCCESS" if success else "FAILURE"
        output = f"[{result}] {method} {endpoint} - Status Code: {status_code}"
        if message:
            output += f" - {message}"

        if success:
            self.success_count += 1
            print(f"\033[92m{output}\033[0m")  # Green for success
        else:
            self.failure_count += 1
            print(f"\033[91m{output}\033[0m")  # Red for failure

        return success

    def log_skipped(self, endpoint, method, reason):
        self.skipped_count += 1
        output = f"[SKIPPED] {method} {endpoint} - {reason}"
        print(f"\033[93m{output}\033[0m")  # Yellow for skipped

    def make_request(self, method, endpoint, data=None, auth_token=None, expected_status=None, form_data=False):
        # Ensure endpoint starts with a slash
        if not endpoint.startswith('/'):
            endpoint = '/' + endpoint

        url = self.base_url + self.api_prefix + endpoint
        headers = self.headers.copy()

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        try:
            print(f"Making {method} request to {url}")
            if data:
                print(f"With data: {json.dumps(data, indent=2)}")

            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if form_data:
                    # For OAuth2 form-based authentication
                    response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return False, None, f"Unsupported method: {method}"

            # Debug information
            print(f"Response status: {response.status_code}")
            try:
                resp_json = response.json()
                print(f"Response JSON: {json.dumps(resp_json, indent=2)[:500]}")
            except:
                print(f"Response text: {response.text[:500]}")

            if expected_status and response.status_code != expected_status:
                return False, response, f"Expected status {expected_status}, got {response.status_code}"

            return response.status_code < 400, response, None

        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
            return False, None, str(e)

    def print_section(self, title):
        print("\n" + "=" * 80)
        print(f" {title} ".center(80, "="))
        print("=" * 80)

    def test_register_and_login(self):
        self.print_section("Testing User Registration and Login")

        # Try the basic endpoints first to ensure connectivity
        try:
            response = requests.get(f"{self.base_url}/ping")
            print(f"Ping test: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Ping test failed: {str(e)}")

        # 1. Register a user - match the user model structure from User class
        user_data = {
            "email": "admin@example.com",
            "password": "adminpassword",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }

        success, response, error = self.make_request("POST", "/users/register", data=user_data)
        if success and response:
            self.log_result("/users/register", "POST", response.status_code, True)
            user_id = response.json().get("id")
            print(f"Created user with ID: {user_id}")
            self.created_ids["user"] = user_id
        else:
            # If the first attempt failed, try with a UserCreate schema
            user_data_alt = {
                "email": "admin@example.com",
                "password": "adminpassword",
                "full_name": "Admin User",  # Some schemas use full_name instead of first/last
                "role": "admin"
            }

            success, response, error = self.make_request("POST", "/users/register", data=user_data_alt)
            self.log_result("/users/register", "POST", response.status_code if response else None,
                            success, "Using alternate schema" if success else error)

            if success and response:
                user_id = response.json().get("id")
                print(f"Created user with ID: {user_id}")
                self.created_ids["user"] = user_id

        # 2. Try multiple login approaches

        # Approach 1: FastAPI OAuth2 form data
        oauth2_data = {
            "username": "admin@example.com",
            "password": "adminpassword",
            "grant_type": "password"
        }

        success, response, error = self.make_request(
            "POST", "/auth/token", data=oauth2_data, form_data=True
        )

        if success and response:
            self.admin_token = response.json().get("access_token")
            self.log_result("/auth/token", "POST", response.status_code, True)
            print(f"Got token: {self.admin_token[:10]}...")
        else:
            print(f"OAuth2 token endpoint failed: {error}")

            # Approach 2: Direct login endpoint
            login_data = {
                "username": "admin@example.com",
                "password": "adminpassword"
            }

            success, response, error = self.make_request("POST", "/auth/login", data=login_data)

            if success and response:
                self.admin_token = response.json().get("access_token")
                self.log_result("/auth/login", "POST", response.status_code, True)
                print(f"Got token: {self.admin_token[:10]}...")
            else:
                # Approach 3: Custom login endpoint
                login_data = {
                    "email": "admin@example.com",
                    "password": "adminpassword"
                }

                success, response, error = self.make_request("POST", "/users/login", data=login_data)

                if success and response:
                    self.admin_token = response.json().get("access_token")
                    self.log_result("/users/login", "POST", response.status_code, True)
                    print(f"Got token: {self.admin_token[:10]}...")
                else:
                    self.log_result("All login attempts", "POST", None, False,
                                    "Failed to authenticate with any method")

        if self.admin_token:
            self.access_token = self.admin_token

    def run_test(self):
        """Run only the registration and login tests"""
        print("\n" + "=" * 80)
        print(" TESTING USER REGISTRATION AND LOGIN ".center(80, "="))
        print("=" * 80)

        try:
            self.test_register_and_login()

            print("\n" + "=" * 80)
            print(" TEST SUMMARY ".center(80, "="))
            print("=" * 80)
            print(f"Total Endpoints Tested: {self.success_count + self.failure_count + self.skipped_count}")
            print(f"Successful: {self.success_count}")
            print(f"Failed: {self.failure_count}")
            print(f"Skipped: {self.skipped_count}")
            print("=" * 80)

            return self.failure_count == 0

        except Exception as e:
            print(f"Error running tests: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test API endpoints")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL of the API server")
    args = parser.parse_args()

    tester = EndpointTester(base_url=args.url)
    success = tester.run_test()

    sys.exit(0 if success else 1)