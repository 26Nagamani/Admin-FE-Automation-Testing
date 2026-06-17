from playwright.sync_api import Page
from config.config import BASE_URL


class PartnerListPage:

    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto(f"{BASE_URL}agents")
        self.page.wait_for_load_state("networkidle")

    def navigate_and_capture_api(self):
        captured = {
            "backend_url": "",
            "payload": "",
            "api_response": ""
        }

        def handle_response(response):
            if (
                "agents" in response.url
                and "localhost:5173" not in response.url
                and response.status == 200
            ):
                captured["backend_url"] = response.url

                try:
                    captured["api_response"] = str(response.json())[:500]
                except Exception:
                    captured["api_response"] = "Could not parse response"

        self.page.on("response", handle_response)

        # Use the same navigation method that already works
        self.navigate()

        print(f"After navigate URL: {self.page.url}")

        self.page.remove_listener("response", handle_response)

        return captured

    def select_branch(self, branch_name: str):
        self.page.locator("#branch-filter").click()
        self.page.keyboard.type(branch_name)
        self.page.locator(
            f".react-select__option:has-text('{branch_name}')"
        ).click()
        self.page.wait_for_load_state("networkidle")

    def click_approved_tab(self):
        self.page.get_by_test_id("tab-approved").wait_for(
            state="visible",
            timeout=10000
        )
        self.page.get_by_test_id("tab-approved").click()
        self.page.wait_for_load_state("networkidle")

    def click_pending_tab(self):
        print(f"Current URL before pending click: {self.page.url}")

        self.page.get_by_test_id("tab-pending").wait_for(
            state="visible",
            timeout=10000
        )
        self.page.get_by_test_id("tab-pending").click()
        self.page.wait_for_load_state("networkidle")

    def get_pending_count(self) -> int:
        text = (
            self.page.get_by_test_id("tab-pending")
            .locator("span")
            .inner_text()
            .strip()
        )
        return int(text) if text.isdigit() else 0

    def click_add_partner(self):
        self.page.get_by_test_id("add-partner-btn").wait_for(
            state="visible",
            timeout=10000
        )
        self.page.get_by_test_id("add-partner-btn").click()
        self.page.wait_for_load_state("networkidle")

    def click_view_details(self, agent_code: str):
        self.page.get_by_test_id(
            f"view-details-{agent_code}"
        ).wait_for(
            state="visible",
            timeout=7000
        )

        self.page.get_by_test_id(
            f"view-details-{agent_code}"
        ).click()

        self.page.wait_for_selector(
            "text=Partner Details",
            timeout=7000
        )