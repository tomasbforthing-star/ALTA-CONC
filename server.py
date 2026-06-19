import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

# Import local modules
from pdf_generator import generate_final_pdf
from email_sender import prepare_and_send_email

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("submissions.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# State file to track sequential submission numbers
STATE_FILE = "submissions_state.json"
BACKUP_FOLDER = "temp_submissions"
TEMPLATE_PDF = "ALTA CONCESIONARIO -.pdf"

def get_next_solicitud_nro():
    """
    Reads the state file, increments the counter, and returns a formatted
    solicitud number like FTH-YYYY-NNNN.
    """
    current_year = datetime.now().year
    counter = 1
    
    # Read existing state if available
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                
            # If the year matches, increment the counter. Else, reset counter to 1 for the new year.
            if state.get("year") == current_year:
                counter = state.get("counter", 0) + 1
            else:
                counter = 1
        except Exception as e:
            logging.error(f"Error reading state file {STATE_FILE}: {e}")
            
    # Save the updated state
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"year": current_year, "counter": counter}, f)
    except Exception as e:
        logging.error(f"Error writing state file {STATE_FILE}: {e}")
        
    return f"FTH-{current_year}-{counter:04d}"


def save_backup_payload(solicitud_nro, data):
    """Saves the raw JSON payload to a temp folder to prevent data loss."""
    try:
        if not os.path.exists(BACKUP_FOLDER):
            os.makedirs(BACKUP_FOLDER)
            
        filepath = os.path.join(BACKUP_FOLDER, f"{solicitud_nro}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        logging.info(f"Backup payload saved to {filepath}")
    except Exception as e:
        logging.error(f"Failed to save backup payload for {solicitud_nro}: {e}")


# API Endpoint to handle form submissions
@app.route('/api/submit', methods=['POST'])
def submit_onboarding():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibieron datos en formato JSON."}), 400
        
    # 1. Validate General Required Fields
    required_fields = [
        'nombre_concesionario', 'razon_social', 'cuit',
        'direccion_legal', 'ciudad', 'provincia',
        'telefono_principal', 'email_principal'
    ]
    
    missing_fields = []
    for field in required_fields:
        if not data.get(field) or str(data.get(field)).strip() == "":
            missing_fields.append(field)
            
    if missing_fields:
        logging.warning(f"Submission rejected. Missing fields: {missing_fields}")
        return jsonify({
            "error": "Datos incompletos.",
            "details": f"Faltan completar los siguientes campos obligatorios: {', '.join(missing_fields)}"
        }), 400
        
    # 2. Validate Photo Uploads (Skipped - Image uploads are now optional)
    pass

    # 3. Generate Request Number
    solicitud_nro = get_next_solicitud_nro()
    fecha_solicitud = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Inject metadata into data dictionary
    data['solicitud_nro'] = solicitud_nro
    data['fecha_solicitud'] = fecha_solicitud
    
    logging.info(f"Processing submission {solicitud_nro} for dealer {data.get('nombre_concesionario')}")
    
    # 4. Save JSON backup immediately (prevents data loss)
    save_backup_payload(solicitud_nro, data)
    
    # 5. Generate corporate PDF
    nombre_concesionario = data.get("nombre_concesionario").strip()
    pdf_filename = f"Alta Concesionario - {nombre_concesionario}.pdf"
    
    # Sanitize filename (remove characters that are invalid in filenames)
    for char in ['/', '\\', '?', '%', '*', ':', '|', '"', '<', '>']:
        pdf_filename = pdf_filename.replace(char, '_')
        
    output_pdf_path = os.path.join(os.getcwd(), pdf_filename)
    
    if not os.path.exists(TEMPLATE_PDF):
        logging.error(f"Template PDF not found: {TEMPLATE_PDF}")
        return jsonify({
            "error": "Error interno del servidor.",
            "details": f"No se encontró el archivo de plantilla base '{TEMPLATE_PDF}' en el servidor."
        }), 500
        
    pdf_success = generate_final_pdf(data, output_pdf_path, TEMPLATE_PDF)
    if not pdf_success:
        logging.error(f"Failed to generate PDF for {solicitud_nro}")
        return jsonify({
            "error": "Error en la generación del PDF.",
            "details": "Ocurrió un error al intentar compilar la información y el anexo fotográfico en el archivo PDF corporativo."
        }), 500
        
    # 6. Dispatch Email Notification
    email_error_msg = None
    try:
        prepare_and_send_email(data, output_pdf_path)
        logging.info(f"Submission {solicitud_nro} completed successfully.")
    except Exception as email_err:
        email_error_msg = str(email_err)
        logging.warning(f"Submission {solicitud_nro} generated PDF successfully, but SMTP email dispatch failed: {email_err}. Backup EML saved locally.")
        
    return jsonify({
        "status": "success",
        "solicitud_nro": solicitud_nro,
        "pdf_filename": pdf_filename,
        "email_warning": email_error_msg
    })


# Serve Static files from the current folder
@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(os.getcwd(), filename)


if __name__ == '__main__':
    # Get port from environment or run on 8000
    try:
        port = int(os.environ.get("PORT", "8000"))
    except ValueError:
        port = 8000
        
    logging.info(f"Starting Forthing Dealer Portal server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
