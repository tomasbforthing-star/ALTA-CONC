import os

file_path = "app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add dynamic role logic
dynamic_logic = """
    // ----------------------------------------------------
    // Dynamic Role Logic
    // ----------------------------------------------------
    const selectTipoRazonSocial = document.getElementById('tipo-razon-social');
    const inputCargoDirector = document.getElementById('cargo-director');
    if (selectTipoRazonSocial && inputCargoDirector) {
        selectTipoRazonSocial.addEventListener('change', (e) => {
            const val = e.target.value;
            if (val === 'SRL') {
                inputCargoDirector.value = 'SOCIO GERENTE';
            } else if (val === 'SA' || val === 'SAS') {
                inputCargoDirector.value = 'PRESIDENTE';
            } else {
                inputCargoDirector.value = '';
            }
        });
    }
"""

# Find a good place to insert, e.g., before "// 2. Section 2: Conditional "Otros" Checkbox"
insert_idx = content.find('// 2. Section 2: Conditional "Otros" Checkbox')
if insert_idx != -1:
    content = content[:insert_idx] + dynamic_logic + "\n    " + content[insert_idx:]

# 2. Add redes_sociales to payload
old_payload = """                sitio_web: document.getElementById('sitio-web').value,
                fecha_apertura: document.getElementById('fecha-apertura').value,"""

new_payload = """                sitio_web: document.getElementById('sitio-web').value,
                redes_sociales: document.getElementById('redes-sociales') ? document.getElementById('redes-sociales').value : '',
                fecha_apertura: document.getElementById('fecha-apertura').value,"""

content = content.replace(old_payload, new_payload)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.js")
