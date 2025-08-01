from fastapi import FastAPI, Response, HTTPException
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from typing import Optional
from io import BytesIO
import os

app = FastAPI(
    title="Bill of Lading Draft Generator",
    description="Generates a Bill of Lading Draft PDF with fields placed on coordinates",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bill of Lading Draft Generator is live 🚀"}

class BillOfLadingData(BaseModel):
    shipper: Optional[str] = ""
    consignee: Optional[str] = ""
    notify_party: Optional[str] = ""
    draft_bill_of_lading: Optional[str] = ""
    place_of_receipt: Optional[str] = ""
    place_of_delivery: Optional[str] = ""
    vessel_and_voyage: Optional[str] = ""
    port_of_loading: Optional[str] = ""
    port_of_discharge: Optional[str] = ""
    marks_numbers: Optional[str] = ""
    packages_description: Optional[str] = ""
    gross_weight: Optional[str] = ""
    measurement: Optional[str] = ""
    cseal_no: Optional[str] = ""
    sline_seal_no: Optional[str] = ""
    invoice_no: Optional[str] = ""
    dtd: Optional[str] = ""
    dt: Optional[str] = ""
    shipping_bill_no: Optional[str] = ""
    net_weight: Optional[str] = ""
    no_of_originals: Optional[str] = ""

@app.post("/generate-bill-of-lading/")
def generate_bill_of_lading(data: BillOfLadingData):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # === Use relative path ===
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_dir, "static", "bg.jpg")  # keep file inside /static

        # Debugging: print to server log
        print(f"Looking for background at: {bg_path}")
        print(f"File exists? {os.path.exists(bg_path)}")

        # === Draw background ===
        if os.path.exists(bg_path):
            try:
                img = ImageReader(bg_path)
                c.drawImage(img, 0, 0, width=width, height=height, preserveAspectRatio=True, mask='auto')
            except Exception as img_err:
                print(f"Image load error: {img_err}")
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, 800, "⚠️ Failed to load background image.")
        else:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, 800, f"⚠️ Background missing at: {bg_path}")

        # === Helper for text ===
        def draw_text(value, x, y, font_size=10):
            c.setFont("Helvetica", font_size)
            c.drawString(x, y, value)

        # === Draw fields ===
        draw_text(data.shipper, 150, 750)
        draw_text(data.consignee, 100, 650)
        draw_text(data.notify_party, 100, 600)
        draw_text(data.draft_bill_of_lading, 350, 650)
        draw_text(data.place_of_receipt, 350, 585)
        draw_text(data.place_of_delivery, 310, 500)
        draw_text(data.vessel_and_voyage, 100, 520)
        draw_text(data.port_of_loading, 50, 480)
        draw_text(data.port_of_discharge, 150, 480)
        draw_text(data.marks_numbers, 50, 450)
        draw_text(data.packages_description, 300, 400)
        draw_text(data.gross_weight, 450, 435)
        draw_text(data.measurement, 530, 435)
        draw_text(data.cseal_no, 100, 320)
        draw_text(data.sline_seal_no, 50, 290)
        draw_text(data.invoice_no, 225, 360)
        draw_text(data.dtd, 290, 360)
        draw_text(data.dt, 350, 350)
        draw_text(data.shipping_bill_no, 150, 340)
        draw_text(data.net_weight, 450, 390)
        draw_text(data.no_of_originals, 150, 90)

        c.save()
        buffer.seek(0)

        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=bill_of_lading_draft.pdf"}
        )

    except Exception as e:
        print("⚠️ PDF generation failed:", str(e))
        raise HTTPException(status_code=500, detail="PDF generation failed")
