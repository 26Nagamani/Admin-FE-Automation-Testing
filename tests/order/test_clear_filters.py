import time

from pages.order.reports_filter_page import ReportsFilterPage
from utils.excel_reader import read_excel
from utils.excel_service import ExcelService


filter_data = read_excel(
    "test_data/ReportsFilterData.xlsx",
    "Sheet1"
)


def test_clear_filters(logged_in_page):

    page = logged_in_page
    filter_page = ReportsFilterPage(page)

    for row in filter_data:

        start_time = time.time()
        result = "FAIL"
        error_message = ""

        try:

            filter_page.toggle_filters()

            filter_page.set_filters(
                order_code=row["OrderCode"],
                phone_number=str(row["PhoneNumber"]),
                from_date=row["FromDate"],
                to_date=row["ToDate"],
                branch=row["Branch"],
                status=row["Status"],
                order_type=row["OrderType"],
                city=row["City"],
                currency=row["Currency"],
                product=row["Product"]
            )

            print("✓ Filters Applied")

            filter_page.clear_filters()

            print("✓ Clear Filters Clicked")

            assert filter_page.get_order_code() == ""
            assert filter_page.get_phone_number() == ""
            assert filter_page.get_from_date() == ""
            assert filter_page.get_to_date() == ""

            result = "PASS"

            print("✓ Filters Cleared Successfully")

        except Exception as e:

            error_message = str(e)

            print(f"✗ FAILED : {error_message}")

        finally:

            ExcelService.write_result(
                module_name="Reports",
                test_id="TC002",
                data_test_id=row["OrderCode"],
                result=result,
                error_message=error_message,
                duration=round(
                    time.time() - start_time,
                    2
                )
            )

            print(f"TC002 : {result}")
