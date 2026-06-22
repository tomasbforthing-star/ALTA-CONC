document.addEventListener('DOMContentLoaded', () => {

function resizeImage(file, maxWidth, maxHeight, quality) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                let width = img.width;
                let height = img.height;

                if (width > height) {
                    if (width > maxWidth) {
                        height = Math.round((height * maxWidth) / width);
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width = Math.round((width * maxHeight) / height);
                        height = maxHeight;
                    }
                }

                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;

                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);

                const dataUrl = canvas.toDataURL('image/jpeg', quality);
                resolve(dataUrl);
            };
            img.onerror = reject;
            img.src = e.target.result;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

    
    // Core Elements
    const form = document.getElementById('onboarding-form');
    const sections = document.querySelectorAll('.form-card-section');
    const stepItems = document.querySelectorAll('.step-item');
    const mainProgressBar = document.getElementById('main-progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    const successModal = document.getElementById('success-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    
    // ----------------------------------------------------
    // 1. Navigation & Progress / ScrollSpy
    // ----------------------------------------------------
    
    // Click step to scroll
    stepItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            const targetSection = document.getElementById(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ScrollSpy: Highlight active step based on scroll position
    const scrollSpyOptions = {
        root: null,
        rootMargin: '-20% 0px -60% 0px', // Trigger when section is in the middle of screen
        threshold: 0
    };

    const scrollSpyObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                
                // Update active class in sidebar
                stepItems.forEach(item => {
                    if (item.getAttribute('data-target') === id) {
                        item.classList.add('active');
                    } else {
                        item.classList.remove('active');
                    }
                });
            }
        });
    }, scrollSpyOptions);

    sections.forEach(section => scrollSpyObserver.observe(section));

    // Dynamic Progress Tracking
    // Helper function to check if a specific section is complete
    function isSectionComplete(section) {
        const stepNum = section.getAttribute('data-step');
        
        if (stepNum === '1') {
            // Section 1: Datos Generales (All fields with [required] must be filled and valid)
            const requiredFields = section.querySelectorAll('[required]');
            let valid = true;
            requiredFields.forEach(field => {
                if (!field.value || field.value.trim() === '' || !field.checkValidity()) {
                    valid = false;
                }
            });
            const cuitField = section.querySelector('#cuit');
            if (cuitField && cuitField.value) {
                const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;
                if (!cuitRegex.test(cuitField.value)) {
                    valid = false;
                }
            }
            return valid;
        }
        
        if (stepNum === '2') {
            // Section 2: Experiencia Comercial (At least one vehicle type checked, or brands filled)
            const checkboxes = section.querySelectorAll('input[name="tipo_vehiculo"]:checked');
            const marcasInput = section.querySelector('#otras-marcas');
            const marcasVal = marcasInput ? marcasInput.value.trim() : '';
            return checkboxes.length > 0 || marcasVal !== '';
        }
        
        if (stepNum === '3') {
            // Section 3: Capacidad Operativa (At least one number field must be filled)
            const numInputs = section.querySelectorAll('input[type="number"]');
            let hasValue = false;
            numInputs.forEach(input => {
                if (input.value !== '' && !isNaN(parseFloat(input.value)) && parseFloat(input.value) >= 0) {
                    hasValue = true;
                }
            });
            return hasValue;
        }
        
        if (stepNum === '4') {
            // Section 4: Superficies (All sector fields filled, total > 0)
            const supInputs = section.querySelectorAll('.sup-input');
            const totalInput = section.querySelector('#sup-total');
            const totalVal = totalInput ? parseFloat(totalInput.value) : 0;
            if (totalVal <= 0) return false;
            
            let allFilled = true;
            supInputs.forEach(input => {
                if (input.value === '') {
                    allFilled = false;
                }
            });
            return allFilled;
        }
        
        if (stepNum === '5') {
            // Section 5: Personal (At least one contact name filled in the table)
            const names = Array.from(section.querySelectorAll('.col-nombre')).map(input => input.value.trim());
            const filledNames = names.filter(name => name !== '');
            return filledNames.length > 0;
        }
        
        if (stepNum === '6') {
            // Section 6: Registro Fotográfico (At least one photo uploaded)
            const previewImages = section.querySelectorAll('.preview-img');
            let hasPhoto = false;
            previewImages.forEach(img => {
                if (img.getAttribute('src') !== '') {
                    hasPhoto = true;
                }
            });
            return hasPhoto;
        }
        
        if (stepNum === '7') {
            // Section 7: Observaciones (Marked complete if observations text is filled)
            const obsTextarea = section.querySelector('#observaciones');
            return obsTextarea && obsTextarea.value.trim() !== '';
        }
        
        return false;
    }

    // Dynamic Progress Tracking
    function updateFormProgress() {
        // 1. Calculate section completion for the sidebar checkmarks
        sections.forEach(section => {
            const stepItem = document.querySelector(`.step-item[data-target="${section.id}"]`);
            const sectionValid = isSectionComplete(section);
            
            if (sectionValid) {
                if (stepItem) stepItem.classList.add('completed');
            } else {
                if (stepItem) stepItem.classList.remove('completed');
            }
        });
        
        // 2. Calculate progress bar percentage specifically based on completed core sections (1 to 5)
        const coreSectionIds = [
            'sec-datos-generales',
            'sec-experiencia-comercial',
            'sec-capacidad-operativa',
            'sec-superficies',
            'sec-personal'
        ];
        
        let completedCore = 0;
        coreSectionIds.forEach(id => {
            const sec = document.getElementById(id);
            if (sec && isSectionComplete(sec)) {
                completedCore++;
            }
        });
        
        const percentage = Math.round((completedCore / coreSectionIds.length) * 100);
        mainProgressBar.style.width = `${percentage}%`;
        progressPercentage.innerText = `${percentage}%`;
    }

    // Attach real-time validation listeners to trigger progress bar updates
    form.addEventListener('input', updateFormProgress);
    form.addEventListener('change', updateFormProgress);
    
    // Initialize progress on load
    updateFormProgress();


    // ----------------------------------------------------
    
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

    // 2. Section 2: Conditional "Otros" Checkbox
    // ----------------------------------------------------
    const chkOtros = document.getElementById('chk-otros');
    const wrapperOtros = document.getElementById('wrapper-otros-especificar');
    const inputOtros = document.getElementById('otros-especificar');

    if (chkOtros && wrapperOtros && inputOtros) {
        chkOtros.addEventListener('change', () => {
            if (chkOtros.checked) {
                wrapperOtros.classList.add('show-conditional');
                inputOtros.setAttribute('required', 'required');
            } else {
                wrapperOtros.classList.remove('show-conditional');
                inputOtros.removeAttribute('required');
                inputOtros.value = ''; // Clear field
                // Remove error styling if hidden
                const group = inputOtros.closest('.input-group');
                if (group) group.classList.remove('invalid-field');
            }
            updateFormProgress();
        });
    }


    // ----------------------------------------------------
    // 3. Section 4: Surface Area Calculation (m²)
    // ----------------------------------------------------
    const supInputs = document.querySelectorAll('.sup-input');
    const supTotal = document.getElementById('sup-total');

    function calculateTotalSurface() {
        let total = 0;
        supInputs.forEach(input => {
            const val = parseFloat(input.value);
            if (!isNaN(val) && val > 0) {
                total += val;
            }
        });
        // Render total
        supTotal.value = total > 0 ? total : 0;
    }

    supInputs.forEach(input => {
        input.addEventListener('input', calculateTotalSurface);
    });


    // ----------------------------------------------------
    // 4. Section 5: Personnel Dynamic Table
    // ----------------------------------------------------
    const personalTableBody = document.getElementById('personal-table-body');
    const btnAddPersonal = document.getElementById('btn-add-personal');

    // Add Row Handler
    if (btnAddPersonal && personalTableBody) {
        btnAddPersonal.addEventListener('click', () => {
            const newRow = document.createElement('tr');
            newRow.className = 'table-row';
            newRow.innerHTML = `
                <td>
                    <input type="text" class="table-input col-cargo" placeholder="Cargo (Ej. Tesorero)">
                </td>
                <td>
                    <input type="text" class="table-input col-nombre" placeholder="Nombre y Apellido">
                </td>
                <td>
                    <input type="email" class="table-input col-email" placeholder="email@ejemplo.com">
                </td>
                <td>
                    <input type="tel" class="table-input col-telefono" placeholder="Teléfono">
                </td>
                <td class="actions-col">
                    <button type="button" class="btn-delete-row" title="Eliminar fila">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>
                    </button>
                </td>
            `;
            personalTableBody.appendChild(newRow);
            
            // Focus on the new row's first input
            newRow.querySelector('.col-cargo').focus();
            
            // Update validation and UI states if needed
            updateFormProgress();
        });
    }

    // Delete Row (using delegation on table body)
    if (personalTableBody) {
        personalTableBody.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('.btn-delete-row');
            if (deleteBtn) {
                const row = deleteBtn.closest('tr');
                if (row) {
                    row.style.opacity = '0';
                    row.style.transform = 'scale(0.95)';
                    row.style.transition = 'all 0.2s ease';
                    setTimeout(() => {
                        row.remove();
                        updateFormProgress();
                    }, 200);
                }
            }
        });
    }


    // ----------------------------------------------------
    // 5. Section 6: Photo Uploader Cards (Drag & Drop)
    // ----------------------------------------------------
    const uploaderCards = document.querySelectorAll('.uploader-card');
    window.categoryImages = { frente: [], salon: [], taller: [], deposito: [], postventa: [], administrativa: [] };

    uploaderCards.forEach(card => {
        const cat = card.getAttribute('data-category');
        const dropzone = card.querySelector('.dropzone');
        const fileInput = card.querySelector('.file-input-hidden');
        const previewContainer = card.querySelector('.preview-container');
        const dropzonePrompt = card.querySelector('.dropzone-prompt');
        
        // Setup preview container for multiple images
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
        previewContainer.style.position = 'relative';
        previewContainer.style.backgroundColor = 'transparent';
        previewContainer.style.flexWrap = 'wrap';
        previewContainer.style.gap = '10px';
        previewContainer.style.marginTop = '15px';
        
        // Trigger file picker on dropzone click (excluding actions overlay clicking)
        dropzone.addEventListener('click', (e) => {
            if (e.target.closest('.preview-actions') || e.target.closest('.btn-action-preview') || e.target.closest('.multi-preview-item')) {
                return; // Let actions work normally
            }
            fileInput.click();
        });

        // Drag & Drop event listeners
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            }, false);
        });

        // File drop handler
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt.files.length > 0) {
                handleUploadedFiles(dt.files);
            }
        });

        // File pick handler
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                handleUploadedFiles(fileInput.files);
            }
            fileInput.value = ''; // clear to allow same file re-selection if needed
        });

        function handleUploadedFiles(files) {
            for(let i=0; i<files.length; i++) {
                const file = files[i];
                if (window.categoryImages[cat].length >= 5) {
                    alert('Límite de 5 fotos por categoría alcanzado.');
                    break;
                }
                
                // File validation: Type
                const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Formato de archivo no válido. Utilice JPG, PNG o WEBP.');
                    continue;
                }

                // File validation: Size (10 MB = 10 * 1024 * 1024 bytes)
                const maxSize = 10 * 1024 * 1024;
                if (file.size > maxSize) {
                    alert('El archivo supera el tamaño máximo de 10 MB.');
                    continue;
                }

                // Preview and compress image
                resizeImage(file, 800, 800, 0.6)
                    .then(base64Str => {
                        window.categoryImages[cat].push(base64Str);
                        renderPreviews();
                        updateFormProgress();
                    })
                    .catch(err => {
                        console.error("Error compressing image:", err);
                        alert("Hubo un error procesando la imagen. Intente de nuevo.");
                    });
            }
        }

        function renderPreviews() {
            previewContainer.innerHTML = '';
            if (window.categoryImages[cat].length > 0) {
                if(dropzonePrompt) dropzonePrompt.style.display = 'none';
                previewContainer.style.display = 'flex';
                window.categoryImages[cat].forEach((base64Str, index) => {
                    const item = document.createElement('div');
                    item.className = 'multi-preview-item';
                    item.style.position = 'relative';
                    item.style.width = '100px';
                    item.style.height = '100px';
                    item.style.borderRadius = '8px';
                    item.style.overflow = 'hidden';
                    item.style.border = '1px solid #E5E7EB';
                    
                    const img = document.createElement('img');
                    img.src = base64Str;
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'cover';
                    
                    const btnDel = document.createElement('button');
                    btnDel.type = 'button';
                    btnDel.innerHTML = '×';
                    btnDel.title = 'Eliminar foto';
                    btnDel.style.position = 'absolute';
                    btnDel.style.top = '4px';
                    btnDel.style.right = '4px';
                    btnDel.style.background = 'rgba(220, 38, 38, 0.9)';
                    btnDel.style.color = 'white';
                    btnDel.style.border = 'none';
                    btnDel.style.borderRadius = '50%';
                    btnDel.style.width = '24px';
                    btnDel.style.height = '24px';
                    btnDel.style.cursor = 'pointer';
                    btnDel.style.fontWeight = 'bold';
                    btnDel.style.display = 'flex';
                    btnDel.style.alignItems = 'center';
                    btnDel.style.justifyContent = 'center';
                    
                    btnDel.onclick = (e) => {
                        e.stopPropagation();
                        window.categoryImages[cat].splice(index, 1);
                        renderPreviews();
                    };
                    
                    item.appendChild(img);
                    item.appendChild(btnDel);
                    previewContainer.appendChild(item);
                });
            } else {
                if(dropzonePrompt) dropzonePrompt.style.display = 'flex';
                previewContainer.style.display = 'none';
            }
            updateFormProgress();
        }
    });


    // CUIT formatter helper while typing
    const cuitField = document.getElementById('cuit');
    if (cuitField) {
        cuitField.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, ''); // Numbers only
            let formatted = '';
            if (val.length > 0) {
                formatted += val.substring(0, 2);
            }
            if (val.length > 2) {
                formatted += '-' + val.substring(2, 10);
            }
            if (val.length > 10) {
                formatted += '-' + val.substring(10, 11);
            }
            e.target.value = formatted;
        });
    }

    // ----------------------------------------------------
    // 6. Form Submission & Validation
    // ----------------------------------------------------
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        let isFormValid = true;
        let firstInvalidField = null;

        // Perform custom validation checks on all required inputs
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (field.type === 'file') return; // Image validation handled separately below

            const inputGroup = field.closest('.input-group') || field.closest('.superficie-card');
            
            // Remove previous error states
            if (inputGroup) {
                inputGroup.classList.remove('invalid-field');
            }

            // Check field validity
            if (!field.value || field.value.trim() === '' || !field.checkValidity()) {
                isFormValid = false;
                if (inputGroup) {
                    inputGroup.classList.add('invalid-field');
                    
                    // Create dynamic validation message if not present
                    let errorMsg = inputGroup.querySelector('.field-error-msg');
                    if (!errorMsg) {
                        errorMsg = document.createElement('span');
                        errorMsg.className = 'field-error-msg';
                        errorMsg.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> Este campo es obligatorio o tiene un formato inválido.`;
                        inputGroup.appendChild(errorMsg);
                    }
                }
                if (!firstInvalidField) {
                    firstInvalidField = field;
                }
            }
        });
        
        // Validate Image uploads
        


    const photoCategories = ['frente', 'salon', 'taller', 'deposito', 'postventa', 'administrativa'];
        for(let cat of photoCategories) {
            const dropzone = document.getElementById(`dropzone-${cat}`);
            if(!window.categoryImages[cat] || window.categoryImages[cat].length === 0) {
                isFormValid = false;
                if (dropzone) {
                    dropzone.style.borderColor = '#DC2626';
                    dropzone.style.backgroundColor = '#FEF2F2';
                    if (!firstInvalidField) firstInvalidField = dropzone;
                }
            } else {
                if (dropzone) {
                    dropzone.style.borderColor = '#D1D5DB';
                    dropzone.style.backgroundColor = '#F9FAFB';
                }
            }
        }

        // Validate CUIT pattern specifically
        if (cuitField && cuitField.value) {
            const cuitRegex = /^\d{2}-\d{8}-\d{1}$/;
            const inputGroup = cuitField.closest('.input-group');
            if (!cuitRegex.test(cuitField.value)) {
                isFormValid = false;
                if (inputGroup) {
                    inputGroup.classList.add('invalid-field');
                    let errorMsg = inputGroup.querySelector('.field-error-msg');
                    if (!errorMsg) {
                        errorMsg = document.createElement('span');
                        errorMsg.className = 'field-error-msg';
                        inputGroup.appendChild(errorMsg);
                    }
                    errorMsg.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg> Ingrese un CUIT válido en formato XX-XXXXXXXX-X.`;
                }
                if (!firstInvalidField) {
                    firstInvalidField = cuitField;
                }
            }
        }

        if (isFormValid) {
            // 1. Gather all form fields into JSON format
            const formData = {
                nombre_concesionario: document.getElementById('nombre-concesionario').value,
                razon_social: document.getElementById('razon-social').value,
                tipo_razon_social: document.getElementById('tipo-razon-social').value,
                cuit: document.getElementById('cuit').value,
                direccion_legal: document.getElementById('direccion-legal').value,
                ciudad: document.getElementById('ciudad').value,
                provincia: document.getElementById('provincia').value,
                telefono_principal: document.getElementById('telefono-principal').value,
                email_principal: document.getElementById('email-principal').value,
                sitio_web: document.getElementById('sitio-web').value,
                redes_sociales: document.getElementById('redes-sociales') ? document.getElementById('redes-sociales').value : '',
                fecha_apertura: document.getElementById('fecha-apertura').value,
                
                otras_marcas: document.getElementById('otras-marcas').value,
                tipo_vehiculo: Array.from(form.querySelectorAll('input[name="tipo_vehiculo"]:checked')).map(cb => cb.value),
                otros_especificar: document.getElementById('otros-especificar').value,
                
                cant_empleados: parseInt(document.getElementById('cant-empleados').value) || 0,
                cant_tecnicos: parseInt(document.getElementById('cant-tecnicos').value) || 0,
                cant_puestos: parseInt(document.getElementById('cant-puestos').value) || 0,
                cant_elevadores: parseInt(document.getElementById('cant-elevadores').value) || 0,
                capacidad_servicios: parseInt(document.getElementById('capacidad-servicios').value) || 0,
                
                sup_salon: parseFloat(document.getElementById('sup-salon').value) || 0,
                sup_taller: parseFloat(document.getElementById('sup-taller').value) || 0,
                sup_deposito: parseFloat(document.getElementById('sup-deposito').value) || 0,
                sup_admin: parseFloat(document.getElementById('sup-admin').value) || 0,
                sup_postventa: parseFloat(document.getElementById('sup-postventa').value) || 0,
                sup_total: parseFloat(document.getElementById('sup-total').value) || 0,
                
                observaciones: document.getElementById('observaciones').value,
                
                // Read personnel table dynamically
                personal: [],
                
                // Read image base64 strings
                imagenes: window.categoryImages
            };
            
            // Read personal table rows
            const rowElements = document.querySelectorAll('#personal-table-body tr');
            rowElements.forEach(row => {
                const cargo = row.querySelector('.col-cargo').value;
                const nombre = row.querySelector('.col-nombre').value;
                const email = row.querySelector('.col-email').value;
                const telefono = row.querySelector('.col-telefono').value;
                
                // Only add if at least nombre, email or telefono is filled
                if (nombre.trim() !== '' || email.trim() !== '' || telefono.trim() !== '') {
                    formData.personal.push({ cargo, nombre, email, telefono });
                }
            });

            // Show loading state on submit button
            const submitBtn = document.getElementById('btn-submit-form');
            const originalBtnContent = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                ENVIANDO SOLICITUD...
                <svg class="spinner-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" style="animation: spin 1s linear infinite; margin-left: 8px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            `;
            
            // Send JSON to backend
            fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => {
                        throw new Error(errData.details || errData.error || 'Falla en el procesamiento de la solicitud.');
                    });
                }
                return response.json();
            })
            .then(resData => {
                // Update modal details
                const modalTitle = successModal.querySelector('.modal-title');
                const modalMsg = successModal.querySelector('.modal-message');
                
                modalTitle.innerText = "Solicitud Enviada Correctamente";
                
                let warningText = "";
                if (resData.email_warning) {
                    console.warn("SMTP email dispatch warning:", resData.email_warning);
                    warningText = `<br><br><span style="display: block; background-color: #FEF3C7; border: 1px solid #FCD34D; color: #92400E; padding: 12px; border-radius: 6px; font-size: 0.8rem; text-align: left; line-height: 1.4;">⚠️ <b>Nota de desarrollo:</b> El PDF fue generado y respaldado localmente, pero el envío de correo SMTP falló (servidor SMTP no disponible localmente). Copia guardada en <code>sent_emails/</code>.</span>`;
                }
                
                modalMsg.innerHTML = `Su solicitud ha sido enviada exitosamente a Forthing Argentina.${warningText}<br><br><b>Número de Solicitud:</b> ${resData.solicitud_nro}<br><br>Nuestro equipo evaluará la información recibida y se pondrá en contacto a través de los datos proporcionados.`;
                
                // Update the download PDF button link
                const downloadPdfBtn = document.getElementById('btn-download-pdf');
                if (downloadPdfBtn && resData.pdf_base64) {
                    try {
                        const byteCharacters = atob(resData.pdf_base64);
                        const byteNumbers = new Array(byteCharacters.length);
                        for (let i = 0; i < byteCharacters.length; i++) {
                            byteNumbers[i] = byteCharacters.charCodeAt(i);
                        }
                        const byteArray = new Uint8Array(byteNumbers);
                        const blob = new Blob([byteArray], { type: 'application/pdf' });
                        const blobUrl = URL.createObjectURL(blob);
                        
                        downloadPdfBtn.href = blobUrl;
                        downloadPdfBtn.download = resData.pdf_filename || "Alta_Concesionario.pdf";
                        downloadPdfBtn.style.display = 'inline-flex';
                    } catch (e) {
                        console.error("Error creating PDF blob:", e);
                        downloadPdfBtn.href = `/api/download/${encodeURIComponent(resData.pdf_filename)}`;
                        downloadPdfBtn.style.display = 'inline-flex';
                    }
                } else if (downloadPdfBtn && resData.pdf_filename) {
                    downloadPdfBtn.href = `/api/download/${encodeURIComponent(resData.pdf_filename)}`;
                    downloadPdfBtn.style.display = 'inline-flex';
                }
                
                // Update the finalize button text
                const finalizeBtn = document.getElementById('btn-close-modal');
                if (finalizeBtn) finalizeBtn.innerText = "FINALIZAR";
                
                // Show Modal
                successModal.classList.add('modal-open');
            })
            .catch(error => {
                alert(`Error al procesar la solicitud:\n\n${error.message}\n\nLos datos ingresados no se han perdido. Por favor, revise e intente nuevamente.`);
            })
            .finally(() => {
                // Restore button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnContent;
            });
            
        } else {
            // Scroll to the first invalid field smoothly
            if (firstInvalidField) {
                firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Briefly focus on the field
                setTimeout(() => {
                    firstInvalidField.focus();
                }, 400);
            }
        }
    });

    // Close Modal Event Handler
    if (btnCloseModal && successModal) {
        btnCloseModal.addEventListener('click', () => {
            successModal.classList.remove('modal-open');
            
            // Clean form and reset uploader files, inputs, etc.
            form.reset();
            
            // Reset PDF download button
            const downloadPdfBtn = document.getElementById('btn-download-pdf');
            if (downloadPdfBtn) {
                downloadPdfBtn.href = '#';
                downloadPdfBtn.style.display = 'none';
            }
            
            // Reset uploader cards previews
            uploaderCards.forEach(card => {
                const previewContainer = card.querySelector('.preview-container');
                const previewImg = card.querySelector('.preview-img');
                const fileInput = card.querySelector('.file-input-hidden');
                
                if (previewContainer && previewImg && fileInput) {
                    fileInput.value = '';
                    previewImg.src = '';
                    previewContainer.style.display = 'none';
                }
            });

            // Reset custom conditional classes
            if (wrapperOtros) {
                wrapperOtros.classList.remove('show-conditional');
                inputOtros.removeAttribute('required');
            }

            // Remove any leftover validation classes
            const invalidGroups = form.querySelectorAll('.invalid-field');
            invalidGroups.forEach(group => group.classList.remove('invalid-field'));

            // Calculate surface areas again (will reset to 0)
            calculateTotalSurface();

            // Re-render progress (will reset to 0%)
            updateFormProgress();

            // Scroll to the top of the form smoothly
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

});
