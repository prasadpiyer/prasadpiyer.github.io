#!/usr/bin/env python3
"""
Extract figures and captions from PDFs in files/papers/.
Saves PNGs under images/papers/<slug>/ and writes
_includes/carousels/<slug>-carousel.html snippets for Jekyll.
Requires: pip install pymupdf Pillow
"""
import fitz  # PyMuPDF
import re, os, json, pathlib, shutil

SRC_DIR = pathlib.Path("files/papers")
FIG_DIR = pathlib.Path("images/papers")
SNIPPET_DIR = pathlib.Path("_includes/carousels")
FIG_DIR.mkdir(parents=True, exist_ok=True)
SNIPPET_DIR.mkdir(parents=True, exist_ok=True)

# Utility to slugify PDF filenames (or titles) so that they match the
# Jekyll‐generated markdown slug style as closely as possible.
SLUG_PATTERN = re.compile(r"[^a-z0-9_-]")

def slugify(text: str) -> str:
    text = text.lower().replace(" ", "-").replace("_", "-")
    text = re.sub(r"-+", "-", text)  # collapse consecutive dashes
    return SLUG_PATTERN.sub("", text)

def clean(txt):
    return re.sub(r"\s+", " ", txt).strip()

def extract_pdf(pdf_path: pathlib.Path):
    # Derive a clean slug from the filename that is likely to match the
    # publication markdown filename (which uses the cleaned title).
    slug = slugify(pdf_path.stem)
    out_dir = FIG_DIR / slug
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    doc = fitz.open(pdf_path)
    fig_index = 1
    carousel_imgs = []

    for page in doc:
        # gather text blocks once per page
        text_blocks = page.get_text("blocks")
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
            except RuntimeError:
                continue

            # Ensure pixmap can be written as PNG (must be grayscale or RGB)
            try:
                save_ready = pix.colorspace and pix.colorspace.n == 3 and pix.alpha == 0
            except Exception:
                save_ready = False

            if not save_ready:
                try:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                except Exception:
                    # If conversion fails, skip this image
                    continue
            img_path = out_dir / f"fig-{fig_index}.png"
            pix.save(img_path.as_posix())

            caption = ""
            # compute image bottom coordinate if available (PDF points from top)
            img_bottom = None
            # Attempt to derive bottom y coordinate using full image info tuple.
            if len(img) >= 18 and all(isinstance(img[i], (int, float)) for i in (15, 17)):
                # y-offset + height
                img_bottom = img[15] + img[17]
            elif len(img) >= 8 and isinstance(img[7], (int, float)):
                img_bottom = img[7]

            if img_bottom is not None:
                for b in sorted(text_blocks, key=lambda b: b[1] if isinstance(b[1], (int, float)) else float('inf')):
                    # Compare y0 of text block to image bottom
                    if isinstance(b[1], (int, float)) and b[1] >= img_bottom:
                        candidate = clean(b[4])
                        if re.match(r"^(Figure|Fig\\.)", candidate, re.I):
                            caption = candidate
                            break
            # The carousel include expects paths relative to the images/
            # directory, since it prepends "/images/" itself. Therefore we
            # store only the sub-path under images/ here.
            rel_path = img_path.relative_to("images")
            carousel_imgs.append({"src": rel_path.as_posix(), "caption": caption})
            fig_index += 1

    # write snippet
    if carousel_imgs:
        snippet_file = SNIPPET_DIR / f"{slug}-carousel.html"
        with open(snippet_file, "w", encoding="utf-8") as fh:
            imgs = [item["src"] for item in carousel_imgs]
            imgs_str = "|".join(imgs)
            # First assign a variable that is an array via split, then reuse.
            fh.write('{% assign carousel_imgs = "' + imgs_str + '" | split: "|" %}\n')
            fh.write('{% include carousel.html id="' + slug + '" images=carousel_imgs %}\n')
            for item in carousel_imgs:
                if item["caption"]:
                    fh.write(f'<p class="fig-cap">{item["caption"]}</p>\n')
        print(f"{pdf_path.name}: extracted {len(carousel_imgs)} images")
    else:
        print(f"{pdf_path.name}: no images found")


def main():
    pdfs = list(SRC_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found in files/papers/")
        return
    for pdf in pdfs:
        extract_pdf(pdf)

if __name__ == "__main__":
    main() 