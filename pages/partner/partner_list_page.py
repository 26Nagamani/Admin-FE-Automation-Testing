from playwright.sync_api import Page
from config.config import BASE_URL


class PartnerListPage:

    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto(f"{BASE_URL}partners")
        self.page.wait_for_load_state("networkidle")

    def navigate_and_capture_api(self):
        captured = {
            "backend_url": "",
            "payload": "",
            "api_response": ""
        }

        def handle_response(response):
            if (
                ("partners-v1" in response.url or "/partners" in response.url)
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
        self.page.get_by_text("Branch:", exact=True).click()
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

    def search_by(self, filter_label: str, value: str):
        self.page.locator("label[for='agent-filter-by']").click()
        self.page.keyboard.type(filter_label)
        self.page.keyboard.press("Enter")

        value_input = self.page.locator("#agent-filter-value")
        value_input.wait_for(state="visible", timeout=10000)
        value_input.fill(str(value))
        self.page.get_by_role("button", name="Search").click()
        self.page.wait_for_load_state("networkidle")

    def search_partner(self, data):
        email = str(data.get("email") or "").strip()
        partner_name = str(data.get("partner_name") or "").strip()
        if email:
            self.search_by("Partner Email", email)
            return email
        if partner_name:
            self.search_by("Partner Name", partner_name)
            return partner_name
        raise ValueError("Cannot search partner: email and partner_name are empty")

    def first_visible_agent_code(self):
        self.page.wait_for_selector('[data-testid^="view-details-"]', timeout=10000)
        first_agent = self.page.locator('[data-testid^="view-details-"]').first
        return first_agent.get_attribute("data-testid").replace("view-details-", "")

    def open_partner_details_from_current_results(self):
        agent_code = self.first_visible_agent_code()
        self.click_view_details(agent_code)
        return agent_code

    def open_pending_partner_details(self, data):
        self.navigate()
        self.click_pending_tab()
        searched_value = self.search_partner(data)
        agent_code = self.open_partner_details_from_current_results()
        print(f"✓ pending partner opened | search={searched_value} | agent_code={agent_code}")
        return agent_code

    def open_approved_partner_markup(self, data):
        self.navigate()
        self.click_approved_tab()
        searched_value = self.search_partner(data)
        self.page.get_by_role("link", name="Apply Markup").first.wait_for(
            state="visible",
            timeout=10000,
        )
        self.page.get_by_role("link", name="Apply Markup").first.click()
        self.page.wait_for_load_state("networkidle")
        print(f"✓ approved partner markup opened | search={searched_value}")

    def get_pending_count(self) -> int:
        text = (
            self.page.get_by_test_id("tab-pending")
            .locator("span")
            .inner_text()
            .strip()
        )
        return int(text) if text.isdigit() else 0

    def click_add_partner(self):
        self.page.get_by_test_id("add-partner-partner-btn").wait_for(
            state="visible",
            timeout=10000
        )
        self.page.get_by_test_id("add-partner-partner-btn").click()
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
