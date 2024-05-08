import os
import argparse
import svg
from typing import Optional, Tuple
import cairosvg
import svgwrite
import svgwrite.text
import subprocess


def create_svg_corners(width: float, height: float, x: float, y: float, fontSize: int,
                       text_anchor: str, dominant_baseline: str, lower_corner: bool,
                       label_line1: str, label_line2: Optional[str] = None) -> svg.SVG:
    """
    Create a svg document with a label in the corner

    Parameters:
        width (float): Width of the artboard, in mm.
        height (float): Height of the artboard, in mm.
        x (float): X-coordinate of the text box. Will be calculated automatically based on the size of the artboard.
        y (float): Y-coordinate of the text box. Will be calculated automatically based on the size of the artboard.
        fontSize (int): Font size.
        text_anchor (str): Specifies whether the text is left, center, or right-aligned.
            "start" as the parameter means left-aligned (the left edge of the text box will be at the x-coordinate).
            "middle" as the parameter means center-aligned (the middle of the text box will be at the x-coordinate).
            "end" as the parameter means right-aligned (the right edge of the text box will be at the x-coordinate).
        dominant_baseline (str): Specifies how the text is aligned vertically relative to the y coordinate.
            "text-bottom": Aligns the bottom of the text box with the y coordinate.
            "middle": Aligns the middle of the text box with the y coordinate.
            "text-top": Aligns the top of the text box with the y coordinate.
        lower_corner (bool): True if it's a lower corner, False otherwise.
        label_line1 (str): First line of the label.
        label_line2 (Optional[str]): Second line of the label (optional).

    Returns:
        svg.SVG: The generated SVG.
    """
    garamond_with_serifs = 'Georgia'  # specifying Garamond font

    # if the label is being written in a lower corner of the document and the label has 2 lines of text,
    # we want to base the positioning of the label off the second line of text
    if lower_corner and label_line2:
        fontSize = fontSize-2
        return svg.SVG(
            width=svg.mm(width),
            height=svg.mm(height),
            elements=[
                svg.Rect(x=0, y=0, width=svg.mm(width), height=svg.mm(height), fill="white", stroke="red"),
                svg.Text(x=svg.mm(x), y=svg.mm(y), stroke= 'none', fill='blue', font_family=garamond_with_serifs, font_size=fontSize,
                         text_anchor=text_anchor, dominant_baseline=dominant_baseline, elements=[
                        svg.TSpan(x=svg.mm(x), dy=1.2, text=label_line2),
                        svg.TSpan(x=svg.mm(x), dy=-1.2 * fontSize, text=label_line1)
                    ]),
            ]
        )

    else:
        if label_line2:
            fontSize = fontSize-2
        return svg.SVG(
            width=svg.mm(width),
            height=svg.mm(height),
            elements=[
                svg.Rect(x=0, y=0, width=svg.mm(width), height=svg.mm(height), fill="white", stroke="red"),
                svg.Text(x=svg.mm(x), y=svg.mm(y), stroke='none', fill='blue', font_family=garamond_with_serifs, font_size=fontSize,
                         text_anchor=text_anchor, dominant_baseline=dominant_baseline, elements=[
                        svg.TSpan(x=svg.mm(x), dy=1.2, text=label_line1),
                        svg.TSpan(x=svg.mm(x), dy=1.2 * fontSize, text=label_line2) if label_line2 else None
                    ]),
            ]
        )


def writeSvg(output_folder: str, file_name: str, width: float, height: float, x_percent_from_edge: float,
             y_percent_from_edge: float, fontSize: int, label_line1: str, label_line2: Optional[str] = None) -> None:
    r"""
        Calls the create SVG function 4 times to generate 4 documents, each having the label in a different corner.
        Saves these 4 SVG documents in the specified output folder and filename

        Parameters:
            output_folder: The file path of the folder that the SVG should be saved in
                        NOTE: Python interprets backslashes as escape characters, so this needs to be an r-string
                        FOR EXAMPLE: r"C:\Users\defaultUser\Documents\Treeline\outputFiles\plaques"
                        notice the lowercase r in front of the file path
            file_name: The name of the file to be saved. A suffix with a .svg extension and the specific corner
                will be automatically added
            width (float): Width of the artboard, in mm.
            height (float): Height of the artboard, in mm.
            x_percent_from_edge: For far away from the horizontal edge of the document the label should be
            y_percent_from_edge: For far away from the vertical edge of the document the label should be
            fontSize (int): Font size
            label_line1 (str): First line of the label.
            label_line2 (Optional[str]): Second line of the label (optional).
        """
    names = ["_topLeft.svg", "_topRight.svg", "_bottomLeft.svg", "_bottomRight.svg"]
    #names = ["_topLeftCentral.svg", "_topLeftHanging.svg", "_bottomLeftCentral.svg", "_bottomLeftHanging.svg"]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    #currently, both variables key off of width so that the label is the same distance away from the
        #horizontal and vertical edges. This can be changed if desired.
    x_edge_distance = min(width, height) * x_percent_from_edge
    y_edge_distance = min(width, height) * y_percent_from_edge

    for i in range(4):
        test_file_name = file_name + names[i]
        svg_file_path = os.path.join(output_folder, test_file_name)
        pdf_file_path = os.path.splitext(svg_file_path)[0] + ".pdf"

        if i == 0:  # top-left
            svg_content = create_svg_corners(width, height, x_edge_distance, y_edge_distance, fontSize,
                                             "start", "hanging", False, label_line1, label_line2)
        elif i == 1:  # top-right
            svg_content = create_svg_corners(width, height, width - x_edge_distance, y_edge_distance, fontSize,
                                              "end", "hanging", False, label_line1, label_line2)
        elif i == 2:  # bottom-left
            svg_content = create_svg_corners(width, height, x_edge_distance, height - y_edge_distance, fontSize,
                                             "start", "central", True, label_line1, label_line2)
        else:  # bottom-right
            svg_content = create_svg_corners(width, height, width - x_edge_distance, height - y_edge_distance,
                                              fontSize, "end", "central", True, label_line1, label_line2)

        with open(svg_file_path, 'w') as svg_file:
            svg_file.write(str(svg_content))
        
        cairosvg.svg2pdf(url=svg_file_path, write_to=pdf_file_path)   
        subprocess.run(["inkscape", pdf_file_path, "--export-pdf=" + pdf_file_path, "--export-text-to-path"]) 
        

