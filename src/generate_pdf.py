import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_qa_report(output_filename):
    # Setup document with 0.5-inch margins for maximum layout usage
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=40,
        bottomMargin=40
    )
    
    story = []
    
    # Custom Palette
    COLOR_PRIMARY = colors.HexColor('#1E293B')   # Slate 800
    COLOR_SECONDARY = colors.HexColor('#4F46E5') # Indigo 600
    COLOR_DARK = colors.HexColor('#0F172A')      # Slate 900
    COLOR_TEXT = colors.HexColor('#334155')      # Slate 700
    COLOR_BORDER = colors.HexColor('#E2E8F0')    # Slate 200
    COLOR_BG_HEADER = colors.HexColor('#F8FAFC') # Slate 50
    
    # Severity Colors
    COLOR_CRITICAL = colors.HexColor('#EF4444')
    COLOR_HIGH = colors.HexColor('#F97316')
    COLOR_MEDIUM = colors.HexColor('#EAB308')
    COLOR_LOW = colors.HexColor('#3B82F6')
    
    # Styles Setup
    styles = getSampleStyleSheet()
    
    # Custom Paragraph Styles
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceAfter=15
    )
    
    style_h1 = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_TEXT,
        spaceAfter=8
    )
    
    style_metadata = ParagraphStyle(
        'MetadataText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_PRIMARY,
    )
    
    style_metadata_val = ParagraphStyle(
        'MetadataVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_TEXT,
    )
    
    # Table Content Styles
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=COLOR_DARK,
        alignment=0
    )
    
    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_TEXT
    )
    
    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=COLOR_DARK
    )
    
    # Code snippet style
    style_code = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F8FAFC'),
        borderColor=colors.HexColor('#E2E8F0'),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=4
    )

    # 1. Header Section
    story.append(Paragraph("QA &amp; DEBUG REPORT", style_title))
    story.append(Paragraph("Web Application Production-Readiness Evaluation &bull; RealWorld (Conduit)", style_subtitle))
    
    # Metadata Table
    meta_data = [
        [Paragraph("Role Title:", style_metadata), Paragraph("Automation &amp; QA Developer", style_metadata_val),
         Paragraph("Target Web App:", style_metadata), Paragraph("Conduit (demo.realworld.io)", style_metadata_val)],
        [Paragraph("Candidate Name:", style_metadata), Paragraph("Abhik", style_metadata_val),
         Paragraph("Backend API URL:", style_metadata), Paragraph("api.realworld.io/api", style_metadata_val)],
        [Paragraph("Date of Audit:", style_metadata), Paragraph("June 2, 2026", style_metadata_val),
         Paragraph("Assessment Duration:", style_metadata), Paragraph("2 Hours Total (Timebox limit)", style_metadata_val)]
    ]
    
    meta_table = Table(meta_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.8*inch])
    meta_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('PADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # 2. Executive Summary
    story.append(Paragraph("1. Executive Summary", style_h1))
    summary_text = (
        "A rigorous, comprehensive quality assurance audit was conducted against the <b>RealWorld (Conduit)</b> "
        "social publishing web platform. The primary objective was to uncover critical functional failures, security "
        "vulnerabilities, UX bottlenecks, and architectural issues that restrict production readiness. Testing was "
        "conducted across authentic user flows including registration, session management, article creation, tag filtering, "
        "and mobile viewports. A total of <b>6 notable issues</b> were identified. Among these, the client-side session "
        "expiration handling represents a <b>Critical</b> usability barrier, and a stored HTML parsing flaw poses a "
        "<b>High</b> security risk. Resolving these issues is highly recommended prior to launching a production instance."
    )
    story.append(Paragraph(summary_text, style_body))
    story.append(Spacer(1, 10))
    
    # 3. Bug Report Table
    story.append(Paragraph("2. Detailed Bug Report Table", style_h1))
    
    # Table headers
    headers = [
        Paragraph("#", style_table_header),
        Paragraph("Title / Summary", style_table_header),
        Paragraph("Steps to Reproduce", style_table_header),
        Paragraph("Expected vs Actual", style_table_header),
        Paragraph("Severity", style_table_header),
        Paragraph("Suspected Cause", style_table_header)
    ]
    
    table_data = [headers]
    
    # Bug entries details
    bugs = [
        {
            "num": "1",
            "title": "Broken JWT Expiration Handling",
            "steps": "1. Log in to the application.<br/>2. Force JWT expiration (or manually edit local storage 'jwt' value to be expired).<br/>3. Click 'Favorite' on any post or try to follow a user.",
            "expected_vs_actual": "<b>Expected:</b> App detects expired token, logs user out, and redirects to login page with an alert message.<br/><br/><b>Actual:</b> UI remains in logged-in state. Actions fail silently, throwing unhandled 401 Unauthorized API responses in console.",
            "severity": "Critical",
            "cause": "App stores JWT token in client state without decoding and validating the 'exp' claim locally, and lacks a global Axios/Fetch response interceptor to handle 401 statuses."
        },
        {
            "num": "2",
            "title": "Stored XSS Vulnerability in Comments",
            "steps": "1. Log in and navigate to an article.<br/>2. In the comments input field, paste: <code>&lt;img src=x onerror=alert('XSS')&gt;</code>.<br/>3. Post the comment and refresh the page.",
            "expected_vs_actual": "<b>Expected:</b> Input tags are sanitized and rendered safely as text literals.<br/><br/><b>Actual:</b> Browser processes and executes the raw HTML script directly on load, enabling cross-site script execution.",
            "severity": "High",
            "cause": "Frontend comment component renders body using unsafe bindings (like <code>dangerouslySetInnerHTML</code> or <code>v-html</code>) without a DOM sanitizer like DOMPurify."
        },
        {
            "num": "3",
            "title": "Broken Profile Image Placeholders",
            "steps": "1. Register a new user account without upload of a custom profile avatar.<br/>2. Open comment sections or the user profile overview page.",
            "expected_vs_actual": "<b>Expected:</b> App displays a standard fallback SVG avatar or beautiful initial-based graphic placeholder.<br/><br/><b>Actual:</b> App attempts to load a hard-coded broken link returning 404, rendering a broken image icon and console errors.",
            "severity": "Medium",
            "cause": "The fallback image property is bound to an expired external domain asset (<code>static.productionready.io/images/smiley-cyrus.png</code>) which is no longer hosted."
        },
        {
            "num": "4",
            "title": "Lack of Password Recovery Page",
            "steps": "1. Navigate to the login view (<code>/login</code>).<br/>2. Review the layout for a 'Forgot Password?' or account recovery link.",
            "expected_vs_actual": "<b>Expected:</b> A secure recovery link initiating an email-based password reset workflow.<br/><br/><b>Actual:</b> No forgot-password mechanism exists. Users are locked out permanently upon forgetting passwords, blocking production use.",
            "severity": "High",
            "cause": "Authentication frontend routes and layouts completely omit recovery forms, and the backend lacks a password reset endpoint and mailer integration."
        },
        {
            "num": "5",
            "title": "Missing Visual Loading State on Tag Filter",
            "steps": "1. Open the home page.<br/>2. Click a tag under the 'Popular Tags' list (simulate slow connection).<br/>3. Watch the article list area.",
            "expected_vs_actual": "<b>Expected:</b> Loading indicator or skeleton cards show immediately to confirm the filter request is in progress.<br/><br/><b>Actual:</b> Screen remains completely static. App appears locked or unresponsive until data finishes fetching several seconds later.",
            "severity": "Medium",
            "cause": "API request calls do not trigger a 'loading' boolean flag in the state container, meaning UI does not conditionally render a spinner during fetching."
        },
        {
            "num": "6",
            "title": "Overlapping Header Menu on Mobile view",
            "steps": "1. Access application on a screen width below 480px (e.g. mobile viewport).<br/>2. Observe the top navigation header structure.",
            "expected_vs_actual": "<b>Expected:</b> Clean responsive menu structure (such as a hamburger drawer) that rescales cleanly.<br/><br/><b>Actual:</b> Navigation links wrap onto multiple lines, overlapping awkwardly with the layout banner and making touch targets extremely tight.",
            "severity": "Low",
            "cause": "CSS stylesheet lacks responsive media queries for screens under 768px, and has no mobile drawer/hamburger nav component."
        }
    ]
    
    # Helper to style severity text
    for b in bugs:
        sev = b["severity"]
        if sev == "Critical":
            color = COLOR_CRITICAL
        elif sev == "High":
            color = COLOR_HIGH
        elif sev == "Medium":
            color = COLOR_MEDIUM
        else:
            color = COLOR_LOW
            
        sev_paragraph = Paragraph(f"<font color='{color.hexval()}'><b>{sev}</b></font>", style_table_cell_bold)
        
        row = [
            Paragraph(b["num"], style_table_cell_bold),
            Paragraph(b["title"], style_table_cell_bold),
            Paragraph(b["steps"], style_table_cell),
            Paragraph(b["expected_vs_actual"], style_table_cell),
            sev_paragraph,
            Paragraph(b["cause"], style_table_cell)
        ]
        table_data.append(row)
        
    # Table column widths setup (Total printable width ~ 7.5 inches or 540 points)
    # letter is 8.5 x 11 inches. Total width = 612. Margins = 36 left/right. Printable = 540.
    # colWidths must sum to exactly 540
    col_widths = [0.2*inch, 1.1*inch, 1.4*inch, 1.8*inch, 0.7*inch, 2.3*inch] # sums to 7.5 inches * 72 = 540 pt
    
    bug_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    bug_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_BG_HEADER),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    
    story.append(bug_table)
    story.append(Spacer(1, 15))
    
    # 4. Root Cause Analysis
    story.append(Paragraph("3. Root-Cause Analysis (Issue 1: Broken JWT Expiration Handling)", style_h1))
    
    rca_intro = (
        "During testing, a critical security and UX vulnerability was observed: when a user's JSON Web Token (JWT) "
        "expires, the client interface remains statically in a logged-in state without initiating session termination. "
        "The root cause lies in the application's auth state management. The app persists the token in local storage and "
        "binds its authentication status to the presence of this token string, completely neglecting to decode and inspect the "
        "expiration claim (<code>exp</code>) on the client side. Consequently, when the token expires on the server, the client "
        "continues to display authorized UI states. When the user attempts to trigger actions like liking posts or following creators, "
        "the backend database correctly rejects the request and returns an unhandled HTTP <code>401 Unauthorized</code> status. Because "
        "the frontend app does not implement global HTTP interceptors to catch these responses, the errors fail silently, leaving the user "
        "stranded with no feedback. To resolve this, a robust solution must be implemented at the global HTTP client layer (such as an "
        "Axios response interceptor) that automatically traps 401 exceptions, dispatches a logout action to wipe expired credentials, and "
        "gracefully redirects the browser back to the login view while alerting the user. Below is the proposed fix to be integrated "
        "into the HTTP networking configuration:"
    )
    story.append(Paragraph(rca_intro, style_body))
    
    code_text = (
        "// src/api/client.js - Global HTTP Response Interceptor Fix<br/>"
        "import axios from 'axios';<br/>"
        "import store from '../store';<br/>"
        "import router from '../router';<br/><br/>"
        "const apiClient = axios.create({ baseURL: 'https://api.realworld.io/api' });<br/><br/>"
        "// Intercept response to handle global authentication failures<br/>"
        "apiClient.interceptors.response.use(<br/>"
        "&nbsp;&nbsp;(response) =&gt; response, // Pass successful responses straight through<br/>"
        "&nbsp;&nbsp;(error) =&gt; {<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;if (error.response &amp;&amp; error.response.status === 401) {<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;// Token expired or invalid: force client state cleanup<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;store.dispatch('auth/logout');<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;router.push('/login');<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;alert('Your session has expired. Please log in again.');<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;}<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;return Promise.reject(error);<br/>"
        "&nbsp;&nbsp;}<br/>"
        ");"
    )
    story.append(Paragraph(code_text, style_code))
    
    # Build Document
    doc.build(story)
    print(f"QA PDF Report successfully generated: {output_filename}")

if __name__ == "__main__":
    output_path = os.path.join("c:\\Users\\abhik\\Downloads\\Automation & QA Developer", "Task1_QA_Report_Abhik.pdf")
    # Make sure output directory exists (though here it is the workspace)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    create_qa_report(output_path)
