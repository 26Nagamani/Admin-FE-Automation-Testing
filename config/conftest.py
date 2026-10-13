from pathlib import Path
# import shutil

import pytest
from playwright.sync_api import sync_playwright

from config.config import BASE_URL, BROWSER, HEADLESS
from pages.login_page import LoginPage
from utils.excel_reader import read_excel


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    setattr(item, f"rep_{call.when}", outcome.get_result())


@pytest.fixture
def page(request):

    screenshot_dir = Path("reports/screenshots")
    # video_dir = Path("reports/videos")
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    # video_dir.mkdir(parents=True, exist_ok=True)
    test_name = request.node.name.replace("/", "_").replace("\\", "_")

    with sync_playwright() as p:

        browser = getattr(p, BROWSER).launch(
            headless=HEADLESS
        )

        context = browser.new_context()
        # context = browser.new_context(
        #     record_video_dir=str(video_dir)
        # )

        page = context.new_page()

        try:
            yield page

        finally:
            if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
                page.screenshot(
                    path=str(screenshot_dir / f"{test_name}.png"),
                    full_page=True
                )

            # video = page.video
            context.close()

            # if video:
            #     video_path = Path(video.path())
            #     if video_path.exists():
            #         shutil.move(
            #             str(video_path),
            #             str(video_dir / f"{test_name}.webm")
            #         )

            browser.close()


@pytest.fixture
def logged_in_page(page):

    login_page = LoginPage(page)

    # Read login data from Excel
    login_data = read_excel(
        "test_data/LoginData.xlsx",
        "Sheet1"
    )[0]

    login_page.navigate(BASE_URL)

    login_page.login(
        login_data["Username"],
        login_data["Password"]
    )

    yield page

    try:
        login_page.logout()
    except Exception:
        pass
