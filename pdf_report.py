"""PDF report generation for the Health-Promoting Spaces assessment.

Layout: title + session header, radar chart of category scores, summary
table of category scores, then a per-category breakdown with each
attribute's indicators. The radar chart is rendered to a temp PNG via
plotly + kaleido, embedded, and the temp file is deleted.
"""

import os
import tempfile
from datetime import datetime
from io import BytesIO

import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _fmt(score):
    return "excluded" if score is None else f"{score:.1f}"


def _wrap_label(text, max_chars=18):
    """Word-wrap a label by inserting <br> at sensible breakpoints."""
    words = str(text).split()
    lines, line = [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > max_chars:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return "<br>".join(lines)


def _spider_png(theta, r, title, color):
    """Render a closed radar/spider chart to a temp PNG and return its path."""
    wrapped = [_wrap_label(t) for t in theta]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=r + [r[0]],
            theta=wrapped + [wrapped[0]],
            fill="toself",
            line=dict(color=color),
        )
    )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=False,
        title=title,
        height=560,
        width=780,
        margin=dict(t=80, b=80, l=160, r=160),
    )
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.write_image(path, format="png", engine="kaleido", scale=2)
    return path


def _table(rows, header_color):
    table = Table(rows, colWidths=[11 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F4F4F4")],
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def generate_pdf(scores: dict, session_id: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Assessment Report {session_id}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"], fontSize=20, spaceAfter=12
    )
    h2 = ParagraphStyle(
        "h2", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8
    )
    h3 = ParagraphStyle(
        "h3", parent=styles["Heading3"], spaceBefore=10, spaceAfter=6
    )
    body = styles["BodyText"]

    project_name = (scores.get("project_name") or "").strip()
    temp_paths = []

    story = []
    story.append(Paragraph("Health-Promoting Spaces Assessment Report", title_style))
    if project_name:
        story.append(
            Paragraph(
                f"<b>Project:</b> {project_name}",
                ParagraphStyle(
                    "project",
                    parent=body,
                    fontSize=14,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#2E7D32"),
                    spaceBefore=2,
                    spaceAfter=10,
                ),
            )
        )
    story.append(Paragraph(f"<b>Session ID:</b> {session_id}", body))
    story.append(
        Paragraph(
            f"<b>Date of submission:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            body,
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    # Overall score
    overall = scores.get("overall_score")
    if overall is not None:
        story.append(
            Paragraph(
                f"<b>Overall Score: {overall:.1f} / 100</b>",
                ParagraphStyle(
                    "overall",
                    parent=body,
                    fontSize=16,
                    alignment=TA_CENTER,
                    textColor=colors.HexColor("#2E7D32"),
                    spaceBefore=8,
                    spaceAfter=6,
                ),
            )
        )
        rating = scores.get("rating", "")
        meaning = scores.get("meaning", "")
        action = scores.get("action", "")
        if rating:
            story.append(
                Paragraph(
                    f"<b>Rating:</b> {rating} &nbsp;&nbsp;|&nbsp;&nbsp; "
                    f"<b>Meaning:</b> {meaning} &nbsp;&nbsp;|&nbsp;&nbsp; "
                    f"<b>Action:</b> {action}",
                    ParagraphStyle(
                        "interpretation",
                        parent=body,
                        fontSize=10,
                        alignment=TA_CENTER,
                        spaceBefore=2,
                        spaceAfter=12,
                    ),
                )
            )
    else:
        story.append(
            Paragraph(
                "<b>Overall Score: excluded</b>",
                ParagraphStyle(
                    "overall",
                    parent=body,
                    fontSize=16,
                    alignment=TA_CENTER,
                    spaceBefore=8,
                    spaceAfter=12,
                ),
            )
        )
    story.append(Spacer(1, 0.4 * cm))

    cats = scores.get("categories", {})
    cat_names = list(cats.keys())

    # Category radar chart
    if cat_names:
        plot_scores = [
            0.0 if cats[n].get("score") is None else float(cats[n]["score"])
            for n in cat_names
        ]
        try:
            path = _spider_png(
                cat_names, plot_scores, "Category scores (0–100)", "#2E7D32"
            )
            temp_paths.append(path)
            story.append(Image(path, width=15 * cm, height=10.8 * cm))
            story.append(Spacer(1, 0.3 * cm))
        except Exception as exc:
            story.append(
                Paragraph(
                    f"<i>(Category radar chart unavailable: {exc})</i>", body
                )
            )

    # Category summary table
    story.append(Paragraph("Category scores", h2))
    cat_rows = [["Category", "Score (0–100)"]]
    for name in cat_names:
        cat_rows.append([name, _fmt(cats[name].get("score"))])
    story.append(_table(cat_rows, "#2E7D32"))
    story.append(Spacer(1, 0.6 * cm))

    # Per-category breakdown
    for cat_name in cat_names:
        cat_data = cats[cat_name]
        story.append(
            Paragraph(f"{cat_name} — {_fmt(cat_data.get('score'))}", h2)
        )

        # Attribute radar for this category
        attr_items = list(cat_data.get("attributes", {}).items())
        if len(attr_items) >= 3:
            attr_names = [n for n, _ in attr_items]
            attr_plot = [
                0.0 if a.get("score") is None else float(a["score"])
                for _, a in attr_items
            ]
            try:
                path = _spider_png(
                    attr_names,
                    attr_plot,
                    f"Attribute scores — {cat_name}",
                    "#1565C0",
                )
                temp_paths.append(path)
                story.append(Image(path, width=14 * cm, height=10 * cm))
                story.append(Spacer(1, 0.3 * cm))
            except Exception as exc:
                story.append(
                    Paragraph(
                        f"<i>(Attribute radar chart unavailable: {exc})</i>",
                        body,
                    )
                )

        for attr_name, attr_data in attr_items:
            story.append(
                Paragraph(f"{attr_name} — {_fmt(attr_data.get('score'))}", h3)
            )
            inds = attr_data.get("indicators", {})
            if inds:
                ind_rows = [["Indicator", "Score (0–100)"]]
                for ind_name, ind_score in inds.items():
                    ind_rows.append([ind_name, _fmt(ind_score)])
                story.append(_table(ind_rows, "#1565C0"))
                story.append(Spacer(1, 0.3 * cm))

    doc.build(story)

    for path in temp_paths:
        try:
            os.remove(path)
        except OSError:
            pass

    buffer.seek(0)
    return buffer.read()
