import os

file_path = "app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update the setup part
old_setup = """        const previewContainer = card.querySelector('.preview-container');
        
        // Setup preview container for multiple images
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'flex';
        previewContainer.style.flexWrap = 'wrap';
        previewContainer.style.gap = '10px';
        previewContainer.style.marginTop = '15px';"""

new_setup = """        const previewContainer = card.querySelector('.preview-container');
        const dropzonePrompt = card.querySelector('.dropzone-prompt');
        
        // Setup preview container for multiple images
        previewContainer.innerHTML = '';
        previewContainer.style.display = 'none';
        previewContainer.style.position = 'relative';
        previewContainer.style.backgroundColor = 'transparent';
        previewContainer.style.flexWrap = 'wrap';
        previewContainer.style.gap = '10px';
        previewContainer.style.marginTop = '15px';"""

content = content.replace(old_setup, new_setup)

# 2. Update renderPreviews part
old_render = """        function renderPreviews() {
            previewContainer.innerHTML = '';
            if (window.categoryImages[cat].length > 0) {
                previewContainer.style.display = 'flex';"""

new_render = """        function renderPreviews() {
            previewContainer.innerHTML = '';
            if (window.categoryImages[cat].length > 0) {
                if(dropzonePrompt) dropzonePrompt.style.display = 'none';
                previewContainer.style.display = 'flex';"""

content = content.replace(old_render, new_render)

old_render_else = """            } else {
                previewContainer.style.display = 'none';
            }
            updateFormProgress();"""

new_render_else = """            } else {
                if(dropzonePrompt) dropzonePrompt.style.display = 'flex';
                previewContainer.style.display = 'none';
            }
            updateFormProgress();"""

content = content.replace(old_render_else, new_render_else)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.js to fix dropzone visibility")
