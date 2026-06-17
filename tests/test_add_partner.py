import time
import os

from pages.partner_list_page import PartnerListPage
from pages.add_partner_page import AddPartnerPage
from utils.excel_reader import read_excel
from utils.excel_service import ExcelService


partner_data = read_excel("test_data/AddPartnerData.xlsx", "AddPartnerData")


def ensure_test_documents():
    os.makedirs("test_data/docs", exist_ok=True)
    files = {
        "doc1.pdf": b"%PDF-1.4\n%Dummy Document 1\n%%EOF",
        "doc2.pdf": b"%PDF-1.4\n%Dummy Document 2\n%%EOF",
        "doc3.pdf": b"%PDF-1.4\n%Dummy Document 3\n%%EOF",
        "doc4.pdf": b"%PDF-1.4\n%Dummy Document 4\n%%EOF",
        "doc5.pdf": b"%PDF-1.4\n%Dummy Document 5\n%%EOF",
    }
    for filename, content in files.items():
        path = f"test_data/docs/{filename}"
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(content)


def test_add_partner(logged_in_page):

    page = logged_in_page
    list_page = PartnerListPage(page)
    add_partner = AddPartnerPage(page)

    result = "FAIL"
    error_message = ""
    start_time = time.time()

    try:
        list_page.navigate()
        print("✓ navigated")

        list_page.click_add_partner()
        print("✓ add partner clicked")

        data = partner_data[0]
        print(f"✓ using data row: {data}")

        add_partner.fill_partner_details(data)
        print("✓ form filled")

        add_partner.verify_pan()
        page.wait_for_timeout(3000)
        print("✓ PAN verify clicked")

        add_partner.verify_bank()
        page.wait_for_timeout(3000)
        print("✓ Bank verify clicked")

        add_partner.verify_gst()
        page.wait_for_timeout(3000)
        print("✓ GST verify clicked")

        # ---- Click Create Partner ----
        add_partner.click_create_partner()
        page.wait_for_timeout(2000)
        print(f"✓ create-partner clicked | current url: {page.url}")

        # Check for validation errors that block step transition
        error_texts = page.locator('.text-status-danger').all_text_contents()
        if error_texts:
            print(f"⚠ Validation errors visible: {error_texts}")

        # Check if step 2 file inputs exist
        file_inputs = page.locator('input[type="file"]')
        count = file_inputs.count()
        print(f"✓ file input count on page: {count}")

        if count == 0:
            raise Exception(
                f"Step 2 documents did not render. "
                f"Validation errors: {error_texts} | URL: {page.url}"
            )

        # ---- Discover real doc_key values ----
        ensure_test_documents()
        dummy_files = [
            "test_data/docs/doc1.pdf",
            "test_data/docs/doc2.pdf",
            "test_data/docs/doc3.pdf",
            "test_data/docs/doc4.pdf",
            "test_data/docs/doc5.pdf",
        ]

        doc_keys = []
        for i in range(count):
            testid = file_inputs.nth(i).get_attribute("data-testid")
            print(f"  Found upload field: {testid}")
            if testid:
                doc_keys.append(testid.replace("upload-", ""))

        for i, doc_key in enumerate(doc_keys):
            file_to_upload = dummy_files[i % len(dummy_files)]
            add_partner.upload_document(doc_key, file_to_upload)
            print(f"✓ uploaded {file_to_upload} -> {doc_key}")

        add_partner.click_upload()
        print("✓ upload clicked")

        result = "PASS"

    except Exception as e:
        error_message = str(e)