import socket

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-Alt",
    8443: "HTTPS-Alt",
    27017: "MongoDB",
    5900: "VNC",
    2375: "Docker",
    9200: "Elasticsearch"
}

PORT_RISK = {
    21: 30,   # FTP - unencrypted
    22: 20,   # SSH - brute force target
    23: 40,   # Telnet - very insecure
    25: 25,   # SMTP - spam relay
    53: 15,   # DNS - zone transfer risk
    80: 10,   # HTTP - normal but unencrypted
    110: 20,  # POP3 - email exposure
    143: 20,  # IMAP - email exposure
    443: 0,   # HTTPS - safe
    445: 40,  # SMB - ransomware target
    3306: 35, # MySQL - db exposed
    3389: 40, # RDP - brute force target
    5432: 35, # PostgreSQL - db exposed
    6379: 35, # Redis - often unsecured
    8080: 15, # HTTP-Alt
    8443: 5,  # HTTPS-Alt
    27017: 35,# MongoDB - often unsecured
    5900: 30, # VNC - remote access
    2375: 45, # Docker - critical exposure
    9200: 35  # Elasticsearch - data exposure
}

def scan_ports(host: str):
    open_ports = []
    total_risk = 0

    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror:
        return {"error": "Could not resolve domain", "open_ports": [], "port_risk_score": 0}

    for port, service in COMMON_PORTS.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()

            if result == 0:
                risk = PORT_RISK.get(port, 10)
                total_risk += risk
                open_ports.append({
                    "port": port,
                    "service": service,
                    "status": "OPEN",
                    "risk_weight": risk,
                    "risk_level": "HIGH" if risk >= 35 else "MEDIUM" if risk >= 20 else "LOW"
                })
        except:
            pass

    return {
        "ip": ip,
        "open_ports": open_ports,
        "port_risk_score": min(total_risk, 100)
    }