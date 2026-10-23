from playwright.sync_api import Page, expect

from config.config import BASE_URL


class PartnerMarkupPage:

    def __init__(self, page: Page):
        self.page = page

    def navigate(self):
        self.page.goto(f"{BASE_URL}partners/markup")
        self.page.wait_for_load_state("networkidle")

    def select_dropdown(self, testid: str, value: str):
        wrapper = self.page.get_by_test_id(testid)
        wrapper.wait_for(state="visible", timeout=10000)
        control = wrapper.locator(".react-select__control")
        if control.count() == 0:
            expect(wrapper.get_by_display_value(value)).to_be_visible(timeout=10000)
            return

        control.click()
        self.page.keyboard.type(value)
        self.page.wait_for_timeout(500)
        self.page.keyboard.press("ArrowDown")
        self.page.keyboard.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def select_branch(self, branch_name: str):
        self.select_dropdown("markup-branch-select", branch_name)

    def select_partner(self, partner_name: str):
        self.select_dropdown("markup-partner-select", partner_name)

    def verify_markup_loaded(self):
        expect(self.page.get_by_test_id("markup-tab")).to_be_visible(timeout=10000)
        expect(self.page.get_by_test_id("set-markup-btn")).to_be_visible(timeout=10000)
        self.page.wait_for_load_state("networkidle")

    def open_set_markup_modal(self):
        button = self.page.get_by_test_id("set-markup-btn")
        button.wait_for(state="visible", timeout=10000)
        button.click()
        expect(self.page.get_by_test_id("markup-setup-modal")).to_be_visible(timeout=10000)

    def select_first_available_currency(self, prefer_group=True, skip=0):
        if not prefer_group:
            self.page.get_by_test_id("markup-individual-currency-mode-0").click()

        wrapper = self.page.get_by_test_id("markup-currency-select-0")
        control = wrapper.locator(".admin-form-select__control")
        control.click()
        options = self.page.locator(
            '[role="option"]:not([aria-disabled="true"]), '
            '.admin-form-select__option:not(.admin-form-select__option--is-disabled)'
        )
        try:
            options.nth(skip).wait_for(state="visible", timeout=3000)
        except Exception:
            if prefer_group:
                self.page.keyboard.press("Escape")
                return self.select_first_available_currency(prefer_group=False, skip=skip)
            raise AssertionError("No available individual currency can receive markup")

        selected = options.nth(skip).inner_text().strip()
        options.nth(skip).click()
        print(
            f"✓ selected {'currency group' if prefer_group else 'individual currency'}: {selected}"
        )
        return {"mode": "group" if prefer_group else "individual", "value": selected}

    def fill_first_markup_row(self):
        self.page.get_by_test_id("markup-pfx-margin-0").fill("1")
        self.page.get_by_test_id("markup-partner-margin-0").fill("1")
        self.page.get_by_test_id("markup-prithvi-charge-0").fill("0")
        self.page.get_by_test_id("markup-partner-charge-0").fill("0")
        expect(self.page.get_by_test_id("markup-save-btn")).to_be_visible(timeout=10000)

    def replace_currency_after_validation(self):
        self.page.get_by_test_id("markup-validation-close-btn").click()
        wrapper = self.page.get_by_test_id("markup-currency-select-0")
        remove_buttons = wrapper.locator('[aria-label^="Remove "]')
        while remove_buttons.count() > 0:
            remove_buttons.first.click()

        self.page.get_by_test_id("markup-individual-currency-mode-0").click()
        return self.select_first_available_currency(prefer_group=False)

    def save_markup_with_currency_retry(self):
        captured = {"backend_url": "", "api_response": "", "responses": []}

        def handle_response(response):
            if "markup" not in response.url.lower() or "localhost:5173" in response.url:
                return
            item = {
                "method": response.request.method,
                "status": response.status,
                "url": response.url,
                "body": "",
            }
            try:
                item["body"] = str(response.json())[:1000]
            except Exception:
                item["body"] = "Could not parse response"
            captured["responses"].append(item)
            captured["backend_url"] = " | ".join(entry["url"] for entry in captured["responses"])
            captured["api_response"] = " | ".join(
                f"{entry['method']} {entry['status']} {entry['url']} => {entry['body']}"
                for entry in captured["responses"]
            )

        self.page.on("response", handle_response)
        try:
            self.page.get_by_test_id("markup-save-btn").click()
            validation = self.page.get_by_test_id("markup-validation-error")
            modal = self.page.get_by_test_id("markup-setup-modal")
            for _ in range(30):
                if validation.count() > 0 and validation.is_visible():
                    print(f"⚠ markup validation error: {validation.inner_text().strip()}")
                    self.replace_currency_after_validation()
                    self.page.get_by_test_id("markup-save-btn").click()
                    break
                if modal.count() == 0 or not modal.is_visible():
                    return captured
                self.page.wait_for_timeout(500)

            expect(modal).to_be_hidden(timeout=30000)
            return captured
        finally:
            self.page.remove_listener("response", handle_response)

    def create_markup(self):
        self.open_set_markup_modal()
        selection = self.select_first_available_currency(prefer_group=True)
        self.fill_first_markup_row()
        captured = self.save_markup_with_currency_retry()
        captured["currency_selection"] = selection
        print("✓ markup created")
        return captured

    def close_set_markup_modal(self):
        self.page.get_by_test_id("markup-setup-close-btn").click()
        self.page.wait_for_selector("text=Configure bulk markup rules.", state="hidden", timeout=10000)

    def switch_to_charges_tab(self):
        self.page.get_by_test_id("charges-tab").click()
        self.page.wait_for_load_state("networkidle")

    def verify_charges_loaded(self):
        expect(self.page.get_by_test_id("charges-tab")).to_have_attribute(
            "aria-selected",
            "true",
            timeout=10000
        )
        self.page.wait_for_load_state("networkidle")
