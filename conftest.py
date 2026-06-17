import pytest
from playwright.sync_api import sync_playwright

from config.config import BASE_URL, BROWSER, HEADLESS
from pages.login_page import LoginPage
from utils.excel_reader import read_excel


@pytest.fixture
def page():

    with sync_playwright() as p:

        browser = getattr(p, BROWSER).launch(
            headless=HEADLESS
        )

        page = browser.new_page()

        yield page

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