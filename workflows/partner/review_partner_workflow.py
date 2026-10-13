from pages.partner.partner_details_page import PartnerDetailsPage
from pages.partner.partner_list_page import PartnerListPage


class ReviewPartnerWorkflow:
    def __init__(self, page):
        self.page = page
        self.list_page = PartnerListPage(page)
        self.details_page = PartnerDetailsPage(page)

    def open_pending_partner_details(self):
        api_captured = self.list_page.navigate_and_capture_api()
        print("✓ navigated")
        print(f"✓ backend url: {api_captured['backend_url']}")

        self.list_page.click_pending_tab()
        pending_count = self.list_page.get_pending_count()
        print(f"✓ pending count: {pending_count}")

        self.page.wait_for_selector('[data-testid^="view-details-"]', timeout=7000)
        first_agent = self.page.locator('[data-testid^="view-details-"]').first
        agent_code = first_agent.get_attribute("data-testid").replace("view-details-", "")
        print(f"✓ agent code: {agent_code}")

        self.list_page.click_view_details(agent_code)
        print("✓ view details clicked")

        self.details_page.verify_modal_open()
        print("✓ modal open")

        self.details_page.verify_documents_section()
        print("✓ documents section visible")

        return api_captured

    def approve_if_available(self, api_captured):
        approve_btn = self.page.locator('[data-testid="approve-btn"]')
        if approve_btn.is_visible():
            print("✓ approve button visible")

            approve_captured = self.details_page.click_approve()
            print("✓ approve clicked")

            api_captured["backend_url"] = approve_captured["backend_url"]
            api_captured["payload"] = approve_captured["payload"]
            api_captured["api_response"] = approve_captured["api_response"]
            print(f"✓ approve api url: {api_captured['backend_url']}")

            self.details_page.verify_credentials_modal()
            print("✓ credentials modal open")

            username, password = self.details_page.get_credentials()
            print(f"✓ credentials — username: {username} | password: {password}")

            self.details_page.close_credentials_modal()
            print("✓ credentials modal closed")
        else:
            print("⚠ approve button not visible — agent already approved/rejected, skipping approve step")
            self.details_page.close_modal()

        return api_captured

    def open_created_pending_partner(self, data):
        agent_code = self.list_page.open_pending_partner_details(data)
        self.details_page.verify_modal_open()
        self.details_page.verify_documents_section()
        return agent_code

    def approve_open_partner(self):
        approve_btn = self.page.locator('[data-testid="approve-btn"]')
        if approve_btn.count() == 0 or not approve_btn.is_visible():
            raise Exception("Approve button not visible for pending partner")

        captured = self.details_page.click_approve()
        if captured.get("approved"):
            self.details_page.close_credentials_modal()
        return captured

    def edit_open_partner_after_approval_errors(self):
        self.details_page.click_edit()

    def open_approved_partner_markup(self, data):
        self.list_page.open_approved_partner_markup(data)
