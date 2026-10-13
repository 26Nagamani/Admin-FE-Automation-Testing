import time
from random import choices
from string import ascii_lowercase, digits

from utils.excel_reader import read_excel
from utils.excel_service import ExcelService
from workflows.partner.create_partner_workflow import CreatePartnerWorkflow
from workflows.partner.partner_markup_workflow import PartnerMarkupWorkflow
from workflows.partner.partner_paths import ADD_PARTNER_DATA_FILE
from workflows.partner.partner_requirements import get_partner_requirements
from workflows.partner.review_partner_workflow import ReviewPartnerWorkflow


partner_data = read_excel(str(ADD_PARTNER_DATA_FILE), "AddPartnerData")


def slug(value):
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


def generate_partner_email(partner_type, test_case):
    partner_slug = slug(partner_type) or "partner"
    test_slug = slug(test_case) or "tc"
    random_suffix = "".join(choices(ascii_lowercase + digits, k=6))
    return f"{random_suffix}@gmail.com"


def failure_screenshot_path():
    return "reports/screenshots/test_add_partner.png"


def capture_backend_responses(page):
    captured = []

    def handle_response(response):
        if "localhost:5173" in response.url or "/api/" not in response.url:
            return

        item = {
            "method": response.request.method,
            "status": response.status,
            "url": response.url,
            "body": "",
        }
        try:
            item["body"] = str(response.json())[:500]
        except Exception:
            item["body"] = "Could not parse response"
        captured.append(item)

    page.on("response", handle_response)
    return captured, handle_response


def format_backend_urls(responses):
    return " | ".join(response["url"] for response in responses)


def format_api_responses(responses):
    return " | ".join(
        f"{response['method']} {response['status']} {response['url']} => {response['body']}"
        for response in responses
    )


def approve_partner_with_retry(page, partner_workflow, review_workflow, data):
    review_workflow.open_created_pending_partner(data)
    approve_captured = review_workflow.approve_open_partner()

    approval_errors = approve_captured.get("approval_errors") or []
    if not approval_errors:
        print("✓ partner approved")
        return approve_captured

    print(f"⚠ approval prerequisites found: {approval_errors}")
    review_workflow.edit_open_partner_after_approval_errors()
    partner_workflow.complete_partner_details(data)
    partner_workflow.upload_required_documents()

    review_workflow.open_created_pending_partner(data)
    retry_captured = review_workflow.approve_open_partner()
    retry_errors = retry_captured.get("approval_errors") or []
    if retry_errors:
        raise Exception(f"Approval prerequisite errors after edit retry: {retry_errors}")

    print("✓ partner approved after edit retry")
    return retry_captured


def run_markup_after_approval(data, review_workflow, markup_workflow):
    try:
        review_workflow.open_approved_partner_markup(data)
        markup_workflow.verify_set_markup_modal()
        markup_workflow.verify_charges_tab()
        print("✓ markup opened from approved partner table")
    except Exception as table_markup_error:
        print(f"⚠ approved table markup path failed, using markup page fallback: {table_markup_error}")
        markup_workflow.open_markup_for_partner(data)
        markup_workflow.verify_set_markup_modal()
        markup_workflow.verify_charges_tab()
        print("✓ markup test completed through markup page")


def test_add_partner(logged_in_page):

    page = logged_in_page
    partner_workflow = CreatePartnerWorkflow(page)
    review_workflow = ReviewPartnerWorkflow(page)
    markup_workflow = PartnerMarkupWorkflow(page)

    failures = []
    document_key_log = {}
    ExcelService.clear_module_results("AddPartner")

    for index, data in enumerate(partner_data, start=1):
        if data.get("Execute") and str(data["Execute"]).upper() != "Y":
            continue

        row_start_time = time.time()
        row_result = "FAIL"
        row_error_message = ""
        row_responses, response_listener = capture_backend_responses(page)

        try:
            data = dict(data)
            if not str(data.get("email") or "").strip():
                test_case = data.get("TestCaseID") or data.get("Test ID") or f"row{index}"
                data["email"] = generate_partner_email(data.get("partner_type"), test_case)
                print(f"✓ generated email for {data.get('partner_type')} row {index}: {data['email']}")

            print(f"✓ using partner type row {index}: {data}")
            requirements = get_partner_requirements(data["partner_type"])
            document_key_log[data["partner_type"]] = requirements["documents"] if requirements else []

            partner_workflow.open_add_partner_form()
            partner_workflow.complete_partner_details(data)
            partner_workflow.upload_required_documents()
            approve_partner_with_retry(page, partner_workflow, review_workflow, data)
            run_markup_after_approval(data, review_workflow, markup_workflow)
            row_result = "PASS"

        except Exception as e:
            row_error_message = f"{data.get('partner_type', f'row {index}')}: {e}"
            failures.append(row_error_message)
            print(f"TC003 Error: {row_error_message}")

        finally:
            page.remove_listener("response", response_listener)
            row_duration = round(time.time() - row_start_time, 2)
            row_backend_urls = format_backend_urls(row_responses)
            row_api_responses = format_api_responses(row_responses)
            try:
                ExcelService.write_result(
                    module_name="AddPartner",
                    test_id=data.get("TestCaseID") or data.get("Test ID") or f"TC003-{index}",
                    data_test_id=data.get("partner_type", f"row-{index}"),
                    result=row_result,
                    error_message=row_error_message,
                    backend_url=row_backend_urls,
                    api_response=row_api_responses,
                    duration=row_duration,
                )
                print(f"✓ output Excel report updated for {data.get('partner_type')}: {row_result}")
            except Exception as excel_err:
                print(f"Output Excel report update failed for {data.get('partner_type')}: {excel_err}")

    result = "FAIL" if failures else "PASS"
    error_message = " | ".join(failures)

    print("📄 overall document upload docKeys by partner type")
    for partner_type, document_keys in document_key_log.items():
        print(f"📄 {partner_type}: {document_keys}")

    print(f"TC003 : {result}")

    if failures:
        raise AssertionError(error_message)
