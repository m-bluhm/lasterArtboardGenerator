import svg
import os
from typing import Optional
import argparse
import cairosvg

# function to determine if a line of text has underhanging characters
def has_descenders(label_line: str) -> bool:
    descender_characters = {'g', 'j', 'p', 'q', 'y'}  # Set of characters with descenders
    return any(char in descender_characters for char in label_line)

def calculate_plaque_dimensions(fontSize: int, label_line1: str, label_line2: Optional[str] = None):
     # Determine the number of lines of text
    num_lines = 1 if label_line2 is None else 2

    # Estimate text width based on label length and font size
    max_label_length = max(len(label_line1), len(label_line2 or ""))
    text_width = max_label_length * (fontSize) * 0.55
    # Adjust multiplier as needed, 0.55 has worked well in my testing.

    # Estimate text height based on font size and number of lines
    text_height = fontSize * num_lines

    # Add padding around the text
    padding_x = fontSize * 0.1
    padding_y = fontSize * 0.1

    # calculate the width and height of the plaque. To change the width, modify the text_width multiplier
    plaque_width = text_width + 2 * padding_x
    plaque_height = text_height + 2 * padding_y

    return plaque_width, plaque_height


def create_svg_plaque(fontSize: int, label_line1: str, label_line2: Optional[str] = None) -> svg.SVG:
    """
        Create SVG corners.

        Parameters:
            fontSize (int): Font size.
            label_line1 (str): First line of the label.
            label_line2 (Optional[str]): Second line of the label (optional).

        Returns:
            svg.SVG: The generated SVG.
        """
    garamond_with_serifs = 'Garamond, serif'  # specifying Garamond font

    # Calculate corner radius for the arcs
    plaque_width, plaque_height = calculate_plaque_dimensions(fontSize, label_line1, label_line2)

    artboard_width = plaque_width * 1.05
    artboard_height = plaque_height * 1.05

    # Calculate plaque position to center it on the artboard
    plaque_x = (artboard_width - plaque_width) / 2
    plaque_y = (artboard_height - plaque_height) / 2

    
    corner_radius = plaque_height * 0.20

    # Define the paths for quarter-circle arcs in each corner
    arc_top_left = svg.Path(
        d=f"M {plaque_x} {plaque_y + corner_radius} A {corner_radius} {corner_radius} 0 0 0 {plaque_x + corner_radius} {plaque_y}",
        fill="none",
        stroke="red"
    )
    arc_top_right = svg.Path(
        d=f"M {plaque_x + plaque_width - corner_radius} {plaque_y} A {corner_radius} {corner_radius} 0 0 0 {plaque_x + plaque_width} {plaque_y + corner_radius}",
        fill="none",
        stroke="red"
    )
    arc_bottom_left = svg.Path(
        d=f"M {plaque_x + corner_radius} {plaque_y + plaque_height} A {corner_radius} {corner_radius} 0 0 0 {plaque_x} {plaque_y + plaque_height - corner_radius}",
        fill="none",
        stroke="red"
    )
    arc_bottom_right = svg.Path(
        d=f"M {plaque_x + plaque_width} {plaque_y + plaque_height - corner_radius} A {corner_radius} {corner_radius} 0 0 0 {plaque_x + plaque_width - corner_radius} {plaque_y + plaque_height}",
        fill="none",
        stroke="red"
    )


    # create the plaque rectangle
    #rectangle = svg.Rect(x=0, y=0, width=plaque_width, height=plaque_height, fill="none", stroke="red")
    rectangle = svg.Rect(x=plaque_x, y=plaque_y, width=plaque_width, height=plaque_height, fill="none", stroke="red")
    # the elements that will be included in the SVG drawing
    elements = [
        rectangle,
        arc_top_left,
        arc_top_right,
        arc_bottom_left,
        arc_bottom_right,
    ]

    # Add text elements as TSpan if label_line2 is provided-- meaning there are 2 lines of text in the plaque
    if label_line2:

        # if line 2 does not have underhanging characters, an offset of 0.45 looks better. If not 0.5
        # These values are based on what looks visually good in testing, and can be changed as needed
        y_offset = 0.45 if not has_descenders(label_line2) else 0.5
        
        text_element = svg.Text(x=plaque_x + (plaque_width / 2), y=plaque_y + 0.85*((plaque_height / 2) - (y_offset * fontSize)),
                                font_family=garamond_with_serifs, font_size=fontSize, text_anchor='middle',
                                dominant_baseline="middle", fill='blue',
                                elements=[svg.TSpan(x=plaque_x + (plaque_width / 2), dy=1.2, text=label_line1),
                                    svg.TSpan(x=plaque_x + (plaque_width / 2), dy=1 * fontSize,
                                              text=label_line2) if label_line2 else None
                                ])
        elements.append(text_element)

    else:
        # if there are underhanging characters, the label should be positioned slightly higher on the plaque
        # 0.05 * fontSize seems to work well for underhanging labels, 0.1 * fontSize for no underhanging characters
        y_offset = 0.05 if has_descenders(label_line1) else 0.1

        text_element = svg.Text(x=plaque_x + (plaque_width / 2), y=plaque_y + 0.85*((plaque_height / 2) + (y_offset * fontSize)),
                                text_anchor="middle", dominant_baseline="middle", fill='blue',
                                font_family=garamond_with_serifs, font_size=fontSize, text=label_line1)
        elements.append(text_element)

    return svg.SVG(
        width=artboard_width,
        height=artboard_height,
        elements=elements
    )


