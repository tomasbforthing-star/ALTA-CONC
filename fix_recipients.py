import os

file_path = "email_sender.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

old_block = """    # Destination addresses
    recipients_env = os.environ.get("SMTP_RECIPIENTS", "")
    if recipients_env:
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]
    else:
        recipients = [
            "Administracion@forthing.com.ar",
            "Venta@forthing.com.ar",
            "Postventa@forthing.com.ar",
            "Comunicaciones@forthing.com.ar",
            "Marketing@forthing.com.ar",
            "Matias.blanco@forthing.com.ar"
        ]"""

new_block = """    # Destination addresses (Hardcoded as requested)
    recipients = [
        "Administracion@forthing.com.ar",
        "Venta@forthing.com.ar",
        "Postventa@forthing.com.ar",
        "Comunicaciones@forthing.com.ar",
        "Marketing@forthing.com.ar",
        "Matias.blanco@forthing.com.ar"
    ]"""

content = content.replace(old_block, new_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed recipients in email_sender.py")
