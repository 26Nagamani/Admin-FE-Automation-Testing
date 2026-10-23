import time

from pages.login.login_page import LoginPage
from utils.excel_reader import read_excel
from utils.excel_service import ExcelService
from config.config import BASE_URL


test_data = read_excel(
    "test_data/LoginData.xlsx",
    "Sheet1"
)


def test_login(page):

    login_page = LoginPage(page)

    payload_data = {}

    # ✅ DEFINE CAPTURE FIRST
    def capture(request):
        if request.method == "POST":
            try:
                payload_data["payload"] = request.post_data
            except:
                payload_data["payload"] = None

    # ✅ REGISTER EVENT AFTER FUNCTION EXISTS
    page.on("request", capture)

    for data in test_data:

        if data["Execute"] != "Y":
            continue

        start_time = time.time()

        try:
            login_page.navigate(BASE_URL)

            login_page.login(
                data["Username"],
                data["Password"]
            )

            if data["Expected"] == "Pass":
                login_page.verify_login_success()
            else:
                login_page.verify_login_failure()

            duration = round(time.time() - start_time, 2)

            ExcelService.write_result(
                module_name="Login",
                test_id=data["TestCaseID"],
                data_test_id="login-submit",
                result="PASS",
                duration=duration,
                payload=payload_data.get("payload", "EMPTY")
            )

            print(f"{data['TestCaseID']} : PASS")

        except Exception as e:

            duration = round(time.time() - start_time, 2)

            ExcelService.write_result(
                module_name="Login",
                test_id=data["TestCaseID"],
                data_test_id="login-submit",
                result="FAIL",
                error_message=str(e),
                duration=duration,
                payload=payload_data.get("payload", "EMPTY")
            )

            print(f"{data['TestCaseID']} : FAIL")

            continue
