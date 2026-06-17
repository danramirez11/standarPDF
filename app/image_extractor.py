import fitz
import os


def extract_images(
    pdf_path: str,
    output_folder: str
):

    doc = fitz.open(pdf_path)


    images = []

    image_index = 1

    for page_index in range(len(doc)):

        page = doc[page_index]

        image_list = page.get_images(
            full=True
        )

        for image in image_list:

            xref = image[0]

            base_image = doc.extract_image(
                xref
            )

            image_bytes = base_image["image"]

            ext = base_image["ext"]

            filename = (
                f"image_{image_index}.{ext}"
            )

            filepath = os.path.join(
                output_folder,
                filename
            )

            with open(
                filepath,
                "wb"
            ) as f:

                f.write(image_bytes)

            images.append({
                "id": image_index,
                "filename": filename,
                "page": page_index + 1
            })

            image_index += 1


    return images