# input_mapping = {
#     "0: 6x8_portrait": (139.7, 203.2, 0.12, 0.12, 28),
#     "1: 6x8_landscape": (203.2, 139.7, 0.12, 0.12, 28),
#     "2: 8x11_portrait": (203.2, 279.4, 0.12, 0.12, 34),
#     "3: x11_landscape": (279.4, 203.2, 0.12, 0.12, 34),
#     "4: 11x15_portrait": (279.4, 381, 0.10, 0.10, 40),
#     "5: 11x15_landscape": (381, 279.4, 0.10, 0.10, 40),
# }

input_mapping = {
    0: (139.7, 203.2, 0.12, 0.12, 28),
    1: (203.2, 139.7, 0.12, 0.12, 28),
    2: (203.2, 279.4, 0.12, 0.12, 34),
    3: (279.4, 203.2, 0.12, 0.12, 34),
    4: (279.4, 381, 0.10, 0.10, 40),
    5: (381, 279.4, 0.10, 0.10, 40),
}

def get_values_from_input() -> Tuple[float, float, float, float, int]:
    # Prompt the user to select a board size and orientation
    print("Please select board size and orientation or enter '6' for custom: \n")
    print(" 0: 6x8_portrait\n 1: 6x8_landscape\n 2: 8x11_portrait\n 3: 85x11_landscape\n 4: 11x15_portrait\n 5: 11x15_landscape\n 6: Custom\n")
    
    # Get user input
    user_input = int(input("Enter the number corresponding to your choice: "))
    
    if user_input == 6:
        # For custom input, prompt the user to enter custom values
        width = float(input("Enter map width (in mm): "))
        height = float(input("Enter map height (in mm): "))
        x_percent_from_edge = float(input("Enter x_percent_from_edge: "))
        y_percent_from_edge = float(input("Enter y_percent_from_edge: "))
        fontSize = int(input("Enter font size: "))
        return width, height, x_percent_from_edge, y_percent_from_edge, fontSize
    
    elif user_input in input_mapping:
        return input_mapping[user_input]
    else:
        raise ValueError("Invalid input. Please choose a number between 0 and 6.")

# Example usage:
values = get_values_from_input()
print(values)

def get_labels_from_input() -> Tuple[str, Optional[str]]:
    # Prompt the user to enter label 1
    label1 = input("Enter label 1: ")

    # Prompt the user to enter label 2 or '0' to skip
    label2_input = input("Enter label 2 or '0' to skip: ")
    label2 = label2_input if label2_input != '0' else None

    return label1, label2

# Example usage:
label1, label2 = get_labels_from_input()
print("Label 1:", label1)
print("Label 2:", label2)

if label2:
    output_folder = os.path.join(r"C:\Users\maxim\Documents\Treeline\PNG\inkscape", label1+label2)
    writeSvg(
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        output_folder, label1+label2, *values, label1, label2)
else:
    output_folder = os.path.join(r"C:\Users\maxim\Documents\Treeline\PNG\inkscape", label1)
    writeSvg(output_folder, label1, *values, label1)            


# test_output_folder = os.path.join(r"C:\Users\maxim\Documents\Treeline\PNG\inkscape", label1+label2)
# writeSvg(test_output_folder, label1+label2, w, h, 0.12, 0.12, text_size, label1, label2)  
# if __name__ == "__main__":
#     # Define the command-line arguments
#     parser = argparse.ArgumentParser(description='Generate SVG files with labels in different corners.')
#     parser.add_argument('output_folder', type=str, help='Output folder for saving SVG files')
#     parser.add_argument('file_name', type=str, help='Base name for the SVG files')
#     parser.add_argument('width', type=float, help='Width of the artboard in mm')
#     parser.add_argument('height', type=float, help='Height of the artboard in mm')
#     parser.add_argument('x_percent_from_edge', type=float, help='Distance from the horizontal edge of the document for label positioning')
#     parser.add_argument('y_percent_from_edge', type=float, help='Distance from the vertical edge of the document for label positioning')
#     parser.add_argument('fontSize', type=int, help='Font size')
#     parser.add_argument('label_line1', type=str, help='First line of the label')
#     parser.add_argument('--label_line2', type=str, default=None, help='Second line of the label (optional)')

#     # Parse the command-line arguments
#     args = parser.parse_args()

#     # Call the writeSvg function with the provided arguments
#     writeSvg(args.output_folder, args.file_name, args.width, args.height, args.x_percent_from_edge,
#              args.y_percent_from_edge, args.fontSize, args.label_line1, args.label_line2)