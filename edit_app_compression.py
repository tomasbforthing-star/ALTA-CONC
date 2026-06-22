import os

file_path = "app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

resize_fn = """
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
"""

# Insert resize_fn at the top or near the photo upload section
insert_pos = content.find("const photoCategories = ['frente', 'salon', 'taller', 'deposito', 'postventa', 'administrativa'];")
if insert_pos != -1:
    content = content[:insert_pos] + resize_fn + "\n    " + content[insert_pos:]

old_preview = """                // Preview image using FileReader
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onloadend = () => {
                    window.categoryImages[cat].push(reader.result);
                    renderPreviews();
                };"""

new_preview = """                // Preview and compress image
                resizeImage(file, 1200, 1200, 0.7)
                    .then(base64Str => {
                        window.categoryImages[cat].push(base64Str);
                        renderPreviews();
                        updateFormProgress();
                    })
                    .catch(err => {
                        console.error("Error compressing image:", err);
                        alert("Hubo un error procesando la imagen. Intente de nuevo.");
                    });"""

content = content.replace(old_preview, new_preview)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.js for compression")
