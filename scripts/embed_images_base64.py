#!/usr/bin/env python3
"""
Embed images as base64 data URIs in markdown posts.

This makes posts completely self-contained but increases file size significantly.

Usage:
    python embed_images_base64.py --file _posts/2025-11-06-ukraine.md --output _posts/2025-11-06-ukraine-embedded.md
    python embed_images_base64.py --file _posts/2025-11-06-ukraine.md --inline  # Replace in-place
"""

import argparse
import base64
import re
from pathlib import Path


def image_to_base64(image_path):
    """Convert image file to base64 data URI."""
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Detect image type
    if image_path.suffix.lower() == '.png':
        mime_type = 'image/png'
    elif image_path.suffix.lower() in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif image_path.suffix.lower() == '.gif':
        mime_type = 'image/gif'
    else:
        mime_type = 'image/png'  # Default

    b64_data = base64.b64encode(image_data).decode('utf-8')
    return f"data:{mime_type};base64,{b64_data}"


def embed_images_in_markdown(markdown_content, base_dir):
    """
    Replace image references with base64 data URIs.

    Matches patterns like:
    - ![Alt text](/path/to/image.png)
    - ![Alt text](../path/to/image.png)
    - ![Alt text](/eastbound/images/image.png)
    """

    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)

        # Skip external URLs
        if image_path.startswith('http://') or image_path.startswith('https://'):
            return match.group(0)  # Leave unchanged

        # Resolve relative paths
        if image_path.startswith('/eastbound/'):
            # Strip baseurl
            image_path = image_path.replace('/eastbound/', '')
        elif image_path.startswith('/'):
            image_path = image_path[1:]  # Strip leading /

        full_path = base_dir / image_path

        if not full_path.exists():
            print(f"[WARN] Image not found: {full_path}")
            return match.group(0)  # Leave unchanged

        try:
            data_uri = image_to_base64(full_path)
            print(f"[OK] Embedded: {image_path} ({full_path.stat().st_size // 1024} KB)")
            return f"![{alt_text}]({data_uri})"
        except Exception as e:
            print(f"[ERROR] Error embedding {image_path}: {e}")
            return match.group(0)  # Leave unchanged

    # Match markdown image syntax: ![alt](path)
    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, markdown_content)


def main():
    parser = argparse.ArgumentParser(description='Embed images as base64 in markdown')
    parser.add_argument('--file', required=True, help='Input markdown file')
    parser.add_argument('--output', help='Output file (default: adds -embedded suffix)')
    parser.add_argument('--inline', action='store_true', help='Replace file in-place')
    parser.add_argument('--base-dir', help='Base directory for resolving image paths (default: repo root)')

    args = parser.parse_args()

    input_file = Path(args.file)

    if not input_file.exists():
        print(f"[ERROR] File not found: {input_file}")
        return

    # Determine base directory (repo root)
    if args.base_dir:
        base_dir = Path(args.base_dir).resolve()
    else:
        # Find repo root by looking for .git directory
        current = input_file.resolve().parent
        while current != current.parent:
            if (current / '.git').exists():
                base_dir = current
                break
            current = current.parent
        else:
            # Fallback: assume parent of parent
            base_dir = input_file.parent.parent
            print(f"[WARN] Could not find .git directory, using fallback: {base_dir}")

    # Read markdown
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Embed images
    print(f"\nProcessing: {input_file}")
    print(f"Base directory: {base_dir}\n")

    embedded_content = embed_images_in_markdown(markdown_content, base_dir)

    # Determine output path
    if args.inline:
        output_file = input_file
    elif args.output:
        output_file = Path(args.output)
    else:
        output_file = input_file.parent / f"{input_file.stem}-embedded{input_file.suffix}"

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(embedded_content)

    # Calculate size difference
    original_size = input_file.stat().st_size
    new_size = output_file.stat().st_size
    size_increase = ((new_size - original_size) / original_size) * 100

    print(f"\n[SUCCESS] Embedded images written to: {output_file}")
    print(f"[SIZE] Original size: {original_size // 1024} KB")
    print(f"[SIZE] New size: {new_size // 1024} KB")
    print(f"[SIZE] Increase: +{size_increase:.1f}%")

    if size_increase > 500:
        print("\n[WARNING] File size increased significantly!")
        print("          Consider using external image references for production.")


if __name__ == '__main__':
    main()
