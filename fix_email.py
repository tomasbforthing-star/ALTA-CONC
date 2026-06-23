import os

file_path = "email_sender.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

bad_block = """    if recipients_env:
        recipients = [r.strip() for r in recipients_env.split(",") if r.strip()]
        recipients = [
            "Administracion@forthing.com.ar",
            "Venta@forthing.com.ar",
            "Postventa@forthing.com.ar",
            "Comunicaciones@forthing.com.ar",
            "Marketing@forthing.com.ar",
            "Matias.blanco@forthing.com.ar"
        ]"""

good_block = """    if recipients_env:
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

content = content.replace(bad_block, good_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed else clause")
