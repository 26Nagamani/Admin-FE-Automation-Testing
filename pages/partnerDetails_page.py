from playwright.sync_api import Page


class AgentDetailsPage:

    def __init__(self, page: Page):
        self.page = page

    def verify_modal_open(self):
        self.page.wait_for_selector("text=Partner Details", timeout=7000)
        assert self.page.get_by_text("Partner Details").is_visible()

    def click_approve(self):
        captured = {
            "backend_url": "",
            "payload": "",
            "api_response": ""
        }

        def handle_request(request):
            if "verify" in request.url or "approve" in request.url:
                captured["backend_url"] = request.url
                try:
                    captured["payload"] = str(request.post_data) if request.post_data else ""
                except Exception:
                    captured["payload"] = ""

        def handle_response(response):
            if "verify" in response.url or "approve" in response.url:
                try:
                    captured["api_response"] = str(response.json())[:500]
                except Exception:
                    captured["api_response"] = "Could not parse response"

        self.page.on("request", handle_request)
        self.page.on("response", handle_response)

        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_test_id("approve-btn").wait_for(state="visible", timeout=5000)
        self.page.get_by_test_id("approve-btn").click()
        self.page.wait_for_selector("text=Agent Approved Successfully!", timeout=10000)

        self.page.remove_listener("request", handle_request)
        self.page.remove_listener("response", handle_response)

        return captured

    def click_reject(self, reason: str = "Test rejection"):
        captured = {
            "backend_url": "",
            "payload": "",
            "api_response": ""
        }

        def handle_request(request):
            if "reject" in request.url:
                captured["backend_url"] = request.url
                try:
                    captured["payload"] = str(request.post_data) if request.post_data else ""
                except Exception:
                    captured["payload"] = ""

        def handle_response(response):
            if "reject" in response.url:
                try:
                    captured["api_response"] = str(response.json())[:500]
                except Exception:
                    captured["api_response"] = "Could not parse response"

        self.page.on("request", handle_request)
        self.page.on("response", handle_response)

        self.page.once("dialog", lambda dialog: dialog.accept(reason))
        self.page.get_by_test_id("reject-btn").wait_for(state="visible", timeout=5000)
        self.page.get_by_test_id("reject-btn").click()
        self.page.wait_for_selector("text=Agent rejected successfully", timeout=7000)

        self.page.remove_listener("request", handle_request)
        self.page.remove_listener("response", handle_response)

        return captured

    def verify_credentials_modal(self):
        self.page.wait_for_selector("text=Agent Approved Successfully!", timeout=10000)
        assert self.page.get_by_text("Agent Approved Successfully!").is_visible()

    def get_credentials(self):
        username = self.page.get_by_test_id("credential-username").input_value()
        password = self.page.get_by_test_id("credential-password").input_value()
        return username, password

    def close_credentials_modal(self):
        self.page.get_by_test_id("credentials-ok-btn").wait_for(state="visible", timeout=5000)
        self.page.get_by_test_id("credentials-ok-btn").click()
        self.page.wait_for_load_state("networkidle")

    def close_modal(self):
        self.page.get_by_test_id("modal-close-btn").wait_for(state="visible", timeout=5000)
        self.page.get_by_test_id("modal-close-btn").click()

    def verify_documents_section(self):
        self.page.get_by_test_id("documents-section-btn").wait_for(state="visible", timeout=7000)
        assert self.page.get_by_test_id("documents-section-btn").is_visible()

    def verify_rejected_status(self):
        self.page.wait_for_selector("text=Agent rejected successfully", timeout=7000)
        assert self.page.get_by_text("Agent rejected successfully").is_visible()