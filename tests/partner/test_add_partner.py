import time
from datetime import datetime
from pathlib import Path
from random import choices
from string import ascii_lowercase, digits

from utils.excel_reader import read_excel
from utils.excel_service import ExcelService
from workflows.partner.partner_requirements import get_partner_requirements
from workflows.partner.onbording_partner_workflow import (
    ADD_PARTNER_DATA_FILE,
    OnboardingPartnerWorkflow,
)

PARTNER_DOCS_DIR = ADD_PARTNER_DATA_FILE.parent / "docs"


def generated_email():
    suffix = "".join(choices(ascii_lowercase + digits, k=6))
    return f"{suffix}@gmail.com"


def capture_failure_screenshot(page, partner_type, row_index):
    safe_partner_type = "".join(
        character if character.isalnum() else "_"
        for character in str(partner_type or f"row_{row_index}").lower()
    ).strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    screenshot_path = Path("reports/screenshots") / (
        f"test_add_partner_{safe_partner_type}_{timestamp}.png"
    )
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(screenshot_path), full_page=True)
    return str(screenshot_path)


def form_responses(captures):
    responses = []
    for capture in captures:
        for response in capture.get("responses", []):
            url = response.get("url", "")
            method = response.get("method", "")
            if method not in {"POST", "PUT", "PATCH"}:
                continue
            if "/admin-agents/agents/" in url or "/upload-document/" in url:
                responses.append(response)
    return responses


def report_backend_urls(captures):
    urls = [response["url"] for response in form_responses(captures)]
    urls.extend(
        capture["backend_url"]
        for capture in captures
        if not capture.get("responses") and capture.get("backend_url")
    )
    return "\n\n".join(urls)


def report_api_responses(captures):
    responses = [
        f"{response['method']} {response['status']}\n"
        f"{response['url']}\n"
        f"{response.get('body', '')}"
        for response in form_responses(captures)
    ]
    responses.extend(
        capture["api_response"]
        for capture in captures
        if not capture.get("responses") and capture.get("api_response")
    )
    return "\n\n".join(responses)


def verification_required(data):
    value = str(data.get("verification_required") or "").strip().lower()
    if value in {"y", "yes", "true", "1"}:
        return True
    if value in {"n", "no", "false", "0"}:
        return False
    raise AssertionError(
        "Excel field 'verification_required' must be Y or N "
        f"for partner type: {data.get('partner_type')}"
    )


def verify_partner_details(add_partner_page, data):
    requirements = get_partner_requirements(
        data["partner_type"],
        data.get("referral_source"),
    )
    if not requirements:
        raise AssertionError(
            f"No requirements configured for partner type: {data['partner_type']}"
        )

    add_partner_page.fill_partner_details(data)
    add_partner_page.verify_required_fields(requirements["fields"])
    print(f"✓ required fields verified for {data['partner_type']}")
    return requirements


def complete_all_verifications(page, add_partner_page):
    verification_actions = (
        ("PAN", add_partner_page.verify_pan),
        ("bank", add_partner_page.verify_bank),
        ("GST", add_partner_page.verify_gst),
    )
    for label, action in verification_actions:
        action()
        add_partner_page.handle_name_mismatch("yes")
        page.wait_for_timeout(3000)
        print(f"✓ {label} verification requested")


def verify_all_verifications_are_pending(add_partner_page):
    for verification_name in ("pan", "bank", "gst"):
        add_partner_page.verify_verification_is_pending(verification_name)
    print("✓ PAN, bank and GST verification left pending")


def partner_document_files():
    if not PARTNER_DOCS_DIR.exists():
        raise AssertionError(
            f"Partner document directory does not exist: {PARTNER_DOCS_DIR}"
        )
    files = [
        path
        for path in PARTNER_DOCS_DIR.iterdir()
        if path.is_file() and path.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png"}
    ]
    if not files:
        raise AssertionError(f"No partner documents found in: {PARTNER_DOCS_DIR}")
    return files


def upload_required_documents(add_partner_page):
    uploaded_documents = add_partner_page.upload_configured_documents(
        partner_document_files()
    )
    captured = add_partner_page.click_upload(
        expected_upload_count=len(uploaded_documents)
    )
    upload_responses = [
        response
        for response in captured.get("responses", [])
        if "/upload-document/" in response.get("url", "")
    ]
    if len(upload_responses) < len(uploaded_documents):
        raise AssertionError(
            "Document save did not complete: "
            f"expected {len(uploaded_documents)} upload responses, "
            f"captured {len(upload_responses)}"
        )
    failed_uploads = [
        response
        for response in upload_responses
        if not 200 <= int(response.get("status", 0)) < 300
    ]
    if failed_uploads:
        raise AssertionError(f"Document upload API failed: {failed_uploads}")
    return captured, uploaded_documents


def test_add_partner(logged_in_page):
    partner_data = read_excel(str(ADD_PARTNER_DATA_FILE), "AddPartnerData")
    failures = []
    ExcelService.clear_module_results("AddPartner")

    for index, source_data in enumerate(partner_data, start=1):
        if source_data.get("Execute") and str(source_data["Execute"]).upper() != "Y":
            continue

        data = dict(source_data)
        if not str(data.get("email") or "").strip():
            data["email"] = generated_email()

        started_at = time.time()
        result = "FAIL"
        error_message = ""
        captures = []
        matched_fields = ""
        matched_documents = ""
        screenshot_path = ""

        try:
            workflow = OnboardingPartnerWorkflow(logged_in_page)
            workflow.open_add_partner_form()
            add_partner_page = workflow.add_partner_page
            requirements = verify_partner_details(add_partner_page, data)
            matched_fields = "\n".join(requirements["fields"])

            if verification_required(data):
                complete_all_verifications(logged_in_page, add_partner_page)
            else:
                verify_all_verifications_are_pending(add_partner_page)

            captures.append(workflow.create_partner_and_assert_created())
            add_partner_page.verify_required_documents(requirements["documents"])
            matched_documents = "\n".join(requirements["documents"])
            print(f"✓ required documents verified for {data['partner_type']}")
            upload_capture, uploaded_documents = upload_required_documents(add_partner_page)
            captures.append(upload_capture)
            matched_documents = "\n".join(uploaded_documents)
            approval_result = workflow.approve_partner(data)
            captures.extend(approval_result["captures"])
            captures.append(workflow.apply_partner_markup(data))
            result = "PASS"
        except Exception as exc:
            error_message = f"{data.get('partner_type', f'row {index}')}: {exc}"
            failures.append(error_message)
            try:
                screenshot_path = capture_failure_screenshot(
                    logged_in_page,
                    data.get("partner_type"),
                    index,
                )
                print(f"✓ failure screenshot captured: {screenshot_path}")
            except Exception as screenshot_error:
                print(f"✗ failure screenshot capture failed: {screenshot_error}")
        finally:
            ExcelService.write_result(
                module_name="AddPartner",
                test_id=data.get("TestCaseID") or data.get("Test ID") or f"row-{index}",
                data_test_id=data.get("partner_type", f"row-{index}"),
                result=result,
                error_message=error_message,
                backend_url=report_backend_urls(captures),
                api_response=report_api_responses(captures),
                matched_fields=matched_fields,
                matched_documents=matched_documents,
                screenshot_path=screenshot_path,
                duration=round(time.time() - started_at, 2),
            )

    if failures:
        raise AssertionError(" | ".join(failures))
