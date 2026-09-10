"""
Builds the executive presentation deck summarizing the Marketing
Analytics Platform capstone project findings.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

NAVY = RGBColor(0x1F, 0x38, 0x64)
ACCENT = RGBColor(0x2E, 0x50, 0x90)
GRAY = RGBColor(0x59, 0x59, 0x59)

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(blank_layout)


def add_title(slide, text, size=36, color=NAVY, top=0.4):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(top), Inches(12.1), Inches(1.0))
    tf = box.text_frame
    tf.text = text
    run = tf.paragraphs[0].runs[0]
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = color
    return box


def add_body_text(slide, text, top=1.5, size=20, color=GRAY, bold=False, height=1.0):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(top), Inches(12.1), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.text = text
    run = tf.paragraphs[0].runs[0]
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def add_bullets(slide, bullets, top=1.8, size=18):
    box = slide.shapes.add_textbox(Inches(0.8), Inches(top), Inches(11.5), Inches(4.5))
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"-  {bullet}"
        p.font.size = Pt(size)
        p.font.color.rgb = GRAY
        p.space_after = Pt(14)


# Slide 1: Title
s = add_slide()
add_title(s, "Marketing Analytics Platform", size=44, top=2.6)
add_body_text(s, "Key Findings & Recommendations", top=3.6, size=24, color=ACCENT)
add_body_text(s, "Joel Bumba  |  Data Analyst", top=4.3, size=16, color=GRAY)

# Slide 2: The Business Question
s = add_slide()
add_title(s, "The Business Question")
add_body_text(
    s,
    "Which customers are we at risk of losing, and where should\n"
    "we focus retention effort to protect revenue?",
    top=2.2, size=26, color=ACCENT, height=2.0
)

# Slide 3: Key Finding 1 - Churn
s = add_slide()
add_title(s, "Finding 1: Purchase Frequency Drives Retention")
add_bullets(s, [
    "50.9% of customers had no purchase in the last 90 days",
    "A churn prediction model correctly identifies 81% of at-risk customers (recall = 0.81)",
    "Purchase FREQUENCY is by far the strongest predictor of churn -- far more than total spend",
    "Customers who buy small amounts often are a safer bet than those who spend big rarely",
])

# Slide 4: Key Finding 2 - Revenue Picture
s = add_slide()
add_title(s, "Finding 2: Revenue Concentration")
add_bullets(s, [
    "Total revenue: $20,972,968 across 40,076 orders from 5,939 customers",
    "The United Kingdom accounts for the large majority of revenue (92% of transactions)",
    "\"Other\" and \"Kitchen & Dining\" are the top two product categories by revenue",
    "Clear seasonal peaks each November -- holiday gift-buying drives the annual cycle",
])

# Slide 5: Recommendation
s = add_slide()
add_title(s, "Recommendation")
add_bullets(s, [
    "Target high-frequency customers who have gone quiet BEFORE they cross the 90-day threshold",
    "Prioritize re-engagement campaigns by predicted churn risk, not just recency alone",
    "Focus retention spend on frequent, moderate-value customers -- the model shows this segment",
    "  is more valuable to protect than rare, high-value ones",
])

# Slide 6: What This Enables
s = add_slide()
add_title(s, "What This Enables Going Forward")
add_bullets(s, [
    "A live dashboard (Tableau) refreshed on demand for ad-hoc exploration",
    "An automated weekly PDF executive summary -- zero manual reporting effort",
    "A churn-scored customer table, ready to feed directly into a retention campaign",
    "A documented, reproducible data pipeline -- not a one-off analysis",
])

# Slide 7: Appendix
s = add_slide()
add_title(s, "Appendix: Technical Summary")
add_bullets(s, [
    "Data warehouse: PostgreSQL, dimensional star schema (1 fact + 4 dimension tables)",
    "ETL: Python (pandas, SQLAlchemy), idempotent and re-runnable",
    "Churn model: Logistic Regression, precision 0.67 / recall 0.81 on the churned class",
    "Source data: Online Retail II (UCI/Kaggle), ~1.06M real transactions, 2009-2011",
], size=16)

prs.save("Marketing_Analytics_Executive_Summary.pptx")
print("Presentation saved: Marketing_Analytics_Executive_Summary.pptx")