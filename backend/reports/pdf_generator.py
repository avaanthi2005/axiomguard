from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

# Brand colors
BLUE       = colors.HexColor('#00d4ff')
PURPLE     = colors.HexColor('#c084fc')
GREEN      = colors.HexColor('#10b981')
ORANGE     = colors.HexColor('#f97316')
RED        = colors.HexColor('#ef4444')
YELLOW     = colors.HexColor('#f59e0b')
GRAY       = colors.HexColor('#94a3b8')
WHITE      = colors.white


def get_risk_color(level):
    level = str(level).upper()
    if level in ['CRITICAL', 'DANGER', 'DANGEROUS']: return RED
    if level in ['HIGH', 'WARNING']:                  return ORANGE
    if level in ['MEDIUM', 'CAUTION', 'SUSPICIOUS']:  return YELLOW
    return GREEN


def _base_styles():
    title_style = ParagraphStyle('title', fontSize=28, textColor=BLUE, alignment=TA_CENTER,
        fontName='Helvetica-Bold', spaceAfter=10)
    sub_style = ParagraphStyle('sub', fontSize=10, textColor=GRAY, alignment=TA_CENTER,
        fontName='Helvetica', spaceAfter=20)
    heading_style = ParagraphStyle('heading', fontSize=13, textColor=BLUE, fontName='Helvetica-Bold',
        spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle('body', fontSize=10, textColor=colors.HexColor('#334155'),
        fontName='Helvetica', spaceAfter=4, leading=16)
    return title_style, sub_style, heading_style, body_style


def _header(story, title_style, sub_style, subtitle):
    story.append(Paragraph("AXIOMGUARD", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(subtitle, sub_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 12))


def _footer(story, gray_style):
    story.append(HRFlowable(width="100%", thickness=1, color=BLUE))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "AXIOMGUARD &mdash; Because security should be absolute. | Generated automatically by AXIOMGUARD platform",
        gray_style
    ))


