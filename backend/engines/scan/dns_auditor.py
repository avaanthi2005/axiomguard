import dns.resolver
import dns.zone
import dns.query

def audit_dns(host: str):
    issues = []
    dns_risk = 0
    results = {}

    # Check SPF record
    try:
        answers = dns.resolver.resolve(host, 'TXT')
        spf_found = any('v=spf1' in str(r) for r in answers)
        results['spf'] = spf_found
        if not spf_found:
            issues.append("Missing SPF record — domain can be spoofed in emails")
            dns_risk += 20
    except:
        results['spf'] = False
        issues.append("Could not retrieve TXT records")
        dns_risk += 15

    # Check DMARC record
    try:
        dmarc_host = f"_dmarc.{host}"
        answers = dns.resolver.resolve(dmarc_host, 'TXT')
        dmarc_found = any('v=DMARC1' in str(r) for r in answers)
        results['dmarc'] = dmarc_found
        if not dmarc_found:
            issues.append("Missing DMARC record — no email authentication policy")
            dns_risk += 20
    except:
        results['dmarc'] = False
        issues.append("Missing DMARC record — no email authentication policy")
        dns_risk += 20

    # Check MX records
    try:
        mx_records = dns.resolver.resolve(host, 'MX')
        results['mx_records'] = [str(r.exchange) for r in mx_records]
        results['mx_count'] = len(results['mx_records'])
    except:
        results['mx_records'] = []
        results['mx_count'] = 0
        issues.append("No MX records found")
        dns_risk += 10

    # Check A record
    try:
        a_records = dns.resolver.resolve(host, 'A')
        results['a_records'] = [str(r) for r in a_records]
    except:
        results['a_records'] = []
        issues.append("No A records found")
        dns_risk += 15

    # Zone transfer check
    try:
        ns_records = dns.resolver.resolve(host, 'NS')
        for ns in ns_records:
            try:
                zone = dns.zone.from_xfr(
                    dns.query.xfr(str(ns), host, timeout=3)
                )
                if zone:
                    issues.append(f"CRITICAL: Zone transfer allowed on {ns} — full DNS exposed to attackers")
                    dns_risk += 40
            except:
                pass
        results['zone_transfer'] = "Secure" if dns_risk < 40 else "VULNERABLE"
    except:
        results['zone_transfer'] = "Could not check"

    return {
        "dns_results": results,
        "issues": issues,
        "dns_risk_score": min(dns_risk, 100)
    }