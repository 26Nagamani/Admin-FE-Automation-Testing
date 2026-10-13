from pages.partner.add_partner_page import AddPartnerPage
from pages.partner.partner_list_page import PartnerListPage
from workflows.partner.partner_paths import PARTNER_DOCS_DIR
from workflows.partner.partner_requirements import get_partner_requirements


class CreatePartnerWorkflow:
    def __init__(self, page):
        self.page = page
        self.list_page = PartnerListPage(page)
        self.add_partner_page = AddPartnerPage(page)

    def open_add_partner_form(self):
        self.list_page.navigate()
        print("✓ navigated")

        self.list_page.click_add_partner()
        print("✓ add partner clicked")

    def complete_partner_details(self, data):
        requirements = get_partner_requirements(data["partner_type"])
        if not requirements:
            raise Exception(f"No field/document requirements configured for partner type: {data['partner_type']}")

        self.add_partner_page.fill_partner_details(data)
        print("✓ form filled")

        self.add_partner_page.verify_required_fields(requirements["fields"])
        print(f"✓ required fields verified for {data['partner_type']}")

        self.add_partner_page.verify_pan()
        self.add_partner_page.handle_name_mismatch("yes")
        self.page.wait_for_timeout(3000)
        print("✓ PAN verify clicked")

        self.add_partner_page.verify_bank()
        self.add_partner_page.handle_name_mismatch("yes")
        self.page.wait_for_timeout(3000)
        print("✓ Bank verify clicked")

        self.add_partner_page.verify_gst()
        self.add_partner_page.handle_name_mismatch("yes")
        self.page.wait_for_timeout(3000)
        print("✓ GST verify clicked")

        self.add_partner_page.click_create_partner()
        self.page.wait_for_timeout(2000)
        print(f"✓ create-partner clicked | current url: {self.page.url}")

        self.add_partner_page.verify_upload_step_visible()
        self.add_partner_page.verify_required_documents(requirements["documents"])
        print(f"✓ required documents verified for {data['partner_type']}")

    def upload_required_documents(self):
        upload_files = self.get_upload_files()

        error_texts = self.page.locator(".text-status-danger").all_text_contents()
        if error_texts:
            print(f"⚠ Validation errors visible: {error_texts}")

        uploaded_documents = self.add_partner_page.upload_configured_documents(upload_files)

        upload_captured = self.add_partner_page.click_upload(
            expected_upload_count=len(uploaded_documents)
        )
        print("✓ upload clicked")
        upload_responses = [
            response for response in upload_captured.get("responses", [])
            if "/upload-document/" in response.get("url", "")
        ]
        if len(upload_responses) < len(uploaded_documents):
            raise Exception(
                f"Document save did not complete. Expected {len(uploaded_documents)} upload API responses, "
                f"captured {len(upload_responses)}. Captured URLs: {upload_captured.get('backend_url', '')}"
            )

        failed_uploads = [
            response for response in upload_responses
            if not (200 <= int(response.get("status", 0)) < 300)
        ]
        if failed_uploads:
            raise Exception(f"Document upload API failed: {failed_uploads}")

        if upload_captured.get("backend_url"):
            print(f"✓ upload API captured: {upload_captured['backend_url']}")
        else:
            print("⚠ upload API response was not captured")

        return upload_captured

    @staticmethod
    def get_upload_files():
        if not PARTNER_DOCS_DIR.exists():
            raise Exception(
                f"Document upload directory does not exist: {PARTNER_DOCS_DIR}. "
                "Create the required files before running the test."
            )

        upload_files = [
            path for path in PARTNER_DOCS_DIR.iterdir()
            if path.is_file() and path.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png"}
        ]

        return upload_files