def _kv_table(data_pairs):
    table = Table(data_pairs, colWidths=[2*inch, 4.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (0,-1), BLUE),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#0f172a')),
        ('FONTNAME', (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    return table


def _clean_ai_text(text):
    return (text or '').replace('**', '').replace('*', '')


# ============================================================
# AXIOM // SCAN
# ============================================================
def generate_scan_report(scan_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)

    title_style, sub_style, heading_style, body_style = _base_styles()
    story = []

    _header(story, title_style, sub_style, "Security Audit Report &mdash; AXIOM//SCAN")

    axiom = scan_data.get('axiom_score', {}) or {}
    score = axiom.get('axiom_score', 0)
    level = axiom.get('level', 'UNKNOWN')

    summary_data = [
        ['Domain', scan_data.get('domain', 'N/A')],
        ['IP Address', scan_data.get('ip', 'N/A')],
        ['AxiomScore', f"{score} / 100"],
        ['Risk Level', level],
        ['Assessment', axiom.get('message', 'N/A')],
    ]
    story.append(_kv_table(summary_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("SCORE BREAKDOWN", heading_style))
    breakdown = axiom.get('breakdown', {}) or {}
    bd_data = [['Component', 'Contribution', 'Weight']]
    components = [
        ('Port Security', breakdown.get('port_contribution', 0), '30%'),
        ('SSL/TLS', breakdown.get('ssl_contribution', 0), '25%'),
        ('DNS Hygiene', breakdown.get('dns_contribution', 0), '20%'),
        ('CVE Risk', breakdown.get('cve_contribution', 0), '25%'),
    ]
    for name, val, weight in components:
        bd_data.append([name, str(val), weight])
    bd_table = Table(bd_data, colWidths=[2.5*inch, 2*inch, 2*inch])
    bd_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0,0), (-1,0), BLUE),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(bd_table)
    story.append(Spacer(1, 16))

    story.append(Paragraph("PORT SCAN RESULTS", heading_style))
    open_ports = (scan_data.get('port_scan', {}) or {}).get('open_ports', [])
    if open_ports:
        port_data = [['Port', 'Service', 'Status', 'Risk Level']]
        for p in open_ports:
            port_data.append([str(p.get('port')), p.get('service', ''), 'OPEN', p.get('risk_level', '')])
        port_table = Table(port_data, colWidths=[1*inch, 2*inch, 1.5*inch, 2*inch])
        port_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), BLUE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ]))
        story.append(port_table)
    else:
        story.append(Paragraph("No commonly targeted ports found open.", body_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("SSL / TLS INSPECTION", heading_style))
    ssl = scan_data.get('ssl_inspection', {}) or {}
    ssl_data = [
        ['Valid', 'Yes' if ssl.get('ssl_valid') else 'No'],
        ['Grade', ssl.get('grade', 'N/A')],
        ['Issuer', ssl.get('issuer', 'N/A')],
        ['Days Until Expiry', str(ssl.get('days_until_expiry', 'N/A'))],
        ['Expiry Date', ssl.get('expiry_date', 'N/A')],
    ]
    story.append(_kv_table(ssl_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("DNS AUDIT", heading_style))
    dns = scan_data.get('dns_audit', {}) or {}
    dns_results = dns.get('dns_results', {}) or {}
    dns_data = [
        ['SPF Record', 'Present' if dns_results.get('spf') else 'Missing'],
        ['DMARC Record', 'Present' if dns_results.get('dmarc') else 'Missing'],
        ['Zone Transfer', dns_results.get('zone_transfer', 'N/A')],
        ['MX Records', f"{dns_results.get('mx_count', 0)} found"],
    ]
    story.append(_kv_table(dns_data))

    dns_issues = dns.get('issues', [])
    if dns_issues:
        story.append(Spacer(1, 8))
        for issue in dns_issues:
            story.append(Paragraph(f"[!] {issue}", body_style))
    story.append(Spacer(1, 16))

    ai_explanation = scan_data.get('ai_explanation', '') or ''
    if ai_explanation and 'unavailable' not in ai_explanation.lower():
        story.append(Paragraph("AI SECURITY ANALYSIS", heading_style))
        story.append(Paragraph(_clean_ai_text(ai_explanation), body_style))
        story.append(Spacer(1, 16))

    _footer(story, ParagraphStyle('footer', fontSize=8, textColor=GRAY, alignment=TA_CENTER))
    doc.build(story)
    return buffer.getvalue()


# ============================================================
# AXIOM // PHISH
# ============================================================
def generate_phish_report(phish_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)

    title_style, sub_style, heading_style, body_style = _base_styles()
    story = []

    _header(story, title_style, sub_style, "Phishing Analysis Report &mdash; AXIOM//PHISH")

    ua = phish_data.get('url_analysis') or {}
    ea = phish_data.get('email_analysis') or {}

    if ua:
        summary_data = [
            ['URL', ua.get('url', 'N/A')],
            ['Domain', ua.get('domain', 'N/A')],
            ['Verdict', ua.get('verdict', 'N/A')],
            ['Risk Score', f"{ua.get('risk_score', 0)} / 100"],
        ]
        story.append(_kv_table(summary_data))
        story.append(Spacer(1, 16))

        story.append(Paragraph("URL FEATURE ANALYSIS", heading_style))
        features = (ua.get('feature_analysis') or {}).get('features', {}) or {}
        feat_data = [['Feature', 'Value']]
        for k, v in features.items():
            feat_data.append([k.replace('_', ' ').title(), str(v)])
        if len(feat_data) > 1:
            feat_table = Table(feat_data, colWidths=[3.5*inch, 3*inch])
            feat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
                ('TEXTCOLOR', (0,0), (-1,0), BLUE),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#0f172a')),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(feat_table)
        story.append(Spacer(1, 16))

        story.append(Paragraph("ENTROPY & HOMOGLYPH CHECK", heading_style))
        entropy = ua.get('entropy', {}) or {}
        homoglyph = ua.get('homoglyph_check', {}) or {}
        eh_data = [
            ['Entropy Value', str(entropy.get('value', 'N/A'))],
            ['Entropy Risk', str((entropy.get('risk') or {}).get('risk', 'N/A'))],
            ['Typosquatting Detected', 'Yes' if homoglyph.get('is_typosquat') else 'No'],
        ]
        story.append(_kv_table(eh_data))
        story.append(Spacer(1, 16))

        ml_pred = ua.get('ml_model_prediction')
        if ml_pred:
            story.append(Paragraph("ML MODEL PREDICTION", heading_style))
            ml_data = [
                ['Model Verdict', str(ml_pred)],
                ['Confidence', f"{ua.get('ml_confidence', 'N/A')}%"],
                ['Model Type', 'Random Forest Classifier'],
                ['Features Used', '12 URL structural features'],
            ]
            story.append(_kv_table(ml_data))
            story.append(Spacer(1, 16))

        risk_flags = (ua.get('feature_analysis') or {}).get('risk_flags', [])
        if risk_flags:
            story.append(Paragraph("RISK FLAGS", heading_style))
            for flag in risk_flags:
                story.append(Paragraph(f"[!] {flag}", body_style))
            story.append(Spacer(1, 16))

    if ea:
        story.append(Paragraph("EMAIL HEADER ANALYSIS", heading_style))
        ea_data = [
            ['Verdict', ea.get('verdict', 'N/A')],
            ['Risk Score', f"{ea.get('email_risk_score', 0)} / 100"],
            ['From', ea.get('from', 'N/A')],
            ['Reply-To', ea.get('reply_to', 'N/A')],
            ['SPF Status', ea.get('spf_status', 'N/A')],
            ['DKIM Present', 'Yes' if ea.get('dkim_present') else 'No'],
        ]
        story.append(_kv_table(ea_data))

        ea_issues = ea.get('issues', [])
        if ea_issues:
            story.append(Spacer(1, 8))
            for issue in ea_issues:
                story.append(Paragraph(f"[!] {issue}", body_style))
        story.append(Spacer(1, 16))

    ai_explanation = phish_data.get('ai_explanation', '') or ''
    if ai_explanation and 'unavailable' not in ai_explanation.lower():
        story.append(Paragraph("AI SECURITY ANALYSIS", heading_style))
        story.append(Paragraph(_clean_ai_text(ai_explanation), body_style))
        story.append(Spacer(1, 16))

    _footer(story, ParagraphStyle('footer', fontSize=8, textColor=GRAY, alignment=TA_CENTER))
    doc.build(story)
    return buffer.getvalue()


# ============================================================
# AXIOM // GUARD
# ============================================================
def generate_guard_report(guard_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)

    title_style, sub_style, heading_style, body_style = _base_styles()
    story = []

    _header(story, title_style, sub_style, "Website Behavior Report &mdash; AXIOM//GUARD")

    summary_data = [
        ['URL', guard_data.get('url', 'N/A')],
        ['Domain', guard_data.get('domain', 'N/A')],
        ['Verdict', guard_data.get('verdict', 'N/A')],
        ['Guard Score', f"{guard_data.get('guard_score', 0)} / 100"],
        ['Action', guard_data.get('action', 'N/A')],
    ]
    story.append(_kv_table(summary_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("SCORE BREAKDOWN", heading_style))
    breakdown = guard_data.get('score_breakdown', {}) or {}
    bd_data = [
        ['Static Contribution', str(breakdown.get('static_contribution', 'N/A'))],
        ['Behavior Contribution', str(breakdown.get('behavior_contribution', 'N/A'))],
        ['Reputation Contribution', str(breakdown.get('reputation_contribution', 'N/A'))],
        ['False Positive Adjusted', 'Yes' if guard_data.get('false_positive_adjusted') else 'No'],
    ]
    story.append(_kv_table(bd_data))
    story.append(Spacer(1, 16))

    story.append(Paragraph("STATIC HTML ANALYSIS", heading_style))
    static = guard_data.get('static_analysis', {}) or {}
    static_data = [
        ['Page Title', static.get('page_title', 'N/A')],
        ['Total Scripts', str(static.get('total_scripts', 'N/A'))],
        ['External Scripts', str(static.get('external_scripts', 'N/A'))],
        ['Total iFrames', str(static.get('total_iframes', 'N/A'))],
    ]
    story.append(_kv_table(static_data))
    static_signals = static.get('signals', [])
    if static_signals:
        story.append(Spacer(1, 8))
        for s in static_signals:
            story.append(Paragraph(f"[!] {s.get('description', '')}", body_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("BEHAVIORAL ANALYSIS", heading_style))
    behavior = guard_data.get('behavior_analysis', {}) or {}
    behavior_data = [
        ['Redirect Count', str(behavior.get('redirect_count', 'N/A'))],
        ['Headers Present', str(len(behavior.get('security_headers_present', []) or []))],
        ['Headers Missing', str(len(behavior.get('security_headers_missing', []) or []))],
    ]
    story.append(_kv_table(behavior_data))
    behavior_signals = behavior.get('signals', [])
    if behavior_signals:
        story.append(Spacer(1, 8))
        for s in behavior_signals:
            story.append(Paragraph(f"[!] {s.get('description', '')}", body_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("DOMAIN REPUTATION", heading_style))
    reputation = guard_data.get('reputation', {}) or {}
    rep_data = [
        ['Reputation Score', str(reputation.get('reputation_score', 'N/A'))],
        ['Trust Level', str(reputation.get('trust_level', 'N/A'))],
        ['Domain Age', f"{reputation.get('domain_age_days', 'Unknown')} days" if reputation.get('domain_age_days', 0) > 0 else 'Unknown'],
        ['TLD Risk Score', f"{reputation.get('tld_risk', 'N/A')} / 10"],
        ['Domain Entropy', str(reputation.get('domain_entropy', 'N/A'))],
    ]
    story.append(_kv_table(rep_data))
    rep_signals = reputation.get('signals', [])
    if rep_signals:
        story.append(Spacer(1, 8))
        for s in rep_signals:
            story.append(Paragraph(f"[!] {s}", body_style))
    story.append(Spacer(1, 16))

    ai_explanation = guard_data.get('ai_explanation', '') or ''
    if ai_explanation and 'unavailable' not in ai_explanation.lower():
        story.append(Paragraph("AI SECURITY ANALYSIS", heading_style))
        story.append(Paragraph(_clean_ai_text(ai_explanation), body_style))
        story.append(Spacer(1, 16))

    _footer(story, ParagraphStyle('footer', fontSize=8, textColor=GRAY, alignment=TA_CENTER))
    doc.build(story)
    return buffer.getvalue()