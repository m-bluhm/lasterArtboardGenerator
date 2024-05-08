import os
import svg
from typing import Optional
import cairosvg
import subprocess


def create_svg_corners_grid(rows: int, columns: int, width: float, height: float, x: float, y: float, fontSize: int,
                       text_anchor: str, dominant_baseline: str, lower_corner: bool,
                       label_line1: str, label_line2: Optional[str] = None) -> svg.SVG:
    """
    Create a SVG document with a label grid.

    Parameters:
        width (float): Width of a single artboard, in mm.
        height (float): Height of a single artboard, in mm.
        x (float): X-coordinate of the top-left corner of the grid.
        y (float): Y-coordinate of the top-left corner of the grid.
        fontSize (int): Font size.
        text_anchor (str): Specifies horizontal text alignment.
        dominant_baseline (str): Specifies vertical text alignment.
        lower_corner (bool): True if labels are in lower corners, False otherwise.
        label_line1 (str): First line of the label.
        label_line2 (Optional[str]): Second line of the label (optional).

    Returns:
        svg.SVG: The generated SVG.
    """
    colorArray = ['#0000FF','#0096FF','#00FFFF']
    garamond_with_serifs = 'Georgia'  # specifying Garamond font
    board_width = width * columns
    board_height = height * rows

    elements = []
    elements.append(svg.Rect(x=0, y=0, width=svg.mm(board_width), height=svg.mm(board_height), fill="white", stroke="red"))

    colorIndex = 0
    for column in range(columns):
        for row in range(rows):
            label_x = x + float(width) * float(column)  # Calculate X-coordinate of the label
            label_y = y + float(height) * float(row)    # Calculate Y-coordinate of the label
            print("label x:", label_x)
            print("label y: ", label_y,"\n")
            

            if lower_corner and label_line2:
            
                text_element=svg.Text(x=svg.mm(label_x), y=svg.mm(label_y), stroke= 'none', fill=colorArray[colorIndex], font_family=garamond_with_serifs, font_size=fontSize,
                            text_anchor=text_anchor, dominant_baseline=dominant_baseline, elements=[
                            svg.TSpan(x=svg.mm(label_x), dy=1.2, text=label_line2),
                            svg.TSpan(x=svg.mm(label_x), dy=-1.2 * fontSize, text=label_line1)
                        ])
            else:
                  text_element = svg.Text(x=svg.mm(label_x), y=svg.mm(label_y), stroke='none', fill=colorArray[colorIndex], font_family=garamond_with_serifs, font_size=fontSize,
                         text_anchor=text_anchor, dominant_baseline=dominant_baseline, elements=[
                        svg.TSpan(x=svg.mm(label_x), dy=1.2, text=label_line1),
                        svg.TSpan(x=svg.mm(label_x), dy=1.2 * fontSize, text=label_line2) if label_line2 else None
                    ])  
            colorIndex+=1      
            elements.append(text_element)


    return svg.SVG(
        width=svg.mm(board_width),
        height=svg.mm(board_height),
        elements=elements
    )

# TODO: Change parameter order

def writeSvg(output_folder: str, file_name: str, rows: int, columns: int, width: float, height: float,
             fontSize: int, label_line1: str, label_line2: Optional[str] = None, x_percent_from_edge: float = 0.12, 
             y_percent_from_edge: float = 0.12) -> None:

    
    """
    Calls the create_svg_corners_3x3 function to generate an SVG grid of labels.
    Saves the SVG document in the specified output folder and filename.

    Parameters:
        output_folder (str): The file path of the folder where the SVG should be saved.
        file_name (str): The name of the file to be saved.
        width (float): Width of a single artboard, in mm.
        height (float): Height of a single artboard, in mm.
        x_percent_from_edge (float): Distance from the horizontal edge of the document for label positioning.
        y_percent_from_edge (float): Distance from the vertical edge of the document for label positioning.
        fontSize (int): Font size.
        label_line1 (str): First line of the label.
        label_line2 (Optional[str]): Second line of the label (optional).
    """
    names = ["_topLeftGrid.svg", "_topRightGrid.svg", "_bottomLeftGrid.svg", "_bottomRightGrid.svg"]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    x_start = min(width, height) * x_percent_from_edge
    y_start = min(width, height) * y_percent_from_edge

    for i in range(4):
        test_file_name = file_name + names[i]
        svg_file_path = os.path.join(output_folder, test_file_name)
        pdf_file_path = os.path.splitext(svg_file_path)[0] + ".pdf"


        if i == 0:  # top-left
            svg_content = create_svg_corners_grid(rows, columns, width, height, x_start, y_start, fontSize,
                                             "start", "text-top", False, label_line1, label_line2)
        elif i == 1:  # top-right
            svg_content = create_svg_corners_grid(rows, columns, width, height, width - x_start, y_start, fontSize,
                                             "end", "text-top", False, label_line1, label_line2)
        elif i == 2:  # bottom-left
            svg_content = create_svg_corners_grid(rows, columns, width, height, x_start, height - y_start, fontSize,
                                             "start", "text-bottom", True, label_line1, label_line2)
        else:  # bottom-right
            svg_content = create_svg_corners_grid(rows, columns, width, height, width - x_start, height - y_start,
                                             fontSize, "end", "text-bottom", True, label_line1, label_line2)

        with open(svg_file_path, 'w') as svg_file:
            svg_file.write(str(svg_content))

        subprocess.run(["inkscape", svg_file_path, "--export-pdf=" + pdf_file_path, "--export-text-to-path"]) 


    
    


rows = 1
columns = 1
width = 139.7
height = 203.2
label1 = "Alabama"
text_size = 28

output_folder = os.path.join(r"C:\Users\maxim\Documents\Treeline\grid", label1)
writeSvg(output_folder, label1, rows, columns, width, height, text_size, label1)

"""for column in range(columns):
        for row in range(rows):
            label_x = x + float(width) * float(column)  # Calculate X-coordinate of the label
            label_y = y + float(height) * float(row)    # Calculate Y-coordinate of the label
            print("label x:", label_x)
            print("label y: ", label_y,"\n")
            

            # Adjust Y-coordinate for the second line of text
            if label_line2 and not lower_corner:
                 label_y += fontSize * 1.2

            text_element = svg.Text(x=svg.mm(label_x), y=svg.mm(label_y), fill='blue', stroke='none',
                                    font_family=garamond_with_serifs, font_size=fontSize,
                                    text_anchor=text_anchor, dominant_baseline=dominant_baseline, elements=[
                                        svg.TSpan(x=svg.mm(label_x), dy=fontSize * 1.0, text=label_line1),
                                        svg.TSpan(x=svg.mm(label_x), dy=fontSize * 1.2, text=label_line2)
                                        if label_line2 else None
                                    ])
            elements.append(text_element)"""