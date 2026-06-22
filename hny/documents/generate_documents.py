from pathlib import Path
from textwrap import wrap


PAGE_W = 595
PAGE_H = 842

COLORS = {
    "blue": (0.40, 0.42, 0.53),
    "slate": (0.47, 0.54, 0.64),
    "teal": (0.57, 0.71, 0.69),
    "celadon": (0.70, 0.79, 0.67),
    "pearl": (0.91, 0.87, 0.71),
    "ink": (0.12, 0.14, 0.22),
    "soft": (0.30, 0.33, 0.42),
    "mist": (0.97, 0.97, 0.95),
    "white": (1, 1, 1),
}


def rgb(name):
    return COLORS[name]


def esc(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


class Canvas:
    def __init__(self):
        self.ops = []

    def color(self, name):
        r, g, b = rgb(name)
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg")

    def stroke_color(self, name):
        r, g, b = rgb(name)
        self.ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG")

    def rect(self, x, y, w, h, fill="white", stroke=None, width=0.8):
        self.color(fill)
        if stroke:
            self.stroke_color(stroke)
            self.ops.append(f"{width:.2f} w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re B")
        else:
            self.ops.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")

    def line(self, x1, y1, x2, y2, color="teal", width=1):
        self.stroke_color(color)
        self.ops.append(f"{width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def text(self, x, y, text, size=10, font="F1", color="ink"):
        self.color(color)
        self.ops.append(f"BT /{font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({esc(text)}) Tj ET")

    def paragraph(self, x, y, text, width_chars=70, size=9.5, leading=13, font="F1", color="soft"):
        lines = wrap(text, width_chars)
        for i, line in enumerate(lines):
            self.text(x, y - i * leading, line, size, font, color)
        return y - len(lines) * leading

    def chip(self, x, y, text, w=None):
        w = w or max(42, len(text) * 5.2 + 18)
        self.rect(x, y - 14, w, 20, fill="mist", stroke="teal", width=0.45)
        self.text(x + 8, y - 8, text, 8, "F2", "blue")
        return x + w + 6

    def commands(self):
        return "\n".join(self.ops)


def build_pdf(pages, output):
    objects = []

    def add(obj):
        objects.append(obj)
        return len(objects)

    catalog_id = add("<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add("")
    font_regular = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    font_bold = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    page_ids = []

    for content in pages:
        stream = content.encode("latin-1", "replace")
        content_id = add(f"<< /Length {len(stream)} >>\nstream\n{content}\nendstream")
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
            f"/Resources << /Font << /F1 {font_regular} 0 R /F2 {font_bold} 0 R >> >> "
            f"/Contents {content_id} 0 R >>"
        )
        page_ids.append(page_id)

    objects[pages_id - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {len(page_ids)} >>"

    output = Path(output)
    pdf = ["%PDF-1.4\n"]
    offsets = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(sum(len(part.encode("latin-1", "replace")) for part in pdf))
        pdf.append(f"{i} 0 obj\n{obj}\nendobj\n")

    xref_at = sum(len(part.encode("latin-1", "replace")) for part in pdf)
    pdf.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.append(f"{offset:010d} 00000 n \n")
    pdf.append(f"trailer\n<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\nstartxref\n{xref_at}\n%%EOF\n")
    output.write_bytes("".join(pdf).encode("latin-1", "replace"))


def resume_page():
    c = Canvas()
    c.rect(0, 0, PAGE_W, PAGE_H, "white")
    c.rect(0, 0, 184, PAGE_H, "blue")
    c.rect(184, 790, 411, 52, "mist")
    c.rect(32, 742, 76, 76, "teal")
    c.text(49, 773, "TN", 28, "F2", "white")
    c.text(212, 795, "TANISHA CHANDRAKANT NALAWADE", 19, "F2", "ink")
    c.text(212, 774, "Java Full Stack Developer | Freelance Web Developer", 10.5, "F2", "blue")
    c.paragraph(
        212,
        748,
        "Business-focused Java Full Stack Developer creating premium responsive websites, REST-ready backend foundations, and polished user interfaces for real client projects.",
        78,
        9.5,
        13,
    )

    c.text(28, 700, "CONTACT", 12, "F2", "pearl")
    contact = [
        "Email: nalawadetanisha5@gmail.com",
        "Phone: 7387479140",
        "GitHub: github.com/Tanisha804",
        "LinkedIn: linkedin.com/in/tanisha-nalawade",
        "Location: Maharashtra, India",
    ]
    y = 678
    for item in contact:
        y = c.paragraph(28, y, item, 28, 8.4, 11, color="white") - 4

    c.text(28, 520, "CORE STACK", 12, "F2", "pearl")
    y = 498
    for skill in ["Java", "Spring Boot", "REST APIs", "MySQL", "HTML5", "CSS3", "JavaScript", "Git", "Responsive UI", "SEO Basics"]:
        c.text(28, y, "- " + skill, 8.8, "F1", "white")
        y -= 15

    c.text(28, 300, "STRENGTHS", 12, "F2", "pearl")
    y = 278
    for item in ["Clean architecture", "Business-first thinking", "Fast learner", "Clear communication", "Detail-oriented UI"]:
        c.text(28, y, "- " + item, 8.8, "F1", "white")
        y -= 15

    c.text(212, 690, "PROFILE", 12, "F2", "blue")
    c.line(212, 682, 555, 682, "teal", 1)
    y = c.paragraph(
        212,
        662,
        "I build websites and web applications that help clients look professional, explain their services clearly, and capture enquiries. My work combines responsive frontend implementation with Java backend fundamentals and practical database knowledge.",
        78,
        9.3,
        13,
    )

    c.text(212, y - 10, "FEATURED PROJECT EXPERIENCE", 12, "F2", "blue")
    c.line(212, y - 18, 555, y - 18, "teal", 1)
    y -= 42
    projects = [
        ("Premium Freelancer Portfolio Website", "Designed and developed a multi-page Ocean Mist themed portfolio with lead capture, enquiry validation, project filtering, responsive sections, SEO tags, downloadable documents, and polished UI animations."),
        ("Business Website & Landing Page Concepts", "Created conversion-focused layouts for service businesses with trust indicators, CTA systems, service previews, process sections, testimonials, and mobile-first structure."),
        ("Java Backend / API Dashboard Concept", "Planned REST API and dashboard-style interfaces with Java, Spring Boot patterns, MySQL-ready data thinking, and clean module separation."),
    ]
    for title, body in projects:
        c.text(212, y, title, 10.2, "F2", "ink")
        y = c.paragraph(226, y - 14, body, 72, 8.8, 12, color="soft") - 6

    c.text(212, y - 8, "TECHNICAL SKILLS", 12, "F2", "blue")
    c.line(212, y - 16, 555, y - 16, "teal", 1)
    y -= 42
    x = 212
    for skill in ["Java", "Spring Boot", "REST API", "MySQL", "HTML", "CSS", "JavaScript", "Git", "SEO", "Responsive Design"]:
        if x > 500:
            x = 212
            y -= 28
        x = c.chip(x, y, skill)

    y -= 46
    c.text(212, y, "EDUCATION & TRAINING", 12, "F2", "blue")
    c.line(212, y - 8, 555, y - 8, "teal", 1)
    c.paragraph(212, y - 28, "Add degree, college, university, year, score, Java/web development training, certifications, and internship details here.", 78, 8.9, 12)

    c.rect(212, 44, 343, 44, "mist", stroke="teal", width=0.5)
    c.text(226, 68, "Freelance Services", 10, "F2", "blue")
    c.text(226, 52, "Business websites | Portfolio websites | REST APIs | Full stack apps | Maintenance", 8.5, "F1", "soft")
    return c.commands()


def portfolio_pages():
    pages = []
    c = Canvas()
    c.rect(0, 0, PAGE_W, PAGE_H, "white")
    c.rect(0, 650, PAGE_W, 192, "blue")
    c.rect(360, 650, 235, 192, "teal")
    c.text(44, 772, "TANISHA NALAWADE", 24, "F2", "white")
    c.text(44, 742, "Java Full Stack Developer", 14, "F2", "pearl")
    c.paragraph(44, 710, "Premium web development portfolio for business websites, Java backend concepts, REST APIs, responsive UI, and lead-focused digital experiences.", 62, 11, 16, color="white")
    c.rect(44, 604, 160, 34, "pearl")
    c.text(62, 616, "PORTFOLIO 2026", 12, "F2", "blue")

    c.text(44, 560, "CAPABILITIES", 13, "F2", "blue")
    x = 44
    y = 532
    for item in ["Business Websites", "Landing Pages", "Portfolio Sites", "E-Commerce UI", "Java Backend", "REST APIs", "Full Stack Apps", "Maintenance"]:
        if x > 440:
            x = 44
            y -= 34
        x = c.chip(x, y, item, max(92, len(item) * 5.2 + 20))

    c.text(44, 420, "SELECTED CASE STUDIES", 13, "F2", "blue")
    cards = [
        ("01", "Growth Studio Website", "Conversion-focused website for service businesses with trust strips, CTA sections, process flow, testimonials, and SEO-ready structure.", "HTML | CSS Grid | JavaScript | SEO"),
        ("02", "Modern Storefront System", "E-commerce UI concept with product-first hierarchy, category sections, trust messaging, responsive cards, and checkout-ready direction.", "Responsive UI | JavaScript | MySQL-ready"),
        ("03", "API Analytics Dashboard", "Java backend and dashboard concept for API status, admin analytics, REST communication, and scalable module planning.", "Java | Spring Boot | REST API | Dashboard"),
    ]
    y = 386
    for num, title, body, stack in cards:
        c.rect(44, y - 74, 507, 86, "mist", stroke="teal", width=0.55)
        c.rect(60, y - 45, 42, 42, "blue")
        c.text(73, y - 22, num, 13, "F2", "white")
        c.text(120, y - 12, title, 11.5, "F2", "ink")
        c.paragraph(120, y - 30, body, 72, 8.7, 11.5)
        c.text(120, y - 66, stack, 8.7, "F2", "blue")
        y -= 110

    c.rect(44, 36, 507, 42, "blue")
    c.text(60, 58, "Contact: nalawadetanisha5@gmail.com | 7387479140 | github.com/Tanisha804", 9, "F2", "white")
    pages.append(c.commands())

    c = Canvas()
    c.rect(0, 0, PAGE_W, PAGE_H, "white")
    c.rect(0, 782, PAGE_W, 60, "blue")
    c.text(44, 804, "PROJECT DELIVERY SNAPSHOT", 18, "F2", "white")
    c.text(44, 750, "Process", 13, "F2", "blue")
    process = [
        ("Discover", "Understand goals, audience, required pages, features, and business priorities."),
        ("Design", "Map the information hierarchy, visual language, CTA flow, responsive layout, and content sections."),
        ("Develop", "Build semantic HTML, modern CSS, JavaScript interactions, form validation, and backend-ready structure."),
        ("Launch", "Perform QA, optimize visuals, prepare handover notes, and support future improvements."),
    ]
    x = 44
    for i, (title, body) in enumerate(process, start=1):
        c.rect(x, 602, 116, 112, "mist", stroke="teal", width=0.55)
        c.text(x + 14, 684, f"0{i}", 16, "F2", "teal")
        c.text(x + 14, 660, title, 10.5, "F2", "ink")
        c.paragraph(x + 14, 642, body, 21, 8, 10.5)
        x += 128

    c.text(44, 540, "Why businesses choose this workflow", 13, "F2", "blue")
    y = 510
    for item in ["Custom development aligned with the client's offer.", "Mobile responsive design for every common device size.", "Clean architecture that is easier to maintain and extend.", "Fast delivery with clear scope, practical milestones, and professional communication.", "Lead generation features such as enquiry forms, newsletter capture, consultation popups, and direct contact buttons."]:
        c.text(58, y, "•", 10, "F2", "teal")
        y = c.paragraph(76, y, item, 78, 9, 12) - 6

    c.text(44, 336, "Project links and next steps", 13, "F2", "blue")
    c.rect(44, 236, 507, 78, "mist", stroke="teal", width=0.55)
    c.text(62, 286, "GitHub", 11, "F2", "ink")
    c.text(150, 286, "github.com/Tanisha804", 10, "F1", "soft")
    c.text(62, 264, "LinkedIn", 11, "F2", "ink")
    c.text(150, 264, "linkedin.com/in/tanisha-nalawade", 10, "F1", "soft")
    c.text(62, 242, "Services", 11, "F2", "ink")
    c.text(150, 242, "Business websites, REST APIs, full stack apps, landing pages, and maintenance", 10, "F1", "soft")

    c.rect(44, 92, 507, 88, "blue")
    c.text(62, 144, "Let's build something amazing together.", 17, "F2", "white")
    c.text(62, 120, "Email: nalawadetanisha5@gmail.com    Phone: 7387479140", 10, "F2", "pearl")
    pages.append(c.commands())
    return pages


if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    build_pdf([resume_page()], base / "Tanisha_Resume.pdf")
    build_pdf(portfolio_pages(), base / "Tanisha_Portfolio.pdf")
