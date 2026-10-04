import ssl
import socket
from datetime import datetime

def inspect_ssl(host: str):
    try:
        context = ssl.create_default_context()
        conn = context.wrap_socket(
            socket.socket(socket.AF_INET),
            server_hostname=host
        )
        conn.settimeout(5)
        conn.connect((host, 443))
        cert = conn.getpeercert()
        conn.close()

        # Get expiry date
        expire_str = cert.get('notAfter', '')
        expire_date = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z")
        days_left = (expire_date - datetime.utcnow()).days

        # Get issuer
        issuer_info = dict(x[0] for x in cert.get('issuer', []))
        issuer = issuer_info.get('organizationName', 'Unknown')

        # Get subject
        subject_info = dict(x[0] for x in cert.get('subject', []))
        common_name = subject_info.get('commonName', host)

        # Get protocol version
        protocol = conn.version() if hasattr(conn, 'version') else "Unknown"

        # Calculate SSL risk score
        ssl_risk = 0
        issues = []

        if days_left < 0:
            ssl_risk += 50
            issues.append("Certificate is EXPIRED")
        elif days_left < 30:
            ssl_risk += 30
            issues.append(f"Certificate expires in {days_left} days")
        elif days_left < 90:
            ssl_risk += 10
            issues.append(f"Certificate expires soon ({days_left} days)")

        # Grade assignment
        if ssl_risk == 0:
            grade = "A"
        elif ssl_risk <= 10:
            grade = "B"
        elif ssl_risk <= 20:
            grade = "C"
        elif ssl_risk <= 30:
            grade = "D"
        else:
            grade = "F"

        return {
            "ssl_valid": True,
            "issuer": issuer,
            "common_name": common_name,
            "days_until_expiry": days_left,
            "expiry_date": expire_str,
            "grade": grade,
            "issues": issues,
            "ssl_risk_score": ssl_risk
        }

    except ssl.SSLError as e:
        return {
            "ssl_valid": False,
            "error": f"SSL Error: {str(e)}",
            "grade": "F",
            "ssl_risk_score": 50,
            "issues": ["SSL certificate invalid or missing"]
        }
    except Exception as e:
        return {
            "ssl_valid": False,
            "error": str(e),
            "grade": "F",
            "ssl_risk_score": 40,
            "issues": ["Could not connect to HTTPS"]
        }