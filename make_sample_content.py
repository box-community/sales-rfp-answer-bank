"""Generate sample sales PDFs into sample_content/ for hub testing.

Pure standard library - no dependencies. Run:

    python make_sample_content.py

Upload the resulting sample_content/ folder tree to Box (as "Sales Content"),
then set SALES_CONTENT_FOLDER_ID in .env to that folder's ID.
"""

from pathlib import Path

ROOT = Path("sample_content")

DOCUMENTS = {
    "RFP Responses/2025-Q1-Acme-RFP-Response.pdf": [
        "Acme Corp RFP Response - Q1 2025",
        "",
        "Enterprise Support SLA",
        "Our standard SLA for enterprise support is 99.9% uptime,",
        "with a 1-hour response time for Priority 1 incidents and",
        "a 4-hour response time for Priority 2 incidents. Named",
        "Customer Success Managers are included for all deals of",
        "200 seats or more.",
        "",
        "Security certifications",
        "We hold SOC 2 Type II, ISO 27001, and HIPAA attestations.",
        "Penetration tests are performed annually by an independent firm.",
    ],
    "RFP Responses/2024-Q3-Healthcare-Compliance-RFP.pdf": [
        "Healthcare Compliance RFP Response - Q3 2024",
        "",
        "Data residency for EU customers",
        "EU customer data can be stored exclusively in our Frankfurt",
        "and Amsterdam regions. We support data residency controls",
        "that prevent replication outside the EEA. GDPR Data Processing",
        "Agreements are available on request for all enterprise deals.",
        "",
        "We do not transfer EU personal data to the US without SCCs",
        "and customer-approved transfer mechanisms.",
    ],
    "Proposals/Enterprise-Platform-Proposal-Template.pdf": [
        "Enterprise Platform Proposal Template",
        "",
        "This template covers platform capabilities, implementation",
        "timeline (typically 6-8 weeks), and success criteria.",
        "Security certifications: SOC 2 Type II, ISO 27001, HIPAA.",
        "Standard enterprise support SLA: 99.9% uptime.",
    ],
    "Proposals/Mid-Market-Proposal-Template.pdf": [
        "Mid-Market Proposal Template",
        "",
        "Designed for 50-200 seat deployments. Includes standard",
        "onboarding, email support with next-business-day response,",
        "and access to the customer community.",
    ],
    "Competitive Intelligence/Win-Loss-Analysis-Q1-2025.pdf": [
        "Win-Loss Analysis - Q1 2025",
        "",
        "Primary win themes: security certifications, EU data residency,",
        "and transparent volume discounting. Primary loss themes:",
        "price sensitivity under 100 seats and missing industry templates.",
    ],
    "Competitive Intelligence/Competitor-Comparison-Matrix.pdf": [
        "Competitor Comparison Matrix",
        "",
        "Category          Us              Competitor A    Competitor B",
        "SOC 2 Type II     Yes             Yes             No",
        "ISO 27001         Yes             No              Yes",
        "EU residency      Yes             Limited         Yes",
        "99.9% SLA         Yes             99.5%           Yes",
    ],
    "Pricing/Enterprise-Pricing-Guide.pdf": [
        "Enterprise Pricing Guide",
        "",
        "List price: $45 per seat / month (annual commitment).",
        "",
        "Volume discount tiers for 500+ seat deals:",
        "  500-999 seats:   10% discount",
        "  1000-2499 seats: 15% discount",
        "  2500+ seats:     20% discount (requires VP approval)",
        "",
        "Multi-year commitments add an additional 5% discount.",
    ],
    "Pricing/Volume-Discount-Schedule.pdf": [
        "Volume Discount Schedule",
        "",
        "Seat band          Discount off list",
        "1-99               0%",
        "100-499            5%",
        "500-999            10%",
        "1000-2499          15%",
        "2500+              20%",
        "",
        "Discounts stack with multi-year commitments (max 25% total).",
    ],
}


def _content_stream(lines: list[str]) -> bytes:
    parts = ["BT", "/F1 11 Tf", "72 720 Td", "14 TL"]
    for line in lines:
        safe = line.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
        parts.append(f"({safe}) Tj")
        parts.append("T*")
    parts.append("ET")
    return ("\n".join(parts)).encode("latin-1")


def build_pdf(lines: list[str]) -> bytes:
    content = _content_stream(lines)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
        + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

    xref_pos = len(pdf)
    count = len(objects) + 1
    pdf += f"xref\n0 {count}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()

    pdf += (
        b"trailer\n<< /Size " + str(count).encode() + b" /Root 1 0 R >>\n"
        b"startxref\n" + str(xref_pos).encode() + b"\n%%EOF\n"
    )
    return bytes(pdf)


def main() -> None:
    written = 0
    for relative, lines in DOCUMENTS.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(build_pdf(lines))
        print(f"Wrote {path}")
        written += 1
    print(f"\nGenerated {written} sample PDFs under {ROOT}/")
    print("Upload this folder tree to Box as 'Sales Content'.")


if __name__ == "__main__":
    main()
