import time

from utils.excel_reader import read_excel
from utils.excel_service import ExcelService
from workflows.partner.partner_markup_workflow import PartnerMarkupWorkflow
from workflows.partner.partner_paths import PARTNER_MARKUP_DATA_FILE


partner_markup_data = read_excel(
    str(PARTNER_MARKUP_DATA_FILE),
    "PartnerMarkupData"
)


def test_partner_markup(logged_in_page):

    page = logged_in_page
    markup_workflow = PartnerMarkupWorkflow(page)
    data = partner_markup_data[0]
    start_time = time.time()
    result, error_message = "FAIL", ""

    try:
        markup_workflow.open_markup_for_partner(data)
        markup_workflow.verify_set_markup_modal()
        markup_workflow.verify_charges_tab()

        result = "PASS"

    except Exception as e:
        error_message = str(e)
        print(f"TC004 Error: {error_message}")

    finally:
        duration = round(time.time() - start_time, 2)
        try:
            ExcelService.write_result(
                module_name="PartnerMarkup",
                test_id="TC004",
                data_test_id="partner-markup",
                result=result,
                error_message=error_message,
                duration=duration,
            )
            print(f"TC004 : {result}")
        except Exception as excel_err:
            print(f"TC004 : {result} | Excel write failed: {excel_err}")
