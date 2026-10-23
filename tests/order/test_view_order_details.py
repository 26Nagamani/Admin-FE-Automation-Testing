import time

from pages.order.order_details_page import OrderDetailsPage
from pages.order.report_list_page import ReportsListPage
from utils.excel_service import ExcelService


def test_view_order_details(logged_in_page):

    page = logged_in_page

    reports_list = ReportsListPage(page)
    order_details = OrderDetailsPage(page)

    start_time = time.time()
    result = "FAIL"
    error_message = ""

    try:

        row_count = reports_list.get_row_count()

        if row_count == 0:
            raise Exception(
                "No orders available in reports table"
            )

        reports_list.click_first_view_order()

        print("✓ View Order clicked")

        order_details.verify_modal_open()

        print("✓ Order Details modal opened")

        order_details.close_modal()

        print("✓ Modal closed")

        result = "PASS"

    except Exception as e:

        error_message = str(e)

        print(f"✗ FAILED : {error_message}")

        raise

    finally:

        ExcelService.write_result(
            module_name="Reports",
            test_id="TC003",
            data_test_id="view-order-details",
            result=result,
            error_message=error_message,
            duration=round(
                time.time() - start_time,
                2
            )
        )

        print(f"TC003 : {result}")
