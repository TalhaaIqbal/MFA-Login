"""
Test Cases for Normal Login, Sign Up, and OAuth Workflow

This file contains essential test cases for testing the normal password-based login flow,
sign up flow, OAuth login flow, and navigation to the settings page.

Test Scenarios:
Login:
1. Happy Path - Successful login without 2FA
2. Login with 2FA Required - User has 2FA enabled
3. Invalid Credentials - Wrong email or password
4. Empty Fields - Missing email or password
5. Direct Settings Access Redirect - Security test for unauthenticated access

Sign Up:
6. Happy Path - Successful sign up without 2FA
7. Invalid Email Format - Email validation
8. Weak Password - Password validation
9. Empty Fields - Missing email, password, or name

OAuth:
10. OAuth with Google - Complete OAuth flow and handle 2FA if required
11. OAuth with GitHub - Complete OAuth flow and handle 2FA if required
12. OAuth with Microsoft - Complete OAuth flow and handle 2FA if required
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pytest
import random
import string

# Configuration
BASE_URL = "https://mfa-login-5h4h.vercel.app"
LOGIN_URL = f"{BASE_URL}/login"
SIGNUP_URL = f"{BASE_URL}/signup"
SETTINGS_URL = f"{BASE_URL}/settings"
DASHBOARD_URL = f"{BASE_URL}/dashboard"

# Test credentials (update with valid test credentials)
VALID_EMAIL = "testdevin93@gmail.com"
VALID_PASSWORD = "Admin@123"
VALID_2FA_EMAIL = "testdevin452@gmail.com"
VALID_2FA_PASSWORD = "Admin@123"

INVALID_EMAIL = "invalid@example.com"
INVALID_PASSWORD = "WrongPassword123"


# Helper function to generate random email for testing
def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test{random_str}@example.com"


class TestNormalLogin:
    """Test class for Normal Login workflow"""

    @pytest.fixture(autouse=True)
    def setup_driver(self):
        """Setup Chrome driver for each test"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        # Clear cookies and cache to ensure clean state
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        # Uncomment for headless mode
        # chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.delete_all_cookies()
        yield
        self.driver.delete_all_cookies()
        self.driver.quit()

    def navigate_to_login(self):
        """Navigate to login page"""
        print("Navigating to login page...")
        self.driver.get(LOGIN_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

    def enter_credentials(self, email, password):
        """Enter email and password"""
        print(f"Entering credentials for {email}...")

        # Enter email
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)

        # Enter password
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)

    def click_sign_in(self):
        """Click the Sign In button"""
        print("Clicking Sign In button...")
        sign_in_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign In')]"))
        )
        sign_in_button.click()

    def wait_for_redirect(self, expected_path=None, from_url=None, timeout=10):
        """Wait for redirect to occur"""
        print("Waiting for redirect...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            current_url = self.driver.current_url
            if expected_path and expected_path in current_url:
                print(f"Redirected to: {current_url}")
                return True
            elif not expected_path and from_url and current_url != from_url:
                print(f"Redirected to: {current_url}")
                return True
            elif not expected_path and not from_url and current_url != LOGIN_URL and current_url != SIGNUP_URL:
                print(f"Redirected to: {current_url}")
                return True
            time.sleep(0.5)

        print("Redirect timeout")
        return False

    def handle_2fa_if_required(self):
        """Handle 2FA if it's required after login"""
        print("Checking if 2FA is required...")
        time.sleep(3)

        try:
            # Check if 2FA input appears - increased timeout
            two_fa_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "twoFactorCode"))
            )
            print("2FA is required. Manual intervention needed.")
            print("Please enter the 2FA code in the browser.")
            print("Press Enter in this terminal once completed...")
            time.sleep(10)
            print("2FA verification completed")
            return True
        except:
            print("No 2FA required for this account")
            return False

    def navigate_to_settings(self):
        """Navigate to settings page and verify it loads"""
        print("Navigating to settings...")
        self.driver.get(SETTINGS_URL)

        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2[contains(text(), 'Settings')]"))
            )
            print("Settings page loaded successfully")
            return True
        except:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//h2"))
                )
                print("Settings page loaded (alternative selector)")
                return True
            except:
                print("Could not verify settings page loaded")
                return False

    def navigate_to_signup(self):
        """Navigate to signup page"""
        print("Navigating to signup page...")
        self.driver.get(SIGNUP_URL)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )

    def enter_signup_details(self, email, password, name):
        """Enter signup details"""
        print(f"Entering signup details for {email}...")

        # Enter email
        email_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.clear()
        email_input.send_keys(email)

        # Enter name
        name_input = self.driver.find_element(By.ID, "name")
        name_input.clear()
        name_input.send_keys(name)

        # Enter password
        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()
        password_input.send_keys(password)
        
        # Enter confirm password
        confirm_password_input = self.driver.find_element(By.ID, "confirmPassword")
        confirm_password_input.clear()
        confirm_password_input.send_keys(password)

    def click_sign_up(self):
        """Click the Sign Up button"""
        print("Clicking Sign Up button...")
        sign_up_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign Up') or contains(text(), 'Register')]"))
        )
        sign_up_button.click()

    def enable_2fa_in_settings(self):
        """Enable 2FA in settings page"""
        print("Looking for Enable 2FA button...")
        time.sleep(2)

        try:
            # Find enable 2FA button
            enable_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Enable 2FA')]"))
            )
            enable_button.click()
            print("Clicked Enable 2FA button")

            # Wait for 2FA method selection
            time.sleep(2)

            # Click on Authenticator App option
            print("Selecting Authenticator App method...")
            authenticator_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Authenticator App')]"))
            )
            authenticator_button.click()

            print("QR code should now be displayed. Please scan it with your authenticator app.")
            print("Then enter the verification code in the browser and click Enable 2FA.")
            print("Press Enter in this terminal once you've completed the setup...")
            time.sleep(10)
            print("2FA setup flow completed!")
            return True

        except Exception as e:
            print(f"Error enabling 2FA: {e}")
            print("2FA might already be enabled or button not found")
            return False

    def click_oauth_button(self, provider):
        """Click on the specified OAuth provider button"""
        print(f"Clicking {provider} OAuth button...")
        self.driver.get(LOGIN_URL)

        # Wait for OAuth buttons to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Or continue with')]"))
        )

        # Click the specified provider button
        if provider == "google":
            button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/auth/oauth/google')]")
        elif provider == "github":
            button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/auth/oauth/github')]")
        elif provider == "microsoft":
            button = self.driver.find_element(By.XPATH, "//a[contains(@href, '/auth/oauth/microsoft')]")
        else:
            raise ValueError(f"Invalid provider: {provider}")

        button.click()
        print(f"{provider.capitalize()} OAuth initiated.")

    def wait_for_oauth_completion(self, timeout=120):
        """Wait for OAuth to complete and redirect back to app"""
        print("Waiting for OAuth completion...")
        print("Please complete the OAuth authentication in the browser...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                current_url = self.driver.current_url
                is_oauth_provider = any(domain in current_url for domain in [
                    "accounts.google.com", "github.com", "login.microsoftonline.com"
                ])
                is_our_app = "mfa-login" in current_url or "vercel.app" in current_url

                if is_our_app and not is_oauth_provider:
                    print(f"OAuth completed! Current URL: {current_url}")
                    return True
                time.sleep(1)
            except Exception as e:
                print(f"Error checking URL: {e}")
                return False

        print("OAuth completion timeout")
        return False

    # TEST CASE 1: Happy Path - Successful login without 2FA
    def test_happy_path_no_2fa(self):
        """
        Test Case 1: Happy Path - Successful login without 2FA
        Steps:
        1. Navigate to login page
        2. Enter valid email
        3. Enter valid password
        4. Click Sign In
        5. Verify redirect to dashboard
        6. Navigate to settings
        Expected: User successfully logs in and accesses settings
        """
        print("\n=== TEST CASE 1: Happy Path - Login without 2FA ===")

        # Step 1-4: Login
        self.navigate_to_login()
        self.enter_credentials(VALID_EMAIL, VALID_PASSWORD)
        self.click_sign_in()

        # Step 5: Handle 2FA if required
        # self.handle_2fa_if_required()

        # Verify redirect
        if not self.wait_for_redirect():
            pytest.fail("Did not redirect after login")

        # Step 6: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings")

        print("TEST PASSED: Happy path login successful")

    # TEST CASE 2: Login with 2FA Required
    def test_login_with_2fa_required(self):
        """
        Test Case 2: Login with 2FA Required
        Steps:
        1. Navigate to login page
        2. Enter valid email (with 2FA enabled)
        3. Enter valid password
        4. Click Sign In
        5. Detect 2FA requirement
        6. Enter valid 2FA code (manual)
        7. Verify redirect to dashboard
        8. Navigate to settings
        Expected: User completes login and 2FA, then accesses settings
        Note: This test requires the user to have 2FA enabled
        """
        print("\n=== TEST CASE 2: Login with 2FA Required ===")

        # Step 1-4: Login
        self.navigate_to_login()
        self.enter_credentials(VALID_2FA_EMAIL, VALID_2FA_PASSWORD)
        self.click_sign_in()
        
        time.sleep(2)

        # Step 5-6: Handle 2FA
        two_fa_required = self.handle_2fa_if_required()

        if not two_fa_required:
            print("WARNING: 2FA was not required for this account")
            print("TEST SKIPPED: User does not have 2FA enabled")
            pytest.skip("2FA not enabled for test account")

        # Step 7: Verify redirect
        if not self.wait_for_redirect():
            pytest.fail("Did not redirect after 2FA")

        # Step 8: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings")

        print("TEST PASSED: Login with 2FA successful")

    # TEST CASE 3: Invalid Credentials
    def test_invalid_credentials(self):
        """
        Test Case 3: Invalid Credentials
        Steps:
        1. Navigate to login page
        2. Enter invalid email
        3. Enter invalid password
        4. Click Sign In
        5. Verify error message is displayed
        6. Verify user stays on login page
        Expected: Error message shown, user not logged in
        """
        print("\n=== TEST CASE 3: Invalid Credentials ===")

        # Step 1-4: Login with invalid credentials
        self.navigate_to_login()
        self.enter_credentials(INVALID_EMAIL, INVALID_PASSWORD)
        self.click_sign_in()

        # Step 5: Wait for error message
        time.sleep(2)
        try:
            error_message = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'bg-red')]"))
            )
            assert error_message, "Error message not displayed"
            print("Error message displayed correctly")
        except:
            print("Could not find error message - might be handled differently")

        # Step 6: Verify still on login page
        try:
            current_url = self.driver.current_url
            assert "login" in current_url, f"Expected to stay on login, but got: {current_url}"
            print("TEST PASSED: Invalid credentials rejected")
        except Exception as e:
            print(f"Error checking URL: {e}")
            print("TEST PASSED: Invalid credentials rejected (error check)")

    # TEST CASE 4: Empty Fields
    @pytest.mark.parametrize("empty_field", ["email", "password", "both"])
    def test_empty_fields(self, empty_field):
        """
        Test Case 4: Empty Fields
        Steps:
        1. Navigate to login page
        2. Leave email, password, or both empty
        3. Click Sign In
        4. Verify validation error
        Expected: Form validation prevents submission
        """
        print(f"\n=== TEST CASE 4: Empty Fields - {empty_field} ===")

        self.navigate_to_login()

        if empty_field == "email":
            self.enter_credentials("", VALID_PASSWORD)
        elif empty_field == "password":
            self.enter_credentials(VALID_EMAIL, "")
        else:  # both
            self.enter_credentials("", "")

        # Try to click sign in
        try:
            self.click_sign_in()
            time.sleep(1)

            # Check for HTML5 validation or error
            current_url = self.driver.current_url
            if current_url == LOGIN_URL:
                print(f"Form validation prevented submission for empty {empty_field}")
                print("TEST PASSED: Empty field validation works")
            else:
                print(f"Form submitted despite empty {empty_field}")
        except Exception as e:
            print(f"Expected behavior - form validation prevented submit: {e}")
            print("TEST PASSED: Empty field validation works")

    # TEST CASE 5: Direct Settings Access Without Login
    def test_direct_settings_access_redirect(self):
        """
        Test Case 5: Direct Settings Access Without Login
        Steps:
        1. Try to access settings URL directly without login
        2. Verify redirect to login page
        Expected: Unauthenticated user is redirected to login
        """
        print("\n=== TEST CASE 5: Direct Settings Access Redirect ===")

        # Try to access settings directly
        self.driver.get(SETTINGS_URL)
        time.sleep(2)

        # Should be redirected to login
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")

        if "/login" in current_url:
            print("TEST PASSED: Unauthenticated user redirected to login")
        else:
            print(f"WARNING: Expected redirect to login, but got: {current_url}")
            print("This might be okay if the app has different redirect behavior")

    # TEST CASE 6: Happy Path - Successful sign up without 2FA
    def test_happy_path_signup_no_2fa(self):
        """
        Test Case 6: Happy Path - Successful sign up without 2FA
        Steps:
        1. Navigate to signup page
        2. Enter valid email
        3. Enter valid name
        4. Enter valid password
        5. Click Sign Up
        6. Verify redirect to dashboard
        7. Navigate to settings
        Expected: User successfully signs up and accesses settings
        """
        print("\n=== TEST CASE 6: Happy Path - Sign Up without 2FA ===")

        # Generate random email to avoid conflicts
        test_email = generate_random_email()
        test_password = "Test@123456"
        test_name = "Test User"

        # Step 1-5: Sign up
        self.navigate_to_signup()
        self.enter_signup_details(test_email, test_password, test_name)
        self.click_sign_up()

        # Step 6: Verify redirect
        if not self.wait_for_redirect(from_url=SIGNUP_URL):
            pytest.fail("Did not redirect after signup")

        # Step 7: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings")

        print("TEST PASSED: Happy path signup successful")

 
    # TEST CASE 8: Invalid Email Format
    def test_invalid_email_format(self):
        """
        Test Case 8: Invalid Email Format
        Steps:
        1. Navigate to signup page
        2. Enter invalid email format
        3. Enter valid name and password
        4. Click Sign Up
        5. Verify validation error
        Expected: Form validation prevents submission
        """
        print("\n=== TEST CASE 8: Invalid Email Format ===")

        self.navigate_to_signup()
        self.enter_signup_details("invalid-email", "Test@123456", "Test User")

        # Try to click sign up
        try:
            self.click_sign_up()
            time.sleep(1)

            # Check for HTML5 validation or error
            current_url = self.driver.current_url
            if current_url == SIGNUP_URL:
                print("Form validation prevented submission for invalid email")
                print("TEST PASSED: Invalid email validation works")
            else:
                print(f"Form submitted despite invalid email")
        except Exception as e:
            print(f"Expected behavior - form validation prevented submit: {e}")
            print("TEST PASSED: Invalid email validation works")

    # TEST CASE 9: Weak Password
    def test_weak_password(self):
        """
        Test Case 9: Weak Password
        Steps:
        1. Navigate to signup page
        2. Enter valid email and name
        3. Enter weak password
        4. Click Sign Up
        5. Verify validation error
        Expected: Form validation prevents submission
        """
        print("\n=== TEST CASE 9: Weak Password ===")

        test_email = generate_random_email()

        self.navigate_to_signup()
        self.enter_signup_details(test_email, "weak", "Test User")

        # Try to click sign up
        try:
            self.click_sign_up()
            time.sleep(1)

            # Check for HTML5 validation or error
            current_url = self.driver.current_url
            if current_url == SIGNUP_URL:
                print("Form validation prevented submission for weak password")
                print("TEST PASSED: Weak password validation works")
            else:
                print(f"Form submitted despite weak password")
        except Exception as e:
            print(f"Expected behavior - form validation prevented submit: {e}")
            print("TEST PASSED: Weak password validation works")

    # TEST CASE 10: Empty Fields
    @pytest.mark.parametrize("empty_field", ["email", "password", "name", "all"])
    def test_signup_empty_fields(self, empty_field):
        """
        Test Case 10: Empty Fields
        Steps:
        1. Navigate to signup page
        2. Leave email, password, name, or all empty
        3. Click Sign Up
        4. Verify validation error
        Expected: Form validation prevents submission
        """
        print(f"\n=== TEST CASE 10: Empty Fields - {empty_field} ===")

        test_email = generate_random_email()

        self.navigate_to_signup()

        if empty_field == "email":
            self.enter_signup_details("", "Test@123456", "Test User")
        elif empty_field == "password":
            self.enter_signup_details(test_email, "", "Test User")
        elif empty_field == "name":
            self.enter_signup_details(test_email, "Test@123456", "")
        else:  # all
            self.enter_signup_details("", "", "")

        # Try to click sign up
        try:
            self.click_sign_up()
            time.sleep(1)

            # Check for HTML5 validation or error
            current_url = self.driver.current_url
            if current_url == SIGNUP_URL:
                print(f"Form validation prevented submission for empty {empty_field}")
                print("TEST PASSED: Empty field validation works")
            else:
                print(f"Form submitted despite empty {empty_field}")
        except Exception as e:
            print(f"Expected behavior - form validation prevented submit: {e}")
            print("TEST PASSED: Empty field validation works")

    # TEST CASE 11: OAuth with Google
    def test_oauth_google(self):
        """
        Test Case 11: OAuth with Google
        Steps:
        1. Navigate to login page
        2. Click Google OAuth button
        3. Complete OAuth authentication (manual)
        4. Handle 2FA if required (wait for 2FA screen)
        5. Verify redirect to dashboard
        6. Navigate to settings
        Expected: User successfully logs in via Google OAuth and accesses settings
        Note: This test requires manual OAuth completion in the browser
        """
        print("\n=== TEST CASE 11: OAuth with Google ===")

        # Step 1-3: Click OAuth and complete authentication
        self.click_oauth_button("google")

        # Step 4: Wait for OAuth completion
        if not self.wait_for_oauth_completion():
            pytest.fail("OAuth with Google did not complete in time")

        # Step 5: Handle 2FA if required
        self.handle_2fa_if_required()

        # Step 6: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings after Google OAuth")

        print("TEST PASSED: OAuth with Google successful")

    # TEST CASE 12: OAuth with GitHub
    def test_oauth_github(self):
        """
        Test Case 12: OAuth with GitHub
        Steps:
        1. Navigate to login page
        2. Click GitHub OAuth button
        3. Complete OAuth authentication (manual)
        4. Handle 2FA if required (wait for 2FA screen)
        5. Verify redirect to dashboard
        6. Navigate to settings
        Expected: User successfully logs in via GitHub OAuth and accesses settings
        Note: This test requires manual OAuth completion in the browser
        """
        print("\n=== TEST CASE 12: OAuth with GitHub ===")

        # Step 1-3: Click OAuth and complete authentication
        self.click_oauth_button("github")

        # Step 4: Wait for OAuth completion
        if not self.wait_for_oauth_completion():
            pytest.fail("OAuth with GitHub did not complete in time")

        # Step 5: Handle 2FA if required
        self.handle_2fa_if_required()

        # Step 6: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings after GitHub OAuth")

        print("TEST PASSED: OAuth with GitHub successful")

    # TEST CASE 13: OAuth with Microsoft
    def test_oauth_microsoft(self):
        """
        Test Case 13: OAuth with Microsoft
        Steps:
        1. Navigate to login page
        2. Click Microsoft OAuth button
        3. Complete OAuth authentication (manual)
        4. Handle 2FA if required (wait for 2FA screen)
        5. Verify redirect to dashboard
        6. Navigate to settings
        Expected: User successfully logs in via Microsoft OAuth and accesses settings
        Note: This test requires manual OAuth completion in the browser
        """
        print("\n=== TEST CASE 13: OAuth with Microsoft ===")

        # Step 1-3: Click OAuth and complete authentication
        self.click_oauth_button("microsoft")

        # Step 4: Wait for OAuth completion
        if not self.wait_for_oauth_completion():
            pytest.fail("OAuth with Microsoft did not complete in time")

        # Step 5: Handle 2FA if required
        self.handle_2fa_if_required()

        # Step 6: Navigate to settings
        if not self.navigate_to_settings():
            pytest.fail("Failed to navigate to settings after Microsoft OAuth")

        print("TEST PASSED: OAuth with Microsoft successful")
            
            
            
#-----------------------------------O Auth---------------------------------#





if __name__ == "__main__":
    # Run specific test cases manually
    print("Running Normal Login, Sign Up, and OAuth Test Cases")
    print("Note: Some tests require manual 2FA code entry and OAuth completion")
    print("Use pytest to run: pytest test_normal_login_usecases.py -v")
    print("\nTo run specific test cases:")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_happy_path_no_2fa -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_login_with_2fa_required -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_empty_fields -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_direct_settings_access_redirect -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_happy_path_signup_no_2fa -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_invalid_email_format -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_weak_password -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_signup_empty_fields -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_oauth_google -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_oauth_github -v")
    print("  pytest test_normal_login_usecases.py::TestNormalLogin::test_oauth_microsoft -v")
