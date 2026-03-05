"""Application steps by system type."""

from typing import List


def apply_steps(system: str) -> List[str]:
    s = (system or "").lower()
    if "ucas" in s:
        return [
            "Apply via UCAS.",
            "Choose the course and university on UCAS.",
            "Write a personal statement and add references.",
            "Submit and track decisions in UCAS.",
        ]
    if "studielink" in s:
        return [
            "Create a Studielink account.",
            "Add the chosen programme and submit your application.",
            "Complete extra steps in the university portal (if required).",
            "Upload documents and track status.",
        ]
    if "uni-assist" in s or "direct" in s:
        return [
            "Check the programme page: it may be 'direct' or via uni-assist.",
            "Prepare documents (transcript, passport, language proof, CV, motivation letter).",
            "Submit before the deadline and monitor updates.",
        ]
    if "universityadmissions" in s:
        return [
            "Apply via Universityadmissions.se (create an account).",
            "Select programmes and upload required documents.",
            "Submit and track status in the portal.",
        ]
    if "studyinfo" in s:
        return [
            "Apply via Finland Studyinfo (joint application/portal).",
            "Select programmes and submit required documents.",
            "Track status in the portal / university system.",
        ]
    if "optagelse" in s:
        return [
            "Check Optagelse.dk (Danish admissions portal) and the university's instructions.",
            "Submit application + required documents.",
            "Track status via the relevant portal.",
        ]
    if "parcoursup" in s:
        return [
            "Check Parcoursup and/or the university portal depending on programme type.",
            "Prepare documents (transcript, language proof, motivation letter).",
            "Submit before deadlines and track updates.",
        ]
    return [
        "Check the official programme page and application portal.",
        "Prepare documents (transcript, passport, language proof, CV, motivation letter).",
        "Submit before the deadline and monitor updates.",
    ]
