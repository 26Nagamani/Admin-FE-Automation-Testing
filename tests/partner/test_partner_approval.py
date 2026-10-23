import time
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from config.conftest import logged_in_page, page
from pages.partner.add_partner_page import AddPartnerPage
from pages.partner.partner_details_page import PartnerDetailsPage
from pages.partner.partner_list_page import PartnerListPage
from utils.excel_service import ExcelService


def join_captured(captures, key):
    return " | ".join(
        capture.get(key, "")
        for capture in captures
        if capture and capture.get(key, "")
    )


def open_pending_partner_for_approval(list_page, details_page, data=None, agent_code=None):
    captured = list_page.navigate_pending_and_capture_api()
    if agent_code:
        list_page.search_by("Partner Code", agent_code)
    elif data:
        list_page.search_partner(data)

    selected_code = list_page.open_partner_details_from_current_results()
    details_page.verify_modal_open()
    details_page.verify_documents_section()
    captured["agent_code"] = selected_code
    return captured


def approve_open_partner(details_page):
    captured = details_page.click_approve()
    if captured.get("approved"):
        details_page.close_credentials_modal()
    return captured


def repair_partner_from_approval_errors(
    details_page,
    add_partner_page,
    approval_capture,
    data=None,
):
    errors = (
        approval_capture.get("approval_error_fields")
        or approval_capture.get("approval_errors")
        or {}
    )
    if not errors:
        return {}

    details_page.click_edit()
    add_partner_page.update_fields_from_approval_errors(errors, data)
    add_partner_page.verify_fields_from_approval_errors(errors)
    captured = add_partner_page.click_create_partner()
    add_partner_page.verify_upload_step_visible()
    return captured


def run_partner_approval(page, data=None, write_report=True):
    """Approve a pending partner and repair approval-check errors if required."""
    list_page = PartnerListPage(page)
    details_page = PartnerDetailsPage(page)
    add_partner_page = AddPartnerPage(page)
    started_at = time.time()
    captures = []
    agent_code = ""
    result = "FAIL"
    error_message = ""

    try:
        list_capture = open_pending_partner_for_approval(
            list_page,
            details_page,
            data=data,
        )
        captures.append(list_capture)
        agent_code = list_capture["agent_code"]

        approval_capture = approve_open_partner(details_page)
        captures.append(approval_capture)
        if not approval_capture.get("approved"):
            errors = (
                approval_capture.get("approval_error_fields")
                or approval_capture.get("approval_errors")
            )
            if not errors:
                raise AssertionError(
                    "Partner approval failed without approval-check validation errors"
                )

            print(f"⚠ approval-check validation errors: {errors}")
            repair_capture = repair_partner_from_approval_errors(
                details_page,
                add_partner_page,
                approval_capture,
                data=data,
            )
            captures.append(repair_capture)
            captures.append(
                open_pending_partner_for_approval(
                    list_page,
                    details_page,
                    agent_code=agent_code,
                )
            )
            retry_capture = approve_open_partner(details_page)
            captures.append(retry_capture)
            if not retry_capture.get("approved"):
                retry_errors = (
                    retry_capture.get("approval_error_fields")
                    or retry_capture.get("approval_errors")
                )
                raise AssertionError(
                    f"Partner approval failed after validation repair: {retry_errors}"
                )

        result = "PASS"
        print(f"✓ partner approved | agent_code={agent_code}")
        return {"agent_code": agent_code, "captures": captures, "approved": True}
    except Exception as exc:
        error_message = str(exc)
        raise
    finally:
        if write_report:
            try:
                ExcelService.write_result(
                    module_name="PartnerApproval",
                    test_id="TC005",
                    data_test_id=agent_code or "pending-partner",
                    result=result,
                    error_message=error_message,
                    backend_url=join_captured(captures, "backend_url"),
                    api_response=join_captured(captures, "api_response"),
                    payload=join_captured(captures, "payload"),
                    duration=round(time.time() - started_at, 2),
                )
                print(f"TC005 : {result}")
            except Exception as report_error:
                print(f"TC005 : {result} | Excel write failed: {report_error}")


def test_partner_approval(logged_in_page):
    run_partner_approval(logged_in_page)
