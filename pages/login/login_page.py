from playwright.sync_api import expect


class LoginPage:

    def __init__(self, page):

        self.page = page

        self.username = page.get_by_test_id(
            "login-username"
        )

        self.password = page.get_by_test_id(
            "login-password"
        )

        self.login_btn = page.get_by_test_id(
            "login-submit"
        )

    def navigate(self, url):

        self.page.goto(url)

    def login(self, username, password):

        self.username.fill(username)
        self.password.fill(password)
        self.login_btn.click()

        self.page.wait_for_timeout(3000)

    def verify_login_success(self):

        current_url = self.page.url

        if "auth/login" in current_url:

            raise Exception(
                f"Login failed. Current URL: {current_url}"
            )

    def verify_login_failure(self):

        current_url = self.page.url

        if "auth/login" not in current_url:

            raise Exception(
                "Login succeeded but failure was expected"
            )