def write_svg_plaque(output_folder: str, file_name: str, fontSize: int, label_line1: str,
                     label_line2: Optional[str] = None) -> None:
    r"""
           Calls the function to generate the plaque SVG and saves the svg in the desired file path.

           Parameters:
               output_folder: The file path of the folder that the SVG should be saved in
                        NOTE: Python interprets backslashes as escape characters, so this needs to be an r-string
                        FOR EXAMPLE: r"C:\Users\defaultUser\Documents\Treeline\outputFiles\plaques"
                        notice the lowercase r in front of the file path
               file_name: The name of the file being saved. A "_plaque.svg" suffix/extension will be automatically added
               fontSize: The size of the font
               label_line1 (str): First line of the label.
               label_line2 (Optional[str]): Second line of the label (optional).
           """
    svg_file_path = os.path.join(output_folder, f"{file_name}_plaque.svg")
    png_file_path = os.path.splitext(svg_file_path)[0] + ".png" 
    with open(svg_file_path, 'w') as file:
        file.write(str(create_svg_plaque(fontSize, label_line1, label_line2)))

    plaque_width, plaque_height = calculate_plaque_dimensions(fontSize, label_line1, label_line2)
    artboard_width = plaque_width * 1.05
    artboard_height = plaque_height * 1.05
    # svg_width_inches = plaque_width / 25.4
    # svg_height_inches = plaque_height / 25.4
    # output_width = int(svg_width_inches * 96)
    # output_height = int(svg_height_inches * 96)
    # print("output_width: ", output_width)
    # print("Output_height: ", output_height, "\n")
    # Convert SVG to PNG using CairoSVG
    # cairosvg.svg2png(url=svg_file_path, write_to=png_file_path, dpi=96, output_width=(output_width * 2), output_height=(output_height*2))
    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path, dpi=96, output_width=artboard_width, output_height=artboard_height)      


test_output_folder = r"C:\Users\maxim\Documents\Treeline\outputFiles\plaques\png_conversion"

label1 = "Broken Mountain"
label1_underhang = "Goopy Pijen Rqual"
label2 = "Sisters, Kansas"

write_svg_plaque(test_output_folder, "2_lines_noUnderhang", 80, label1, label2)
write_svg_plaque(test_output_folder, "BrokenNoUnderhang", 80, label1)
write_svg_plaque(test_output_folder, "underhang", 80, label1_underhang)
write_svg_plaque(test_output_folder, "2_lines_underhang", 80, label1_underhang, label1_underhang)
write_svg_plaque(test_output_folder, "0.8_offset", 24, label1, label1_underhang)
write_svg_plaque(test_output_folder, "2_lines_underhang_topOnly", 80, label1_underhang, label1)