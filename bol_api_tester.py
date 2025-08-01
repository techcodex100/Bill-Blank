import os
import time
import datetime
import requests
import psutil
from faker import Faker
from pydantic import BaseModel

fake = Faker()

# === Config ===
pdf_output_dir = "rendered_bol_pdfs"
os.makedirs(pdf_output_dir, exist_ok=True)

# API URL for your deployed FastAPI app
RENDER_URL = "https://bill-blank.onrender.com/generate-bill-of-lading/"  # Change to your URL
MAX_RETRIES = 5
DELAY_BETWEEN_REQUESTS = 2  # seconds
TOTAL_TESTS = 20  # Number of PDFs to generate

# === Data model ===
class BillOfLadingData(BaseModel):
    shipper: str
    consignee: str
    notify_party: str
    draft_bill_of_lading: str
    place_of_receipt: str
    place_of_delivery: str
    vessel_and_voyage: str
    port_of_loading: str
    port_of_discharge: str
    marks_numbers: str
    packages_description: str
    gross_weight: str
    measurement: str
    cseal_no: str
    sline_seal_no: str
    invoice_no: str
    dtd: str
    dt: str
    shipping_bill_no: str
    net_weight: str
    no_of_originals: str

# === Faker Data Generator ===
def generate_faker_data():
    return BillOfLadingData(
        shipper=fake.company() + "\n" + fake.address(),
        consignee=fake.company() + "\n" + fake.address(),
        notify_party=fake.company(),
        draft_bill_of_lading="BOL-" + str(fake.random_number(digits=6)),
        place_of_receipt=fake.city(),
        place_of_delivery=fake.city(),
        vessel_and_voyage=f"Vessel-{fake.word()} Voyage-{fake.random_int(1000, 9999)}",
        port_of_loading=fake.city(),
        port_of_discharge=fake.city(),
        marks_numbers=f"Mark-{fake.random_number(digits=4)}",
        packages_description=fake.text(max_nb_chars=50),
        gross_weight=f"{fake.random_int(1000, 5000)} KG",
        measurement=f"{fake.random_int(10, 100)} CBM",
        cseal_no="CSEAL-" + str(fake.random_number(digits=5)),
        sline_seal_no="SSEAL-" + str(fake.random_number(digits=5)),
        invoice_no="INV-" + str(fake.random_number(digits=5)),
        dtd=str(fake.date()),
        dt=str(fake.date()),
        shipping_bill_no="SB-" + str(fake.random_number(digits=6)),
        net_weight=f"{fake.random_int(800, 4500)} KG",
        no_of_originals=str(fake.random_int(1, 5))
    )

# === Static Data Generator (Non-Faker) ===
def generate_static_data():
    return BillOfLadingData(
        shipper="ABC Exporters\n123 Street, City",
        consignee="XYZ Imports\n456 Avenue, City",
        notify_party="Notify Party Ltd.",
        draft_bill_of_lading="BOL-123456",
        place_of_receipt="Mumbai",
        place_of_delivery="New York",
        vessel_and_voyage="Evergreen 1020",
        port_of_loading="Nhava Sheva",
        port_of_discharge="Newark",
        marks_numbers="Mark-001",
        packages_description="50 cartons of textiles",
        gross_weight="2500 KG",
        measurement="75 CBM",
        cseal_no="CSEAL-78901",
        sline_seal_no="SSEAL-45678",
        invoice_no="INV-98765",
        dtd="2025-08-01",
        dt="2025-08-02",
        shipping_bill_no="SB-654321",
        net_weight="2400 KG",
        no_of_originals="3"
    )

# === Run Test ===
for i in range(1, TOTAL_TESTS + 1):
    # Alternate between faker & static for testing variety
    test_data = generate_faker_data() if i % 2 == 0 else generate_static_data()
    start_time = time.time()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(RENDER_URL, json=test_data.model_dump())
            if response.status_code == 200:
                break
            else:
                print(f"⚠️ Attempt {attempt}: Failed PDF {i} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ Exception: {e}")
        time.sleep(3)

    if response.status_code != 200:
        print(f"❌ Skipped PDF {i} after {MAX_RETRIES} retries.")
        continue

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    pdf_filename = os.path.join(pdf_output_dir, f"bill_of_lading_{i}_{timestamp}.pdf")
    with open(pdf_filename, "wb") as f:
        f.write(response.content)

    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    elapsed = round(time.time() - start_time, 2)

    print(f"✅ [{i}/{TOTAL_TESTS}] PDF Generated: {pdf_filename}")
    print(f"   CPU Usage: {cpu}% | Memory: {mem}% | Time: {elapsed}s")
    print("-" * 50)

    time.sleep(DELAY_BETWEEN_REQUESTS)

print("🎉 Testing Completed!")
