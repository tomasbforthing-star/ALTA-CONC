import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

# Try to load dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def prepare_and_send_email(data, pdf_path, temp_files_folder="/tmp/sent_emails"):
    """
    Composes and dispatches the dealer onboarding email containing the PDF
    report and all original photo attachments.
    """
    # 1. Load SMTP Settings from environment variables
    smtp_host = os.environ.get("SMTP_HOST", "localhost")
    try:
        smtp_port = int(os.environ.get("SMTP_PORT", "1025")) # Default to a local dev mailserver port (e.g., Mailpit/Mailhog or python SMTP debugging server)
    except ValueError:
        smtp_port = 1025
        
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_password = os.environ.get("SMTP_PASSWORD", "")
    smtp_from = os.environ.get("SMTP_FROM", "portal@forthing.com.ar")
    
    use_tls = os.environ.get("SMTP_USE_TLS", "False").lower() in ("true", "1", "yes")
    use_ssl = os.environ.get("SMTP_USE_SSL", "False").lower() in ("true", "1", "yes")

    # Destination addresses
    recipients_env = os.environ.get("SMTP_RECIPIENTS", "")
    if recipients_env:
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]
    else:
        recipients = [
            "tomas-barcia@forthing.com.ar"
        ]
    
    # 2. Compose Email Content
    concesionario_name = data.get("nombre_concesionario", "Sin Nombre")
    solicitud_nro = data.get("solicitud_nro", "FTH-2026-XXXX")
    
    msg = MIMEMultipart()
    msg["From"] = smtp_from
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = f"Nueva Solicitud de Alta de Concesionario - {concesionario_name}"
    
    body = f"""Estimados,

Se ha recibido una nueva solicitud de Alta de Concesionario para evaluación por parte de Forthing Argentina.

Número de Solicitud:
[{solicitud_nro}]

Concesionario:
[{concesionario_name}]

Razón Social:
[{data.get("razon_social", "")}]

CUIT:
[{data.get("cuit", "")}]

Ciudad:
[{data.get("ciudad", "")}]

Provincia:
[{data.get("provincia", "")}]

Se adjunta el formulario completo junto con el registro fotográfico correspondiente.

Este correo fue generado automáticamente por el Portal de Alta de Concesionarios Forthing Argentina.
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    # 3. Attach the generated PDF
    pdf_filename = f"Alta Concesionario - {concesionario_name}.pdf"
    try:
        with open(pdf_path, "rb") as f:
            pdf_attachment = MIMEApplication(f.read(), Name=pdf_filename)
            pdf_attachment["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
            msg.attach(pdf_attachment)
    except Exception as e:
        raise IOError(f"Error attaching generated PDF: {e}")
        
    # 4. Attach original images
    photo_labels = {
        'frente': 'Frente_Concesionario',
        'salon': 'Salon_de_Ventas',
        'taller': 'Taller_Mecanico',
        'deposito': 'Deposito_de_Repuestos',
        'postventa': 'Area_de_Postventa',
        'administrativa': 'Area_Administrativa'
    }
    
    import base64
    photos_dict = data.get("imagenes", {})
    for key, base64_list in photos_dict.items():
        if not isinstance(base64_list, list):
            if base64_list:
                base64_list = [base64_list]
            else:
                base64_list = []
                
        for idx, base64_str in enumerate(base64_list):
            if base64_str:
                try:
                    # Decode base64
                    if "," in base64_str:
                        header, base64_data = base64_str.split(",")
                    else:
                        base64_data = base64_str
                        header = "image/jpeg"
                        
                    # Determine extension
                    ext = "jpg"
                    if "png" in header:
                        ext = "png"
                    elif "webp" in header:
                        ext = "webp"
                        
                    img_bytes = base64.b64decode(base64_data)
                    label = photo_labels.get(key, key)
                    filename = f"{label}_{idx+1}.{ext}"
                    
                    # Attachment structure
                    img_attachment = MIMEApplication(img_bytes, Name=filename)
                    img_attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
                    # Attempt to guess and set Content-Type
                    mime_type, _ = mimetypes.guess_type(filename)
                    if mime_type:
                        img_attachment["Content-Type"] = mime_type
                    else:
                        img_attachment["Content-Type"] = f"image/{ext}"
                        
                    msg.attach(img_attachment)
                except Exception as e:
                    print(f"Failed to attach image {key}_{idx+1}: {e}")

    # 5. Local Backup/Audit (Save as .eml file)
    try:
        if not os.path.exists(temp_files_folder):
            os.makedirs(temp_files_folder)
        eml_filename = f"{solicitud_nro}_{concesionario_name.replace(' ', '_')}.eml"
        eml_path = os.path.join(temp_files_folder, eml_filename)
        with open(eml_path, "wb") as f:
            f.write(msg.as_bytes())
        print(f"Local audit email copy saved to {eml_path}")
    except Exception as e:
        print(f"Warning: Failed to save audit copy of email: {e}")

    # 6. SMTP Delivery
    try:
        # Check if dummy settings are present, if so, write a note and skip actual connection
        # to avoid blocking if the server is not defined, but raise a descriptive connection error
        # so it logs correctly.
        if smtp_host == "localhost" and smtp_port == 1025 and not smtp_user:
            # Let's check if there is an active SMTP server running.
            # We will attempt connection with a short timeout.
            # If it fails, we will save the file and raise an error, advising how to configure it.
            print("Connecting to local SMTP server...")
            
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            
        if use_tls:
            server.starttls()
            
        if smtp_user and smtp_password:
            server.login(smtp_user, smtp_password)
            
        server.sendmail(smtp_from, recipients, msg.as_string())
        server.quit()
        print("Email sent successfully via SMTP.")
        
    except Exception as e:
        print(f"SMTP delivery failed: {e}")
        # If we failed but saved the local EML file, we still raise the error to inform the frontend
        # that email delivery failed, so the user sees a specific error.
        raise ConnectionError(
            f"El correo no pudo ser enviado a través del servidor SMTP ({smtp_host}:{smtp_port}). "
            f"Error original: {e}. Se guardó una copia de auditoría local en la carpeta '{temp_files_folder}'."
        )
