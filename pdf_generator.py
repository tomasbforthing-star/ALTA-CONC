import os
import io
import base64
import tempfile
from PIL import Image as PILImage
from pypdf import PdfReader, PdfWriter

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas to calculate total page count and render page numbers
    dynamically at the bottom right.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#6B7280")) # var(--text-muted)
        
        # Draw submission footer note
        self.drawString(54, 30, "Portal de Alta de Concesionarios – Forthing Argentina")
        
        # Draw page numbers at bottom right (Landscape page width is A4[1])
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[1] - 54, 30, page_text)
        self.restoreState()


def decode_base64_image(base64_str):
    """Decodes a base64 string and returns bytes."""
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    return base64.b64decode(base64_str)


def create_temp_image_file(image_bytes, max_width=600, max_height=300):
    """
    Saves image bytes to a temp file, resizes it while maintaining aspect ratio
    to fit the landscape page, and returns the path to the temp file.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        img = PILImage.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if in RGBA mode (JPEG doesn't support transparency)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            background = PILImage.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
            img = background
            
        img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
        img.save(temp_file.name, "JPEG", quality=85)
        return temp_file.name
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


def generate_pdf_content(data, temp_pdf_path):
    """Generates the raw PDF content using ReportLab Flowables in Landscape mode."""
    
    # Page setup: A4 Landscape size (841.89 x 595.27)
    # Margins: Top 115pt (to avoid logo overlap), Bottom 65pt, Left/Right 54pt
    doc = SimpleDocTemplate(
        temp_pdf_path,
        pagesize=landscape(A4),
        leftMargin=54,
        rightMargin=54,
        topMargin=115,
        bottomMargin=65
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Colors
    primary_color = colors.HexColor("#0D0E12")
    accent_color = colors.HexColor("#C5A85A")
    muted_color = colors.HexColor("#4B5563")
    light_border_color = colors.HexColor("#E5E7EB")
    
    # Custom Styles matching Forthing premium identity
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=muted_color,
        spaceAfter=15
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.white
    )
    
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.white
    )

    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    field_label_style = ParagraphStyle(
        'FieldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=muted_color
    )
    
    field_val_style = ParagraphStyle(
        'FieldVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=primary_color
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=primary_color
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=primary_color
    )

    story = []

    # Title Banner
    story.append(Paragraph("SOLICITUD DE ALTA DE CONCESIONARIO", title_style))
    story.append(Paragraph("Evaluación e Incorporación a la Red Oficial Forthing Argentina", subtitle_style))
    
    # Request Metadata Block (Request Number & Date)
    # Total landscape printable width is 733.89. We target 730 points for layout tables.
    meta_data = [
        [
            Paragraph("N° de Solicitud:", meta_label_style),
            Paragraph(data.get('solicitud_nro', 'FTH-2026-XXXX'), meta_val_style),
            Paragraph("Fecha de Solicitud:", meta_label_style),
            Paragraph(data.get('fecha_solicitud', '18/06/2026'), meta_val_style)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[130, 235, 130, 235])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, accent_color),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Helpers to write sections
    def add_section_divider(title_text):
        divider_data = [[Paragraph(title_text, section_title_style)]]
        divider_table = Table(divider_data, colWidths=[730])
        divider_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 1, accent_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(KeepTogether([divider_table, Spacer(1, 6)]))

    # SECTION 1: Datos Generales
    add_section_divider("1. DATOS GENERALES DEL CONCESIONARIO")
    
    general_data = [
        [
            Paragraph("Nombre Comercial:", field_label_style),
            Paragraph(data.get('nombre_concesionario', ''), field_val_style),
            Paragraph("Razón Social:", field_label_style),
            Paragraph(data.get('razon_social', ''), field_val_style),
        ],
        [
            Paragraph("Tipo Razón Social:", field_label_style),
            Paragraph(data.get('tipo_razon_social', ''), field_val_style),
            Paragraph("CUIT:", field_label_style),
            Paragraph(data.get('cuit', ''), field_val_style),
        ],
        [
            Paragraph("Dirección Legal:", field_label_style),
            Paragraph(data.get('direccion_legal', ''), field_val_style),
            Paragraph("Ciudad:", field_label_style),
            Paragraph(data.get('ciudad', ''), field_val_style),
        ],
        [
            Paragraph("Provincia:", field_label_style),
            Paragraph(data.get('provincia', ''), field_val_style),
            Paragraph("Teléfono Principal:", field_label_style),
            Paragraph(data.get('telefono_principal', ''), field_val_style),
        ],
        [
            Paragraph("Correo Principal:", field_label_style),
            Paragraph(data.get('email_principal', ''), field_val_style),
            Paragraph("Sitio Web:", field_label_style),
            Paragraph(data.get('sitio_web', ''), field_val_style),
        ],
        [
            Paragraph("Apertura Estimada:", field_label_style),
            Paragraph(data.get('fecha_apertura', ''), field_val_style),
            Paragraph("Redes Sociales:", field_label_style),
            Paragraph(data.get('redes_sociales', ''), field_val_style),
        ]
    ]
    
    general_table = Table(general_data, colWidths=[140, 225, 140, 225])
    general_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, light_border_color),
    ]))
    story.append(general_table)
    story.append(Spacer(1, 10))

    # SECTION 2: Experiencia Comercial
    add_section_divider("2. EXPERIENCIA COMERCIAL")
    
    chk_vehicles = data.get('tipo_vehiculo', [])
    chk_str = ", ".join(chk_vehicles) if chk_vehicles else "Ninguno seleccionado"
    if "Otros" in chk_vehicles and data.get('otros_especificar'):
        chk_str += f" ({data.get('otros_especificar')})"
        
    comercial_data = [
        [
            Paragraph("Otras Marcas Representadas:", field_label_style),
            Paragraph(data.get('otras_marcas', 'No declara otras marcas representadas.').replace('\n', '<br/>'), field_val_style)
        ],
        [
            Paragraph("Tipos de Vehículos Comercializados:", field_label_style),
            Paragraph(chk_str, field_val_style)
        ]
    ]
    comercial_table = Table(comercial_data, colWidths=[200, 530])
    comercial_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, light_border_color),
    ]))
    story.append(comercial_table)
    story.append(Spacer(1, 10))

    # SECTION 3: Capacidad Operativa & Superficies
    add_section_divider("3. CAPACIDAD OPERATIVA Y SUPERFICIES")
    
    cap_data = [
        [
            Paragraph("Empleados Totales:", field_label_style),
            Paragraph(str(data.get('cant_empleados', '0')), field_val_style),
            Paragraph("Salón de Ventas:", field_label_style),
            Paragraph(f"{data.get('sup_salon', '0')} m²", field_val_style),
        ],
        [
            Paragraph("Técnicos Certificados:", field_label_style),
            Paragraph(str(data.get('cant_tecnicos', '0')), field_val_style),
            Paragraph("Taller Mecánico:", field_label_style),
            Paragraph(f"{data.get('sup_taller', '0')} m²", field_val_style),
        ],
        [
            Paragraph("Puestos de Taller:", field_label_style),
            Paragraph(str(data.get('cant_puestos', '0')), field_val_style),
            Paragraph("Depósito Repuestos:", field_label_style),
            Paragraph(f"{data.get('sup_deposito', '0')} m²", field_val_style),
        ],
        [
            Paragraph("Elevadores:", field_label_style),
            Paragraph(str(data.get('cant_elevadores', '0')), field_val_style),
            Paragraph("Área Administrativa:", field_label_style),
            Paragraph(f"{data.get('sup_admin', '0')} m²", field_val_style),
        ],
        [
            Paragraph("Servicios Mensuales Est.:", field_label_style),
            Paragraph(str(data.get('capacidad_servicios', '0')), field_val_style),
            Paragraph("Área Postventa:", field_label_style),
            Paragraph(f"{data.get('sup_postventa', '0')} m²", field_val_style),
        ],
        [
            Paragraph("", field_label_style),
            Paragraph("", field_val_style),
            Paragraph("Superficie Total:", ParagraphStyle('BoldLabel', parent=field_label_style, textColor=primary_color)),
            Paragraph(f"<b>{data.get('sup_total', '0')} m²</b>", field_val_style),
        ]
    ]
    cap_table = Table(cap_data, colWidths=[180, 185, 180, 185])
    cap_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, light_border_color),
    ]))
    story.append(cap_table)
    story.append(Spacer(1, 10))

    # SECTION 5: Personal del Concesionario
    add_section_divider("4. PERSONAL DEL CONCESIONARIO")
    
    staff_list = data.get('personal', [])
    if staff_list:
        staff_data = [[
            Paragraph("Cargo", table_header_style),
            Paragraph("Nombre y Apellido", table_header_style),
            Paragraph("Correo Electrónico", table_header_style),
            Paragraph("Teléfono", table_header_style)
        ]]
        
        for idx, member in enumerate(staff_list):
            staff_data.append([
                Paragraph(member.get('cargo', '-'), table_cell_style),
                Paragraph(member.get('nombre', '-'), table_cell_style),
                Paragraph(member.get('email', '-'), table_cell_style),
                Paragraph(member.get('telefono', '-'), table_cell_style)
            ])
            
        staff_table = Table(staff_data, colWidths=[180, 205, 195, 150])
        
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, light_border_color),
        ]
        
        for i in range(1, len(staff_data)):
            if i % 2 == 0:
                t_style.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor("#F9FAFB")))
                
        staff_table.setStyle(TableStyle(t_style))
        story.append(staff_table)
    else:
        story.append(Paragraph("No se ha cargado información de personal.", field_val_style))
    story.append(Spacer(1, 10))

    # SECTION 7: Observaciones
    obs_text = data.get('observaciones', '').strip()
    if obs_text:
        add_section_divider("5. OBSERVACIONES ADICIONALES")
        story.append(Paragraph(obs_text.replace('\n', '<br/>'), field_val_style))
        story.append(Spacer(1, 10))

    # ANEXO FOTOGRÁFICO
    photos_dict = data.get('imagenes', {})
    has_photos = any(photos_dict.values())
    
    if has_photos:
        story.append(PageBreak())
        story.append(Paragraph("REGISTRO FOTOGRÁFICO DE INSTALACIONES", title_style))
        story.append(Paragraph("Documentación visual del concesionario para análisis corporativo.", subtitle_style))
        
        photo_labels = {
            'frente': 'Frente del Concesionario',
            'salon': 'Salón de Ventas',
            'taller': 'Taller Mecánico',
            'deposito': 'Depósito de Repuestos',
            'postventa': 'Área de Postventa',
            'administrativa': 'Área Administrativa'
        }
        
        temp_files_to_clean = []
        
        for key, base64_list in photos_dict.items():
            if not isinstance(base64_list, list):
                if base64_list:
                    base64_list = [base64_list]
                else:
                    base64_list = []
                    
            if base64_list:
                label = photo_labels.get(key, key.capitalize())
                story.append(Paragraph(f"<b>Categoría: {label}</b>", section_title_style))
                story.append(Spacer(1, 4))
                
                for idx, base64_str in enumerate(base64_list):
                    if not base64_str:
                        continue
                        
                    try:
                        img_bytes = decode_base64_image(base64_str)
                        temp_img_path = create_temp_image_file(img_bytes)
                        
                        if temp_img_path:
                            temp_files_to_clean.append(temp_img_path)
                            
                            with PILImage.open(temp_img_path) as pimg:
                                w, h = pimg.size
                                
                            story.append(KeepTogether([
                                Paragraph(f"Foto {idx+1}", field_label_style),
                                Spacer(1, 2),
                                Image(temp_img_path, width=w, height=h),
                                Spacer(1, 10)
                            ]))
                    except Exception as ex:
                        story.append(KeepTogether([
                            Paragraph(f"Foto {idx+1}", field_label_style),
                            Spacer(1, 2),
                            Paragraph(f"<font color='red'>Error cargando imagen: {ex}</font>", field_val_style),
                            Spacer(1, 10)
                        ]))
                story.append(Spacer(1, 5))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Cleanup temp images now that PDF is generated
    if has_photos:
        for f in temp_files_to_clean:
            try:
                os.remove(f)
            except OSError:
                pass


def generate_final_pdf(data, output_pdf_path, template_pdf_path):
    """
    Generates the content PDF in landscape orientation and merges it page-by-page
    with the letterhead PDF template file.
    """
    # Create a temporary PDF to hold ReportLab's output
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf_path = temp_pdf.name
        
    try:
        # 1. Generate programmatic PDF text and tables in Landscape
        generate_pdf_content(data, temp_pdf_path)
        
        # 2. Merge/Overlay with the corporate template PDF
        bg_reader = PdfReader(template_pdf_path)
        bg_page = bg_reader.pages[0] # The landscape letterhead template
        
        content_reader = PdfReader(temp_pdf_path)
        writer = PdfWriter()
        
        for page in content_reader.pages:
            # Create a blank sheet with matching landscape dimensions
            new_page = bg_page.create_blank_page(
                width=bg_page.mediabox.width,
                height=bg_page.mediabox.height
            )
            
            # Merge background first, then text content on top
            new_page.merge_page(bg_page)
            new_page.merge_page(page)
            writer.add_page(new_page)
            
        # 3. Write final output file
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)
            
        return True
        
    except Exception as e:
        print(f"Error generating final merged PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Always remove the temporary content PDF file
        try:
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
        except OSError:
            pass
