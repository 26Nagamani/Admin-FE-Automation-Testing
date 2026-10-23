from pathlib import Path
import subprocess
import sys

from pages.partner.add_partner_page import AddPartnerPage
from pages.partner.partner_list_page import PartnerListPage


REPO_ROOT = Path(__file__).resolve().parents[2]
ADD_PARTNER_DATA_FILE = REPO_ROOT / "test_data" / "partner" / "AddPartnerData.xlsx"
PARTNER_TESTS = [
    REPO_ROOT / "tests" / "partner" / "test_add_partner.py",
]


class OnboardingPartnerWorkflow:
    """Open the add-partner form and assert that partner creation succeeds."""

    def __init__(self, page):
        self.page = page
        self.list_page = PartnerListPage(page)
        self.add_partner_page = AddPartnerPage(page)

    def open_add_partner_form(self):
        self.list_page.navigate()
        self.list_page.click_add_partner()

    def create_partner_and_assert_created(self):
        captured = self.add_partner_page.click_create_partner()
        self.add_partner_page.verify_upload_step_visible()
        print("✓ partner created and document-upload step displayed")
        return captured

    def approve_partner(self, data=None):
        """Select the newly onboarded pending partner and complete approval."""
        from tests.partner.test_partner_approval import run_partner_approval

        result = run_partner_approval(self.page, data=data, write_report=False)
        print(f"✓ partner approved | agent_code={result['agent_code']}")
        return result

    def apply_partner_markup(self, data):
        """Apply markup to the partner approved in this browser context."""
        from tests.partner.test_partner_markup import run_direct_partner_markup

        captured = run_direct_partner_markup(self.page, data)
        print("✓ partner markup applied during onboarding")
        return captured


def run_partner_tests():
    """Run every test script included in the partner onboarding suite."""
    missing_tests = [str(test_path) for test_path in PARTNER_TESTS if not test_path.exists()]
    if missing_tests:
        raise FileNotFoundError(f"Partner test scripts not found: {missing_tests}")

    command = [
        sys.executable,
        "-m",
        "pytest",
        *(str(test_path) for test_path in PARTNER_TESTS),
        "-v",
    ]
    print(f"Running partner test suite: {[path.name for path in PARTNER_TESTS]}")
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def test_partner_onboarding_suite():
    """Pytest entry point for the complete partner onboarding suite."""
    return_code = run_partner_tests()
    assert return_code == 0, f"Partner test suite failed with exit code {return_code}"


if __name__ == "__main__":
    raise SystemExit(run_partner_tests())
