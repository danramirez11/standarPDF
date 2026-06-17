import fitz

SECTION_GAP = 40
ROW_THRESHOLD = 5
TABLE_MIN_ROWS = 3


def group_rows(elements):

    elements.sort(
        key=lambda e: (
            round(e["y"], 1),
            round(e["x"], 1)
        )
    )

    rows = []

    current_row = []

    current_y = None

    for element in elements:

        if current_y is None:
            current_y = element["y"]
            current_row.append(element)
            continue

        if abs(element["y"] - current_y) <= ROW_THRESHOLD:
            current_row.append(element)
        else:

            current_row.sort(
                key=lambda e: e["x"]
            )

            rows.append(current_row)

            current_row = [element]

            current_y = element["y"]

    if current_row:

        current_row.sort(
            key=lambda e: e["x"]
        )

        rows.append(current_row)

    return rows


def detect_table(rows):

    if len(rows) < TABLE_MIN_ROWS:
        return False

    column_counts = [
        len(row)
        for row in rows
    ]

    most_common = max(
        set(column_counts),
        key=column_counts.count
    )

    repeated = column_counts.count(
        most_common
    )

    return repeated >= 3 and most_common >= 2


def rows_to_table(rows):

    return [
        [
            cell["text"]
            for cell in row
        ]
        for row in rows
    ]


def rows_to_text(rows):

    lines = []

    for row in rows:

        line = " ".join(
            cell["text"]
            for cell in row
        )

        lines.append(line)

    return "\n".join(lines)


def extract_text(pdf_path: str):

    doc = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(doc):

        data = page.get_text("dict")

        elements = []

        for block in data["blocks"]:

            if block["type"] != 0:
                continue

            for line in block["lines"]:

                for span in line["spans"]:

                    text = span["text"].strip()

                    if not text:
                        continue

                    x0, y0, x1, y1 = span["bbox"]

                    elements.append({
                        "text": text,
                        "x": x0,
                        "y": y0
                    })

        elements.sort(
            key=lambda e: (
                round(e["y"], 1),
                round(e["x"], 1)
            )
        )

        sections = []

        current_section = []

        previous_y = None

        for element in elements:

            if previous_y is None:

                current_section.append(element)

                previous_y = element["y"]

                continue

            gap = element["y"] - previous_y

            if gap > SECTION_GAP:

                sections.append(
                    current_section
                )

                current_section = []

            current_section.append(element)

            previous_y = element["y"]

        if current_section:
            sections.append(
                current_section
            )

        structured_sections = []

        for section in sections:

            rows = group_rows(section)

            if detect_table(rows):

                structured_sections.append({
                    "type": "tableCandidate",
                    "rows": rows_to_table(rows)
                })

            else:

                structured_sections.append({
                    "type": "text",
                    "content": rows_to_text(rows)
                })

        pages.append({
            "page": page_number + 1,
            "sections": structured_sections
        })

    return pages