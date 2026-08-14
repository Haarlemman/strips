import os
import json
from bs4 import BeautifulSoup

comics = []
item_id = 1
gallery_photos = []

# 1. Scan the images folder for all photos
image_folder = 'images'
if os.path.exists(image_folder):
    for root, _, files in os.walk(image_folder):
        for img in sorted(files):
            if img.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                rel_path = os.path.relpath(os.path.join(root, img), '.').replace('\\', '/')
                gallery_photos.append(rel_path)

# 2. Extract comic items from HTML sheets
files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']

for filename in sorted(files):
    series_fallback = filename.replace('.html', '')
    
    with open(filename, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        table = soup.find('table', class_='waffle')
        if not table:
            continue
            
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 12:
                continue
            
            def get_text(idx):
                if idx < len(cols):
                    a_tag = cols[idx].find('a')
                    return a_tag.text.strip() if a_tag else cols[idx].text.strip()
                return ""

            def get_link(idx):
                if idx < len(cols):
                    a_tag = cols[idx].find('a')
                    if a_tag and a_tag.has_attr('href'):
                        return a_tag['href']
                return ""

            def get_img(idx):
                if idx < len(cols):
                    img_tag = cols[idx].find('img')
                    if img_tag and img_tag.has_attr('src'):
                        return img_tag['src'].replace('\\', '/')
                return ""

            title = get_text(3)
            issue_nr = get_text(2)
            
            if not title or title.lower() in ["titel", "c", "title"] or issue_nr.lower() in ["nr", "b"]:
                continue

            series_name = get_text(4) or series_fallback
            author = get_text(6)
            link = get_link(8) or get_link(3)
            print_year = get_text(9)
            condition = get_text(10)
            price = get_text(11)
            img_src = get_img(1)

            comics.append({
                "id": item_id,
                "title": title,
                "series": series_name,
                "issue": issue_nr,
                "author": author,
                "print": print_year,
                "condition": condition,
                "price": price,
                "img": img_src,
                "link": link
            })
            item_id += 1

# 3. Output JavaScript file
with open('comics.js', 'w', encoding='utf-8') as out:
    out.write(f"const galleryPhotos = {json.dumps(gallery_photos, indent=2, ensure_ascii=False)};\n\n")
    out.write(f"const comics = {json.dumps(comics, indent=2, ensure_ascii=False)};\n")

print(f"Extraction complete! Found {len(gallery_photos)} showcase photos and {len(comics)} item rows.")