import email
import re

def extract_domain(address: str) -> str:
    match = re.search(r'@([\w.-]+)', address)
    return match.group(1).lower() if match else ""

def parse_email_headers(raw_email: str) -> dict:
    """
    Parses raw email text and checks for spoofing indicators.
    """
    try:
        msg = email.message_from_string(raw_email)
    except:
        return {"error": "Could not parse email headers"}

    from_field    = msg.get('From', '')
    reply_to      = msg.get('Reply-To', '')
    return_path   = msg.get('Return-Path', '')
    received      = msg.get('Received', '')
    subject       = msg.get('Subject', '')
    spf           = msg.get('Received-SPF', '')
    dkim          = msg.get('DKIM-Signature', '')

    from_domain    = extract_domain(from_field)
    replyto_domain = extract_domain(reply_to)
    return_domain  = extract_domain(return_path)

    issues = []
    risk_score = 0

    # Check From vs Reply-To mismatch
    if reply_to and from_domain and replyto_domain:
        if from_domain != replyto_domain:
            issues.append(f"Reply-To domain ({replyto_domain}) differs from From domain ({from_domain}) — spoofing indicator")
            risk_score += 35

    # Check From vs Return-Path mismatch
    if return_path and from_domain and return_domain:
        if from_domain != return_domain:
            issues.append(f"Return-Path domain ({return_domain}) differs from From domain — spoofing indicator")
            risk_score += 30

    # Check SPF
    if spf:
        if 'fail' in spf.lower():
            issues.append("SPF check FAILED — sender not authorized to send from this domain")
            risk_score += 40
        elif 'softfail' in spf.lower():
            issues.append("SPF softfail — sender may not be authorized")
            risk_score += 20
        elif 'pass' in spf.lower():
            risk_score = max(0, risk_score - 10)
    else:
        issues.append("No SPF verification found in headers")
        risk_score += 10

    # Check DKIM
    if not dkim:
        issues.append("No DKIM signature found — email authenticity unverified")
        risk_score += 15

    # Urgency keywords in subject
    urgency_words = ['urgent', 'immediate', 'verify', 'suspend', 'action required',
                     'limited time', 'act now', 'account closed', 'security alert']
    subject_lower = subject.lower()
    urgency_found = [w for w in urgency_words if w in subject_lower]
    if urgency_found:
        issues.append(f"Urgency keywords in subject: {', '.join(urgency_found)}")
        risk_score += len(urgency_found) * 10

    verdict = "SAFE"
    if risk_score >= 60:
        verdict = "DANGEROUS"
    elif risk_score >= 30:
        verdict = "SUSPICIOUS"

    return {
        "from": from_field,
        "from_domain": from_domain,
        "reply_to": reply_to,
        "return_path": return_path,
        "subject": subject,
        "spf_status": spf or "Not found",
        "dkim_present": bool(dkim),
        "issues": issues,
        "email_risk_score": min(risk_score, 100),
        "verdict": verdict
    }