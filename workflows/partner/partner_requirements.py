def normalize_partner_type(value: str) -> str:
    return " ".join(str(value or "").strip().lower().replace("_", " ").split())


def normalize_referral_source(value: str) -> str:
    normalized = "".join(
        character if character.isalnum() else " "
        for character in str(value or "").lower()
    )
    return " ".join(normalized.split())


COMMON_FIELD_ALIASES = {
    "account_holder_name": "account_holder_name",
    "pan_number": "pan_number",
    "phone_number": "phone_number",
    "registered_mobile (Bank)": "registered_mobile",
    "registered_mobile": "registered_mobile",
    "address": "address",
    "gst_number": "gst_number",
    "buisness_name": "buisness_name",
    "business_name": "buisness_name",
    "ifsc_code": "ifsc_code",
    "ifsc": "ifsc_code",
    "bank_account_number": "bank_account_number",
    "cin_llpin": "cin_llpin",
    "referral_employee_id": "referral_employee_id",
    "referral_employee_email_id": "referral_employee_email_id",
}

DOCUMENT_FILE_ALIASES = {
    "aadhar": "aadhar_image.png",
    "aadharcard": "aadhar_image.png",
    "aadharimage": "aadhar_image.png",
    "aadharcardimage": "aadhar_image.png",
    "aadharcarddirectorimage": "aadhar_card_director_image.png",
    "directorpartneraadharcard": "aadhar_card_director_image.png",
    "directorpartneraadharcardimage": "aadhar_card_director_image.png",
    "aoa": "aoa_image.png",
    "aoaimage": "aoa_image.png",
    "certificateofincorporation": "certificate_of_incorporation.png",
    "corporategst": "gst_image_corporate.png",
    "corporategstcertificate": "gst_certificate.png",
    "gstcertificate": "gst_certificate.png",
    "gstimagecorporate": "gst_image_corporate.png",
    "directorpartner": "pan_card_director_image.png",
    "directorpartnerpan": "pan_card_director_image.png",
    "directorpartnerpancard": "pan_card_director_image.png",
    "directorpartnerpancardimage": "pan_card_director_image.png",
    "llpagreement": "llp_agreement.png",
    "llpcertificate": "llp_certificate.png",
    "moa": "moa_image.png",
    "moaimage": "moa_image.png",
    "pan": "pan_image.png",
    "pancard": "pan_card_image.png",
    "pancardimage": "pan_card_image.png",
    "panimage": "pan_image.png",
    "partnershipdeed": "partnership_deed.png",
    "udaycertificate": "uday_certificate_image.png",
    "udaycertificateimage": "uday_certificate_image.png",
    "udyamudaycertificate": "uday_certificate_image.png",
    "udyamudaycertificateimage": "uday_certificate_image.png",
}


PARTNER_TYPE_REQUIREMENTS = {
    "individual": {
        "fields": [
            "account_holder_name",
            "pan_number",
            "phone_number",
            "address",
            "gst_number",
            "buisness_name",
            "ifsc_code",
            "bank_account_number",
        ],
        "documents": [
            "aadhar_image",
            "gst_image_corporate",
            "pan_card_director_image",
            "aadhar_card_director_image",
            "pan_image",
            "uday_certificate_image",
        ],
    },
    "limited liability partnership (llp)": {
        "fields": [
            "bank_account_number",
            "gst_number",
            "phone_number",
            "cin_llpin",
            "pan_number",
            "ifsc_code",
            "account_holder_name",
            "address",
            "buisness_name",
        ],
        "documents": [
            "pan_image",
            "aadhar_image",
            "pan_card_director_image",
            "llp_certificate",
            "gst_image_corporate",
            "llp_agreement",
            "aadhar_card_director_image",
        ],
    },
    "llp": {
        "fields": [
            "bank_account_number",
            "gst_number",
            "phone_number",
            "cin_llpin",
            "pan_number",
            "ifsc_code",
            "account_holder_name",
            "address",
            "buisness_name",
        ],
        "documents": [
            "pan_image",
            "aadhar_image",
            "pan_card_director_image",
            "llp_certificate",
            "gst_image_corporate",
            "llp_agreement",
            "aadhar_card_director_image",
        ],
    },
    "partnership firm": {
        "fields": [
            "gst_number",
            "pan_number",
            "phone_number",
            "account_holder_name",
            "buisness_name",
            "address",
            "ifsc_code",
            "bank_account_number",
        ],
        "documents": [
            "pan_image",
            "llp_agreement",
            "aadhar_image",
            "pan_card_director_image",
            "aadhar_card_director_image",
            "partnership_deed",
            "gst_image_corporate",
            "llp_certificate",
        ],
    },
    "private limited company": {
        "fields": [
            "cin_llpin",
            "phone_number",
            "ifsc_code",
            "address",
            "gst_number",
            "pan_number",
            "buisness_name",
            "bank_account_number",
            "account_holder_name",
        ],
        "documents": [
            "aadhar_card_director_image",
            "aadhar_image",
            "gst_image_corporate",
            "moa_image",
            "certificate_of_incorporation",
            "aoa_image",
            "pan_card_director_image",
            "pan_image",
        ],
    },
    "sole proprietor": {
        "fields": [
            "bank_account_number",
            "address",
            "pan_number",
            "buisness_name",
            "phone_number",
            "gst_number",
            "ifsc_code",
            "account_holder_name",
        ],
        "documents": [
            "uday_certificate_image",
            "pan_card_director_image",
            "pan_image",
            "aadhar_image",
            "gst_image_corporate",
            "aadhar_card_director_image",
        ],
    },
    "soleproperitor": {
        "fields": [
            "bank_account_number",
            "address",
            "pan_number",
            "buisness_name",
            "phone_number",
            "gst_number",
            "ifsc_code",
            "account_holder_name",
        ],
        "documents": [
            "uday_certificate_image",
            "pan_card_director_image",
            "pan_image",
            "aadhar_image",
            "gst_image_corporate",
            "aadhar_card_director_image",
        ],
    },
}


REFERRAL_SOURCE_REQUIREMENTS = {
    "internal sales team": {
        "fields": [
            "referral_employee_id",
            "referral_employee_email_id",
        ],
        "documents": [],
    },
}


def get_partner_requirements(partner_type: str, referral_source: str = ""):
    normalized = normalize_partner_type(partner_type)
    partner_requirements = PARTNER_TYPE_REQUIREMENTS.get(normalized)
    if not partner_requirements:
        return None

    requirements = {
        "fields": list(partner_requirements["fields"]),
        "documents": list(partner_requirements["documents"]),
    }
    referral_requirements = REFERRAL_SOURCE_REQUIREMENTS.get(
        normalize_referral_source(referral_source)
    )
    if referral_requirements:
        requirements["fields"].extend(referral_requirements["fields"])
        requirements["documents"].extend(referral_requirements["documents"])
    return requirements


def document_key(value: str) -> str:
    return "".join(ch for ch in str(value or "").lower() if ch.isalnum())


def get_document_file_name(document_name: str):
    return DOCUMENT_FILE_ALIASES.get(document_key(document_name))
