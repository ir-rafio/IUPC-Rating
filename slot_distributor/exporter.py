from pathlib import Path

import pandas as pd


def _column_letter(number: int) -> str:
    result = ""
    while number >= 0:
        result = chr(number % 26 + ord("A")) + result
        number = number // 26 - 1
    return result


def _format_sheet(workbook, worksheet, frame: pd.DataFrame) -> None:
    header = workbook.add_format({"bg_color": "#535FC1", "font_color": "white"})
    worksheet.set_row(0, None, header)
    if not frame.empty:
        cell_range = f"A2:{_column_letter(len(frame.columns) - 1)}{len(frame) + 1}"
        for formula, color in [("=ISEVEN(ROW())", "#C9DAF8"), ("=ISODD(ROW())", "#FFFFFF")]:
            worksheet.conditional_format(cell_range, {
                "type": "formula",
                "criteria": formula,
                "format": workbook.add_format({"bg_color": color}),
            })
    for index, column in enumerate(frame.columns):
        value_width = frame[column].map(lambda value: len(str(value))).max() if not frame.empty else 0
        worksheet.set_column(index, index, max(value_width, len(column)) + 2)


def generate_excel(
    ratings: pd.DataFrame,
    slots: pd.DataFrame,
    waiting_list: pd.DataFrame,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    slot_sheet = slots.rename(columns={"Slots": "General Slots"}).copy()
    slot_sheet["Reserved Slots"] = 0
    slot_sheet["Total Slots"] = ""
    slot_sheet["Explanation for Reserved Slots"] = ""

    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        workbook = writer.book
        for name, frame in [
            ("Slots", slot_sheet),
            ("Waiting List", waiting_list),
            ("Ratings", ratings),
        ]:
            frame.to_excel(writer, sheet_name=name, index=False, header=False, startrow=1)
            worksheet = writer.sheets[name]
            for column, heading in enumerate(frame.columns):
                worksheet.write(0, column, heading)
            _format_sheet(workbook, worksheet, frame)
            worksheet.protect()

        worksheet = writer.sheets["Slots"]
        general = slot_sheet.columns.get_loc("General Slots")
        reserved = slot_sheet.columns.get_loc("Reserved Slots")
        total = slot_sheet.columns.get_loc("Total Slots")
        explanation = slot_sheet.columns.get_loc("Explanation for Reserved Slots")
        unlocked = workbook.add_format({"locked": False})
        for row in range(len(slot_sheet)):
            excel_row = row + 2
            worksheet.write_formula(
                row + 1,
                total,
                f"={_column_letter(general)}{excel_row}+{_column_letter(reserved)}{excel_row}",
            )
            worksheet.write(row + 1, reserved, slot_sheet.iloc[row, reserved], unlocked)
            worksheet.write(row + 1, explanation, slot_sheet.iloc[row, explanation], unlocked)
