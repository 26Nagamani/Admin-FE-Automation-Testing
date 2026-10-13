from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PARTNER_DATA_DIR = REPO_ROOT / "test_data" / "partner"
TEST_DATA_DOCS_DIR = REPO_ROOT / "test_data" / "docs"
ADD_PARTNER_DATA_FILE = PARTNER_DATA_DIR / "AddPartnerData.xlsx"
AGENT_DETAILS_DATA_FILE = PARTNER_DATA_DIR / "AgentDetailsData.xlsx"
PARTNER_MARKUP_DATA_FILE = PARTNER_DATA_DIR / "PartnerMarkupData.xlsx"
PARTNER_DOCS_DIR = TEST_DATA_DOCS_DIR
