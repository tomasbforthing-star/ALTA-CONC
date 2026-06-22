import os

file_path = "app.js"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# The function as it currently exists in the file
function_str = """function resizeImage(file, maxWidth, maxHeight, quality) {
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
}"""

# Remove it from its current location
content = content.replace(function_str, "")

# Insert it right after the DOMContentLoaded event listener begins
insert_marker = "document.addEventListener('DOMContentLoaded', () => {"
insert_idx = content.find(insert_marker)

if insert_idx != -1:
    # insert right after the marker
    new_content = content[:insert_idx + len(insert_marker)] + "\n\n" + function_str + "\n" + content[insert_idx + len(insert_marker):]
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Fixed app.js: Moved resizeImage function to top scope.")
else:
    print("Could not find insert marker.")
