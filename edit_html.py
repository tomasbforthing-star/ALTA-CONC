import os
import re

file_path = "index.html"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add redes sociales
old_redes = """                            <div class="input-group full-width-tablet">
                                <label for="sitio-web">Sitio Web</label>
                                <input type="url" id="sitio-web" name="sitio_web" placeholder="Ej. https://www.concesionario.com.ar">
                            </div>
                            
                            <div class="input-group">
                                <label for="fecha-apertura" class="required-label">Fecha de Apertura Aproximada</label>"""
new_redes = """                            <div class="input-group full-width-tablet">
                                <label for="sitio-web">Sitio Web</label>
                                <input type="url" id="sitio-web" name="sitio_web" placeholder="Ej. https://www.concesionario.com.ar">
                            </div>

                            <div class="input-group full-width-tablet">
                                <label for="redes-sociales">Redes Sociales</label>
                                <input type="text" id="redes-sociales" name="redes_sociales" placeholder="Ej. Instagram: @forthing.arg">
                            </div>
                            
                            <div class="input-group">
                                <label for="fecha-apertura" class="required-label">Fecha de Apertura Aproximada</label>"""
content = content.replace(old_redes, new_redes)

# 2. Replace tbody
tbody_start = '<tbody id="personal-table-body">'
tbody_end = '</tbody>'
start_idx = content.find(tbody_start)
end_idx = content.find(tbody_end) + len(tbody_end)

roles = [
    ("Responsable de Ventas", "Responsable de Ventas"),
    ("Vendedor", "Vendedor"),
    ("Responsable de Administración", "Responsable de Administración"),
    ("Responsable de Repuestos", "Responsable de Repuestos"),
    ("Responsable de Postventa", "Responsable de Postventa"),
    ("Mecánico", "Mecánico"),
    ("Mecánico", "Mecánico")
]

new_tbody = '<tbody id="personal-table-body">\n'
new_tbody += """                                    <!-- Dynamic Director Row -->
                                    <tr class="table-row">
                                        <td>
                                            <input type="text" class="table-input col-cargo" id="cargo-director" value="" readonly style="background-color: #F3F4F6; cursor: not-allowed; color: #4B5563; font-weight: 500;" placeholder="Seleccione Tipo de Razón Social...">
                                        </td>
                                        <td><input type="text" class="table-input col-nombre" placeholder="Nombre y Apellido"></td>
                                        <td><input type="email" class="table-input col-email" placeholder="email@ejemplo.com"></td>
                                        <td><input type="tel" class="table-input col-telefono" placeholder="Teléfono"></td>
                                        <td class="actions-col"></td>
                                    </tr>\n"""

for role_id, role_val in roles:
    new_tbody += f"""                                    <tr class="table-row">
                                        <td>
                                            <input type="text" class="table-input col-cargo" value="{role_val}" readonly style="background-color: #F3F4F6; cursor: not-allowed; color: #4B5563; font-weight: 500;">
                                        </td>
                                        <td><input type="text" class="table-input col-nombre" placeholder="Nombre y Apellido"></td>
                                        <td><input type="email" class="table-input col-email" placeholder="email@ejemplo.com"></td>
                                        <td><input type="tel" class="table-input col-telefono" placeholder="Teléfono"></td>
                                        <td class="actions-col"></td>
                                    </tr>\n"""
new_tbody += '                                </tbody>'

content = content[:start_idx] + new_tbody + content[end_idx:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated index.html")
