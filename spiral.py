from math import sqrt
from util import add_padding_to_layout

def layout_poster(valentine_data, W, H, margin=0, vertical_margin=0):
    """
    Lays out a poster with a title, Super Groups (SGs) containing Visual Groups (VGs),
    and Knowledge Groups (KGs) within VGs. VGs within an SG have widths proportional to their content areas.
    
    Args:
        valentine_data: Dictionary containing "data" with VGs, each having "knowledges".
        W: Poster width (float).
        H: Poster height (float).
        margin: Horizontal margin for KGs in VGs with multiple KGs (float, default=0).
        vertical_margin: Vertical spacing between KGs (float, default=0).
    
    Returns:
        Dictionary mapping element keys to their coordinates (as lists of [x, y] points).
        Now includes Text coordinates for each KG.
    """
    # Character width-to-height ratios
    def calculate_text_width(string, font_height):
        ratios = {
            'B': 0.5, 'E': 0.5, 'F': 0.5, 'J': 0.5, 'L': 0.5, 'P': 0.5, 'S': 0.5,
            'A': 0.8889, 'D': 0.8889, 'H': 0.8889, 'K': 0.8889, 'N': 0.8889,
            'R': 0.8889, 'T': 0.8889, 'U': 0.8889, 'V': 0.8889, 'X': 0.8889,
            'Y': 0.8889, 'Z': 0.8889, 'C': 1.0, 'G': 1.0, 'O': 1.0, 'Q': 1.0,
            'M': 1.1111, 'W': 1.1111, 'b': 0.5, 'd': 0.5, 'f': 0.5, 'h': 0.5,
            'k': 0.5, 'l': 0.5, 't': 0.5, 'c': 1.0, 'e': 1.0, 'o': 1.0, 's': 1.0,
            'a': 0.7, 'g': 0.7, 'n': 0.7, 'p': 0.7, 'q': 0.7, 'r': 0.7, 'u': 0.7,
            'v': 0.7, 'w': 0.7, 'x': 0.7, 'y': 0.7, 'z': 0.7, ' ': 0.4
        }
        return sum(ratios.get(char, 0.7) * font_height for char in string)

    # Helper function to calculate area of a rectangle
    def calculate_area(x1, y1, x2, y2):
        return (x2 - x1) * (y2 - y1)

    # Helper function to define SG structure based on number of VGs
    def get_sg_structure(n_VG):
        if n_VG == 1:
            return [[0]]
        elif n_VG == 2:
            return [[0], [1]]
        elif n_VG == 3:
            return [[0, 1], [2]]
        elif n_VG == 4:
            return [[0, 1], [2], [3]]
        elif n_VG == 5:
            return [[0, 1], [2, 3], [4]]
        elif n_VG == 6:
            return [[0, 1], [2, 3], [4], [5]]
        elif n_VG == 7:
            return [[0, 1], [2, 3], [4], [5, 6]]
        elif n_VG == 8:
            return [[0, 1], [2, 3], [4], [5, 6], [7]]
        elif n_VG == 9:
            return [[0, 1], [2, 3], [4], [5, 6], [7, 8]]
        elif n_VG == 10:
            return [[0, 1], [2, 3], [4], [5, 6], [7, 8, 9]]
        else:
            raise ValueError("Unsupported number of VGs (must be 1 to 10)")
        
    # Define VG reordering based on number of VGs
    reorder_map = {
        1: [0],
        2: [0, 1],
        3: [0, 1, 2],
        4: [0, 1, 2, 3],
        5: [0, 1, 3, 2, 4],
        6: [0, 1, 3, 2, 4, 5],
        7: [0, 1, 3, 2, 4, 5, 6],
        8: [0, 1, 3, 2, 4, 6, 5, 7],
        9: [0, 1, 3, 2, 4, 6, 5, 7, 8],
        10: [0, 1, 3, 2, 4, 6, 5, 7, 8, 9]
    }
    
    VGs = valentine_data["data"]
    n_VG = len(VGs)
    if n_VG not in reorder_map:
        raise ValueError("Unsupported number of VGs (must be 1 to 10)")
    new_order = reorder_map[n_VG]
    VGs = [VGs[i] for i in new_order]  # Reorder VGs according to the map
    sg_structure = get_sg_structure(n_VG)
    n_SG = len(sg_structure)

    # Calculate coefficients for the quadratic equation b * x^2 + a * x + c - H * W = 0
    a = 3.0 * W + 1.5 * n_SG * W  # Title (3x * W) + Subtitles (1.5x * W per VG)
    b = 0.0  # Area coefficient
    c = -H * W  # Target poster area

    # Compute b and vg_areas
    vg_areas = []
    for VG in VGs:
        knowledges = VG["knowledges"]
        sum_s_KG = 0.0
        for KG in knowledges:
            text = KG["knowledge_content"]
            highlight = KG["first_level_highlight"]
            n_images = (1 if KG["icon_keyword"] != "" else 0) + (1 if KG["visualization"]["is_visualization"] else 0)
            s_text = calculate_text_width(text, 1.0)
            s_highlight = calculate_text_width(highlight, 1.0)
            s_KG = s_text + 4 * s_highlight + s_text * n_images
            sum_s_KG += s_KG
            b += s_KG  # Add to total area coefficient
        vg_areas.append(sum_s_KG)

    # Add vertical margins to c
    for VG in VGs:
        n_KG = len(VG["knowledges"])
        if n_KG > 1:
            c += (n_KG - 1) * vertical_margin * W

    # Solve b * x^2 + a * x + c = 0
    discriminant = a**2 - 4 * b * c
    if discriminant < 0:
        raise ValueError("No solution for font size x")
    x = (-a + sqrt(discriminant)) / (2 * b) if b != 0 else -c / a
    if x <= 0:
        raise ValueError("Invalid font size x")

    # Layout the poster
    layout = {}
    layout["Title"] = [[0.0, 0.0], [W, 0.0], [0.0, 3.0 * x], [W, 3.0 * x]]
    y = 3.0 * x  # Start below title

    for sg in sg_structure:
        n_VG_in_SG = len(sg)
        total_area_in_sg = sum(vg_areas[i] for i in sg) if sg else 0.0
        vg_heights = []

        x_VG_start = 0.0
        for vg_idx in sg:
            VG = VGs[vg_idx]
            knowledges = VG["knowledges"]
            n_KG = len(knowledges)
            w_VG = W * (vg_areas[vg_idx] / total_area_in_sg) if total_area_in_sg > 0 else W
            kg_width = w_VG if n_KG == 1 else w_VG - 2 * margin
            kg_x = x_VG_start if n_KG == 1 else x_VG_start + margin

            VG_key = f"VG{vg_idx + 1}"
            layout[VG_key] = {}

            # Subtitle
            y_VG_start = y
            layout[VG_key]["Subtitle"] = [
                [x_VG_start, y], [x_VG_start + w_VG, y],
                [x_VG_start, y + 1.5 * x], [x_VG_start + w_VG, y + 1.5 * x]
            ]
            y_VG = y + 1.5 * x
            if n_KG > 1:
                y_VG += vertical_margin

            # Layout KGs within VG
            for j, KG in enumerate(knowledges, 1):
                text = KG["knowledge_content"]
                highlight = KG["first_level_highlight"]
                has_icon = KG["icon_keyword"] != ""
                has_vis = KG["visualization"]["is_visualization"]

                A_text = x * calculate_text_width(text, x)
                A_highlight = 2.0 * x * calculate_text_width(highlight, 2.0 * x)
                A_icon = x * calculate_text_width(text, x) if has_icon else 0.0
                A_vis = x * calculate_text_width(text, x) if has_vis else 0.0
                A_KG = A_text + A_highlight + A_icon + A_vis
                h_KG = A_KG / kg_width if kg_width > 0 else 0.0

                KG_key = f"KG{j}"
                layout[VG_key][KG_key] = {}
                layout[VG_key][KG_key]["coords"] = [
                    [kg_x, y_VG], [kg_x + kg_width, y_VG],
                    [kg_x, y_VG + h_KG], [kg_x + kg_width, y_VG + h_KG]
                ]

                y_KG = y_VG
                h_highlight = 2.0 * x
                w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                layout[VG_key][KG_key]["Highlight"] = [
                    [kg_x, y_KG], [kg_x + w_highlight, y_KG],
                    [kg_x, y_KG + h_highlight], [kg_x + w_highlight, y_KG + h_highlight]
                ]
                layout[VG_key][KG_key]["Icon"] = None
                layout[VG_key][KG_key]["Vis"] = None
                layout[VG_key][KG_key]["placement_type"] = "none"  # Initialize placement type

                # Image placement functions
                aspect_ratios = [1.0, 1.333, 0.75, 1.5, 0.667, 1.777, 0.562, 0.5, 2.0, 1.4, 0.714, 0.8, 1.25, 0.6, 1.667]

                def try_placement_a(r, A_img):
                    w_img = sqrt(A_img * r)
                    h_img = sqrt(A_img / r)
                    x1 = kg_x + kg_width - w_img
                    y1 = y_KG
                    x2 = kg_x + kg_width
                    y2 = y_KG + h_img
                    coords = [[x1, y1], [x2, y1], [x1, y2], [x2, y2]]
                    overflow_area = 0
                    if y2 > y_KG + h_KG:
                        overflow_area += (y2 - (y_KG + h_KG)) * w_img
                    if x1 < kg_x + w_highlight:
                        overlap_area = (min(x2, kg_x + w_highlight) - x1) * h_img if x2 > kg_x + w_highlight else w_img * h_img
                        overflow_area += overlap_area
                    return True if overflow_area == 0 else False, coords, overflow_area

                def try_placement_b(r, A_img):
                    w_img = sqrt(A_img * r)
                    h_img = sqrt(A_img / r)
                    x1 = kg_x
                    y1 = y_KG + h_highlight
                    x2 = kg_x + w_img
                    y2 = y_KG + h_highlight + h_img
                    coords = [[x1, y1], [x2, y1], [x1, y2], [x2, y2]]
                    overflow_area = 0
                    if y2 > y_KG + h_KG:
                        overflow_area += (y2 - (y_KG + h_KG)) * w_img
                    if x2 > kg_x + kg_width:
                        overflow_area += (x2 - (kg_x + kg_width)) * h_img
                    return True if overflow_area == 0 else False, coords, overflow_area

                def try_combination_1(r_a, r_b):
                    w_a = sqrt(A_icon * r_a)
                    h_a = sqrt(A_icon / r_a)
                    w_b = sqrt(A_vis * r_b)
                    h_b = sqrt(A_vis / r_b)
                    x1_a = kg_x + kg_width - w_a
                    y1_a = y_KG
                    x2_a = kg_x + kg_width
                    y2_a = y_KG + h_a
                    coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                    x1_b = kg_x + kg_width - w_a - w_b
                    y1_b = y_KG
                    x2_b = kg_x + kg_width - w_a
                    y2_b = y_KG + h_b
                    coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                    overflow_area = 0
                    if y2_a > y_KG + h_KG:
                        overflow_area += (y2_a - (y_KG + h_KG)) * w_a
                    if y2_b > y_KG + h_KG:
                        overflow_area += (y2_b - (y_KG + h_KG)) * w_b
                    if x1_a < kg_x + w_highlight and y1_a < y_KG + h_highlight:
                        overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, h_highlight) if x2_a > kg_x + w_highlight else w_a * min(h_a, h_highlight)
                        overflow_area += overlap_area
                    if x1_b < kg_x + w_highlight and y1_b < y_KG + h_highlight:
                        overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, h_highlight) if x2_b > kg_x + w_highlight else w_b * min(h_b, h_highlight)
                        overflow_area += overlap_area
                    return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

                def try_combination_2(r_a, r_b):
                    w_a = sqrt(A_icon * r_a)
                    h_a = sqrt(A_icon / r_a)
                    w_b = sqrt(A_vis * r_b)
                    h_b = sqrt(A_vis / r_b)
                    x1_a = kg_x + kg_width - w_a
                    y1_a = y_KG
                    x2_a = kg_x + kg_width
                    y2_a = y_KG + h_a
                    coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                    x1_b = kg_x
                    y1_b = y_KG + h_highlight
                    x2_b = kg_x + w_b
                    y2_b = y_KG + h_highlight + h_b
                    coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                    overflow_area = 0
                    if y2_a > y_KG + h_KG:
                        overflow_area += (y2_a - (y_KG + h_KG)) * w_a
                    if y2_b > y_KG + h_KG:
                        overflow_area += (y2_b - (y_KG + h_KG)) * w_b
                    if x1_a < kg_x + w_highlight and y1_a < y_KG + h_highlight:
                        overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, h_highlight) if x2_a > kg_x + w_highlight else w_a * min(h_a, h_highlight)
                        overflow_area += overlap_area
                    if x2_b > kg_x + kg_width:
                        overflow_area += (x2_b - (kg_x + kg_width)) * h_b
                    # Visualization's top-right corner overlaps Icon's bottom-left corner
                    if x2_b > x1_a and y1_b < y2_a:
                        overlap_width = min(x2_b, x2_a) - x1_a  # Width of overlap (limited by Icon's right edge)
                        overlap_height = min(y2_a, y2_b) - y1_b  # Height of overlap (limited by Visualization's bottom)
                        overlap_area = overlap_width * overlap_height
                        overflow_area += overlap_area
                    return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

                def try_combination_3(r_a, r_b):
                    w_a = sqrt(A_icon * r_a)
                    h_a = sqrt(A_icon / r_a)
                    w_b = sqrt(A_vis * r_b)
                    h_b = sqrt(A_vis / r_b)
                    x1_a = kg_x + kg_width - w_a
                    y1_a = y_KG
                    x2_a = kg_x + kg_width
                    y2_a = y_KG + h_a
                    coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                    x1_b = kg_x + kg_width - w_b
                    y1_b = y_KG + h_a
                    x2_b = kg_x + kg_width
                    y2_b = y_KG + h_a + h_b
                    coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                    overflow_area = 0
                    if y2_a > y_KG + h_KG:
                        overflow_area += (y2_a - (y_KG + h_KG)) * w_a
                    if y2_b > y_KG + h_KG:
                        overflow_area += (y2_b - (y_KG + h_KG)) * w_b
                    if x1_a < kg_x + w_highlight and y1_a < y_KG + h_highlight:
                        overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, h_highlight) if x2_a > kg_x + w_highlight else w_a * min(h_a, h_highlight)
                        overflow_area += overlap_area
                    if x1_b < kg_x + w_highlight and y1_b < y_KG + h_highlight:
                        overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, h_highlight - (y1_b - y_KG)) if x2_b > kg_x + w_highlight else w_b * min(h_b, h_highlight - (y1_b - y_KG))
                        overflow_area += overlap_area
                    return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

                def try_combination_4(r_a, r_b):
                    w_a = sqrt(A_icon * r_a)
                    h_a = sqrt(A_icon / r_a)
                    w_b = sqrt(A_vis * r_b)
                    h_b = sqrt(A_vis / r_b)
                    x1_a = kg_x
                    y1_a = y_KG + h_highlight
                    x2_a = kg_x + w_a
                    y2_a = y_KG + h_highlight + h_a
                    coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                    x1_b = kg_x + kg_width - w_b
                    y1_b = y_KG + h_KG - h_b
                    x2_b = kg_x + kg_width
                    y2_b = y_KG + h_KG
                    coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                    overflow_area = 0
                    if y2_a > y_KG + h_KG:
                        overflow_area += (y2_a - (y_KG + h_KG)) * w_a
                    if x2_a > kg_x + kg_width:
                        overflow_area += (x2_a - (kg_x + kg_width)) * h_a
                    if y2_b > y_KG + h_KG:
                        overflow_area += (y2_b - (y_KG + h_KG)) * w_b
                    if x1_b < kg_x + w_highlight and y1_b < y_KG + h_highlight:
                        overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, h_highlight - (y1_b - y_KG)) if x2_b > kg_x + w_highlight else w_b * min(h_b, h_highlight - (y1_b - y_KG))
                        overflow_area += overlap_area
                    return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

                # Image placement logic with placement type assignment
                if has_icon and has_vis:
                    min_overflow = float('inf')
                    best_layout = None
                    combination_funcs = [try_combination_1, try_combination_2, try_combination_3, try_combination_4]
                    for idx, comb in enumerate(combination_funcs):
                        for r_a in aspect_ratios:
                            for r_b in aspect_ratios:
                                fit, coords_a, coords_b, overflow = comb(r_a, r_b)
                                if fit:
                                    layout[VG_key][KG_key]["Icon"] = coords_a
                                    layout[VG_key][KG_key]["Vis"] = coords_b
                                    layout[VG_key][KG_key]["placement_type"] = f"comb{idx + 1}"
                                    min_overflow = 0
                                    break
                                if overflow < min_overflow:
                                    min_overflow = overflow
                                    best_layout = (coords_a, coords_b, r_a, r_b, idx)
                            if min_overflow == 0:
                                break
                        if min_overflow == 0:
                            break
                    if min_overflow > 0:
                        coords_a, coords_b, r_a, r_b, comb_idx = best_layout
                        w_a = sqrt(A_icon * r_a)
                        h_a = sqrt(A_icon / r_a)
                        x1_a, y1_a = coords_a[0]
                        x2_a, y2_a = coords_a[3]
                        w_b = sqrt(A_vis * r_b)
                        h_b = sqrt(A_vis / r_b)
                        x1_b, y1_b = coords_b[0]
                        x2_b, y2_b = coords_b[3]
                        if comb_idx == 0:
                            if x1_a < kg_x + w_highlight:
                                w_a = kg_width - (kg_x + w_highlight - x1_a)
                            if y2_a > y_KG + h_KG:
                                h_a = h_KG - (y1_a - y_KG)
                            w_a_new = min(w_a, h_a * r_a)
                            h_a_new = w_a_new / r_a
                            coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                            if x1_b < kg_x + w_highlight:
                                w_b = kg_width - (kg_x + w_highlight - x1_b)
                            if y2_b > y_KG + h_KG:
                                h_b = h_KG - (y1_b - y_KG)
                            w_b_new = min(w_b, h_b * r_b)
                            h_b_new = w_b_new / r_b
                            coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                        elif comb_idx == 1:  # Combination 2
                            # Resize Icon (A), anchored at top-right
                            if x1_a < kg_x + w_highlight:
                                w_a = kg_width - (kg_x + w_highlight - x1_a)  # Max width from Highlight's right edge
                            if y2_a > y_KG + h_KG:
                                h_a = h_KG - (y1_a - y_KG)  # Max height within KG
                            w_a_new = min(w_a, h_a * r_a)  # Preserve aspect ratio
                            h_a_new = w_a_new / r_a
                            # Anchor at top-right (x2_a = kg_x + kg_width, y1_a = y_KG)
                            x2_a_new = kg_x + kg_width
                            x1_a_new = x2_a_new - w_a_new  # Adjust left edge based on new width
                            coords_a = [
                                [x1_a_new, y1_a], [x2_a_new, y1_a],
                                [x1_a_new, y1_a + h_a_new], [x2_a_new, y1_a + h_a_new]
                            ]
                            # Resize Visualization (B), then check overlap with resized Icon
                            if x2_b > kg_x + kg_width:
                                w_b = kg_width - (x1_b - kg_x)  # Max width within KG
                            if y2_b > y_KG + h_KG:
                                h_b = h_KG - (y1_b - y_KG)  # Max height within KG
                            # Apply aspect ratio constraint first
                            w_b_new = min(w_b, h_b * r_b)
                            h_b_new = w_b_new / r_b
                            # Compute tentative right edge of B after initial resizing
                            x2_b_tentative = x1_b + w_b_new
                            # Check if Visualization's top-right corner overlaps Icon's bottom-left corner
                            if x2_b_tentative > x1_a_new and y1_b < y1_a + h_a_new:
                                w_b_new = min(w_b_new, x1_a_new - x1_b)  # Limit width so x2_b does not exceed x1_a_new
                                h_b_new = w_b_new / r_b  # Recalculate height to maintain aspect ratio
                            coords_b = [
                                [x1_b, y1_b], [x1_b + w_b_new, y1_b],
                                [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]
                            ]
                        elif comb_idx == 2:
                            if x1_a < kg_x + w_highlight:
                                w_a = kg_width - (kg_x + w_highlight - x1_a)
                            if y2_a > y_KG + h_KG:
                                h_a = h_KG - (y1_a - y_KG)
                            w_a_new = min(w_a, h_a * r_a)
                            h_a_new = w_a_new / r_a
                            coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                            if x1_b < kg_x + w_highlight:
                                w_b = kg_width - (kg_x + w_highlight - x1_b)
                            if y2_b > y_KG + h_KG:
                                h_b = h_KG - (y1_b - y_KG)
                            w_b_new = min(w_b, h_b * r_b)
                            h_b_new = w_b_new / r_b
                            coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                        elif comb_idx == 3:
                            if x2_a > kg_x + kg_width:
                                w_a = kg_width - (x1_a - kg_x)
                            if y2_a > y_KG + h_KG:
                                h_a = h_KG - (y1_a - y_KG)
                            w_a_new = min(w_a, h_a * r_a)
                            h_a_new = w_a_new / r_a
                            coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                            if x1_b < kg_x + w_highlight and y1_b < y_KG + h_highlight:
                                ratio_x = (kg_width - w_highlight) / w_b
                                ratio_y = (h_KG - h_highlight) / h_b
                                scale = max(ratio_x, ratio_y)
                                w_b_new = w_b * scale
                                h_b_new = h_b * scale
                            else:
                                w_b_new = w_b
                                h_b_new = h_b
                            x1_b_new = x2_b - w_b_new
                            y1_b_new = y2_b - h_b_new
                            coords_b = [[x1_b_new, y1_b_new], [x2_b, y1_b_new], [x1_b_new, y2_b], [x2_b, y2_b]]
                        layout[VG_key][KG_key]["Icon"] = coords_a
                        layout[VG_key][KG_key]["Vis"] = coords_b
                        layout[VG_key][KG_key]["placement_type"] = f"comb{comb_idx + 1}"

                elif has_icon:
                    min_overflow = float('inf')
                    best_layout = None
                    placement_funcs = [try_placement_a, try_placement_b]
                    for idx, placement in enumerate(placement_funcs):
                        for r in aspect_ratios:
                            fit, coords, overflow = placement(r, A_icon)
                            if fit:
                                layout[VG_key][KG_key]["Icon"] = coords
                                layout[VG_key][KG_key]["placement_type"] = 'a' if idx == 0 else 'b'
                                min_overflow = 0
                                break
                            if overflow < min_overflow:
                                min_overflow = overflow
                                best_layout = (coords, r, idx)
                        if min_overflow == 0:
                            break
                    if min_overflow > 0:
                        coords, r, placement_idx = best_layout
                        w_img = sqrt(A_icon * r)
                        h_img = sqrt(A_icon / r)
                        x1, y1 = coords[0]
                        x2, y2 = coords[3]
                        if placement_idx == 0:
                            if x1 < kg_x + w_highlight:
                                w_img = kg_width - w_highlight
                            if y2 > y_KG + h_KG:
                                h_img = h_KG - (y1 - y_KG)
                            w_img_new = min(w_img, h_img * r)
                            h_img_new = w_img_new / r
                            layout[VG_key][KG_key]["Icon"] = [
                                    [x2 - w_img_new, y1],  # New top-left
                                    [x2, y1],              # New top-right
                                    [x2 - w_img_new, y1 + h_img_new],              # New bottom-left
                                    [x2, y1 + h_img_new]                           # Bottom-right (fixed)
                                ]
                        elif placement_idx == 1:
                            if x2 > kg_x + kg_width:
                                w_img = kg_width - (x1 - kg_x)
                            if y2 > y_KG + h_KG:
                                h_img = h_KG - (y1 - y_KG)
                            w_img_new = min(w_img, h_img * r)
                            h_img_new = w_img_new / r
                            layout[VG_key][KG_key]["Icon"] = [
                                [x1, y1], [x1 + w_img_new, y1],
                                [x1, y1 + h_img_new], [x1 + w_img_new, y1 + h_img_new]
                            ]
                        layout[VG_key][KG_key]["placement_type"] = 'a' if placement_idx == 0 else 'b'

                elif has_vis:
                    min_overflow = float('inf')
                    best_layout = None
                    placement_funcs = [try_placement_a, try_placement_b]
                    for idx, placement in enumerate(placement_funcs):
                        for r in aspect_ratios:
                            fit, coords, overflow = placement(r, A_vis)
                            if fit:
                                layout[VG_key][KG_key]["Vis"] = coords
                                layout[VG_key][KG_key]["placement_type"] = 'a' if idx == 0 else 'b'
                                min_overflow = 0
                                break
                            if overflow < min_overflow:
                                min_overflow = overflow
                                best_layout = (coords, r, idx)
                        if min_overflow == 0:
                            break
                    if min_overflow > 0:
                        coords, r, placement_idx = best_layout
                        w_img = sqrt(A_vis * r)
                        h_img = sqrt(A_vis / r)
                        x1, y1 = coords[0]
                        x2, y2 = coords[3]
                        if placement_idx == 0:
                            if x1 < kg_x + w_highlight:
                                w_img = kg_width - w_highlight
                            if y2 > y_KG + h_KG:
                                h_img = h_KG - (y1 - y_KG)
                            w_img_new = min(w_img, h_img * r)
                            h_img_new = w_img_new / r
                            layout[VG_key][KG_key]["Vis"] = [
                                    [x2 - w_img_new, y1],  # New top-left
                                    [x2, y1],              # New top-right
                                    [x2 - w_img_new, y1 + h_img_new],              # New bottom-left
                                    [x2, y1 + h_img_new]                           # Bottom-right (fixed)
                                ]
                        elif placement_idx == 1:
                            if x2 > kg_x + kg_width:
                                w_img = kg_width - (x1 - kg_x)
                            if y2 > y_KG + h_KG:
                                h_img = h_KG - (y1 - y_KG)
                            w_img_new = min(w_img, h_img * r)
                            h_img_new = w_img_new / r
                            layout[VG_key][KG_key]["Vis"] = [
                                [x1, y1], [x1 + w_img_new, y1],
                                [x1, y1 + h_img_new], [x1 + w_img_new, y1 + h_img_new]
                            ]
                        layout[VG_key][KG_key]["placement_type"] = 'a' if placement_idx == 0 else 'b'

                # Calculate Text block coordinates based on placement type
                kg_coords = layout[VG_key][KG_key]["coords"]
                highlight_coords = layout[VG_key][KG_key]["Highlight"]
                icon_coords = layout[VG_key][KG_key]["Icon"]
                vis_coords = layout[VG_key][KG_key]["Vis"]
                placement_type = layout[VG_key][KG_key]["placement_type"]

                x1_KG, y1_KG = kg_coords[0]
                x2_KG, y2_KG = kg_coords[3]
                x1_highlight, y1_highlight = highlight_coords[0]
                x2_highlight, y2_highlight = highlight_coords[3]

                possible_blocks = []

                if placement_type == 'a':
                    if icon_coords:
                        x1_img, y1_img = icon_coords[0]
                        x2_img, y2_img = icon_coords[3]
                    elif vis_coords:
                        x1_img, y1_img = vis_coords[0]
                        x2_img, y2_img = vis_coords[3]
                    if y2_highlight < y2_img:
                        possible_blocks = [
                            [(x1_KG, y2_img), (x2_KG, y2_KG)],
                            [(x1_KG, y2_highlight), (x1_img, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_img, y2_KG)]
                        ]
                    else:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y2_img), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_img, y2_KG)]
                        ]
                elif placement_type == 'b':
                    if icon_coords:
                        x1_img, y1_img = icon_coords[0]
                        x2_img, y2_img = icon_coords[3]
                    elif vis_coords:
                        x1_img, y1_img = vis_coords[0]
                        x2_img, y2_img = vis_coords[3]
                    if x2_highlight < x2_img:
                        possible_blocks = [
                            [(x2_highlight, y1_KG), (x2_KG, y2_highlight)],
                            [(x2_img, y1_KG), (x2_KG, y2_KG)],
                            [(x1_KG, y2_img), (x2_KG, y2_KG)]
                        ]
                    else:
                        possible_blocks = [
                            [(x2_highlight, y1_KG), (x2_KG, y2_KG)],
                            [(x2_img, y2_highlight), (x2_KG, y2_KG)],
                            [(x1_KG, y2_img), (x2_KG, y2_KG)]
                        ]
                elif placement_type == 'comb1':
                    x1_a, y1_a = icon_coords[0]
                    x2_a, y2_a = icon_coords[3]
                    x1_b, y1_b = vis_coords[0]
                    x2_b, y2_b = vis_coords[3]
                    if y2_highlight <= y2_b <= y2_a:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x1_a, y2_KG)],
                            [(x1_KG, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif y2_highlight <= y2_a <= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_b, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif y2_b <= y2_highlight <= y2_a:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_a, y2_KG)],
                            [(x1_KG, y2_a), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_highlight, y2_b), (x1_a, y2_KG)]
                        ]
                    elif y2_b <= y2_a <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_highlight, y2_b), (x1_a, y2_KG)],
                            [(x2_highlight, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif y2_a <= y2_highlight <= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x1_a, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif y2_a <= y2_b <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_highlight, y2_b), (x2_KG, y2_KG)],
                            [(x1_a, y2_a), (x2_KG, y2_KG)]
                        ]
                elif placement_type == 'comb2':
                    x1_a, y1_a = icon_coords[0]
                    x2_a, y2_a = icon_coords[3]
                    x1_b, y1_b = vis_coords[0]
                    x2_b, y2_b = vis_coords[3]
                    if x2_highlight > x2_b and y2_a <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_b, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                            [(x2_highlight, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif x2_highlight > x2_b and y2_highlight <= y2_a <= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_b, y2_highlight), (x1_a, y2_KG)],
                            [(x2_b, y2_a), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_KG)]
                        ]
                    elif x2_highlight > x2_b and y2_a >= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_b), (x1_a, y2_KG)],
                            [(x1_KG, y2_a), (x2_KG, y2_KG)],
                            [(x2_b, y2_highlight), (x1_a, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_KG)]
                        ]
                    elif x2_highlight <= x2_b and y2_a <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y1_b)],
                            [(x2_b, y1_KG), (x1_a, y2_KG)] if x2_b < x1_a else [],
                            [(x2_b, y2_a), (x2_KG, y2_KG)]
                        ]
                        possible_blocks = [b for b in possible_blocks if b]  # Remove empty lists
                    elif x2_highlight <= x2_b and y2_highlight <= y2_a <= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y1_b)],
                            [(x2_b, y1_KG), (x1_a, y2_KG)],
                            [(x2_b, y2_a), (x2_KG, y2_KG)]
                        ]
                    elif x2_highlight <= x2_b and y2_a >= y2_b:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x2_KG, y2_KG)],
                            [(x1_KG, y2_b), (x1_a, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y1_b)],
                            [(x2_b, y1_KG), (x1_a, y2_KG)]
                        ]
                elif placement_type == 'comb3':
                    x1_a, y1_a = icon_coords[0]
                    x2_a, y2_a = icon_coords[3]
                    x1_b, y1_b = vis_coords[0]
                    x2_b, y2_b = vis_coords[3]
                    if y2_highlight > y2_a and y2_b < y2_highlight and x1_a > x1_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_a)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_highlight, y2_b), (x2_KG, y2_KG)]
                        ]
                    elif y2_highlight > y2_a and y2_b >= y2_highlight and x1_a > x1_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_a)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)]
                        ]
                    elif y2_highlight > y2_a and y2_b < y2_highlight and x1_a <= x1_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                            [(x2_highlight, y2_a), (x1_b, y2_KG)],
                            [(x2_highlight, y2_b), (x2_KG, y2_KG)]
                        ]
                    elif y2_highlight > y2_a and y2_b >= y2_highlight and x1_a <= x1_b:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                            [(x2_highlight, y2_a), (x1_b, y2_KG)]
                        ]
                    elif y2_highlight <= y2_a and x1_b >= x1_a:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_a, y2_KG)],
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_a, y2_KG)]
                        ]
                    elif y2_highlight <= y2_a and x1_b <= x2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_a, y2_a)],
                            [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_a)]
                        ]
                    elif y2_highlight <= y2_a and x2_highlight <= x1_b <= x1_a:
                        possible_blocks = [
                            [(x1_KG, y2_highlight), (x1_a, y2_a)],
                            [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                            [(x1_KG, y2_b), (x2_KG, y2_KG)],
                            [(x2_highlight, y1_KG), (x1_a, y2_a)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)]
                        ]
                elif placement_type == 'comb4':
                    x1_a, y1_a = icon_coords[0]
                    x2_a, y2_a = icon_coords[3]
                    x1_b, y1_b = vis_coords[0]
                    x2_b, y2_b = vis_coords[3]
                    if x2_a < x2_highlight and y1_b <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)]
                        ]
                    elif x2_a < x2_highlight and y2_highlight <= y1_b <= y2_a and x1_b > x2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x2_KG, y1_b)]
                        ]
                    elif x2_a < x2_highlight and y2_highlight <= y1_b <= y2_a and x1_b <= x2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)]
                        ]
                    elif x2_a < x2_highlight and y1_b >= y2_a and x1_b >= x2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x2_KG, y1_b)],
                            [(x1_KG, y2_a), (x2_KG, y1_b)]
                        ]
                    elif x2_a < x2_highlight and y1_b >= y2_a and x2_a <= x1_b <= x2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_a, y1_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_a, y1_a), (x2_KG, y1_b)],
                            [(x1_KG, y2_a), (x2_KG, y1_b)]
                        ]
                    elif x2_a < x2_highlight and y1_b >= y2_a and x1_b <= x2_a:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_a, y1_a), (x2_KG, y1_b)],
                            [(x1_KG, y2_a), (x2_KG, y1_b)]
                        ]
                    elif x2_a >= x2_highlight and y1_b <= y2_highlight:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x1_b, y1_a)],
                            [(x2_a, y1_KG), (x1_b, y2_KG)]
                        ]
                    elif x2_a >= x2_highlight and y2_highlight <= y1_b <= y2_a:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x2_highlight, y1_KG), (x2_KG, y2_a)],
                            [(x2_a, y1_KG), (x1_b, y2_KG)],
                            [(x2_a, y1_KG), (x2_KG, y1_b)]
                        ]
                    elif x2_a >= x2_highlight and y1_b >= y2_a and x1_b > x2_a:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x1_KG, y2_a), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x2_KG, y2_a)],
                            [(x2_a, y1_KG), (x1_b, y2_KG)],
                            [(x2_a, y1_KG), (x2_KG, y1_b)]
                        ]
                    elif x2_a >= x2_highlight and y1_b >= y2_a and x1_b <= x2_a:
                        possible_blocks = [
                            [(x1_KG, y2_a), (x1_b, y2_KG)],
                            [(x1_KG, y2_a), (x2_KG, y1_b)],
                            [(x2_highlight, y1_KG), (x2_KG, y2_a)],
                            [(x2_a, y1_KG), (x2_KG, y1_b)]
                        ]
                else:  # No placement (no Icon or Vis)
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                        [(x2_highlight, y1_KG), (x2_KG, y2_KG)]
                    ]

                # Find the block with maximum area
                max_area = -1
                best_block = None
                for (x1, y1), (x2, y2) in possible_blocks:
                    x1 = max(x1_KG, min(x2_KG, x1))
                    x2 = max(x1_KG, min(x2_KG, x2))
                    y1 = max(y1_KG, min(y2_KG, y1))
                    y2 = max(y1_KG, min(y2_KG, y2))
                    if x1 < x2 and y1 < y2:
                        area = calculate_area(x1, y1, x2, y2)
                        if area > max_area:
                            max_area = area
                            best_block = (x1, y1, x2, y2)

                if best_block:
                    x1, y1, x2, y2 = best_block
                    layout[VG_key][KG_key]["Text"] = [
                        [x1, y1], [x2, y1],
                        [x1, y2], [x2, y2]
                    ]
                else:
                    layout[VG_key][KG_key]["Text"] = None

                y_VG += h_KG
                if j < n_KG:
                    y_VG += vertical_margin

            h_VG = y_VG - y_VG_start
            vg_heights.append(h_VG)
            x_VG_start += w_VG

        h_SG = max(vg_heights) if vg_heights else 0.0
        x_VG_start = 0.0
        for vg_idx in sg:
            VG_key = f"VG{vg_idx + 1}"
            w_VG = W * (vg_areas[vg_idx] / total_area_in_sg) if total_area_in_sg > 0 else W
            layout[VG_key]["coords"] = [
                [x_VG_start, y], [x_VG_start + w_VG, y],
                [x_VG_start, y + h_SG], [x_VG_start + w_VG, y + h_SG]
            ]
            x_VG_start += w_VG

        y += h_SG

    # Create new layout with original VG indices
    new_layout = {"Title": layout["Title"]}
    original_order = reorder_map[n_VG]  # Get the new order (same as reorder map here)
    inverse_order = [original_order.index(i) for i in range(n_VG)]  # Compute inverse mapping
    for i, orig_idx in enumerate(inverse_order):
        new_key = f"VG{orig_idx + 1}"
        old_key = f"VG{i + 1}"
        if new_key in layout:
            new_layout[old_key] = layout[new_key]

    
    # Resize specific VGs based on n_VG
    if n_VG == 4:
        vgs_to_resize = [("VG3", True, 'both')]
    elif n_VG == 5:
        vgs_to_resize = [("VG4", True, 'both')]
    elif n_VG in [6, 7]:
        vgs_to_resize = [("VG4", True, 'both'), ("VG5", False, 'horizontal')]
    elif n_VG in [8, 9, 10]:
        vgs_to_resize = [("VG4", True, 'both'), ("VG5", False, 'horizontal'), ("VG7", True, 'both')]
    else:
        vgs_to_resize = []

    min_HW = min(H, W)
    for VG_key, use_left, direction in vgs_to_resize:
        if VG_key in new_layout:
            coords = new_layout[VG_key]["coords"]
            x_coords = [p[0] for p in coords]
            y_coords = [p[1] for p in coords]
            x_left = min(x_coords)
            x_right = max(x_coords)
            y_top = min(y_coords)
            y_bottom = max(y_coords)
            old_width = x_right - x_left
            old_height = y_bottom - y_top
            
            # Determine reference point
            ref_x = x_left if use_left else x_right
            ref_y = (y_top + y_bottom) / 2
            
            # New dimensions
            alpha = 0.08
            new_width = alpha/2 * min_HW
            new_height = alpha * min_HW
            sx = 1 - new_width / old_width if old_width > 0 and direction in ['both', 'horizontal'] else 1
            sy = 1 - new_height / old_height if old_height > 0 and direction in ['both', 'vertical'] else 1
            
            # Function to scale a list of points
            def scale_points(points, ref_x, ref_y, sx, sy):
                return [[(x - ref_x) * sx + ref_x, (y - ref_y) * sy + ref_y] for x, y in points]
            
            # Scale VG's "coords"
            new_layout[VG_key]["coords"] = scale_points(coords, ref_x, ref_y, sx, sy)
            
            # Scale "Subtitle" if exists
            if "Subtitle" in new_layout[VG_key]:
                new_layout[VG_key]["Subtitle"] = scale_points(new_layout[VG_key]["Subtitle"], ref_x, ref_y, sx, sy)
            
            # Scale each KG's elements
            for kg_key in new_layout[VG_key]:
                if kg_key.startswith("KG"):
                    kg = new_layout[VG_key][kg_key]
                    if "coords" in kg:
                        kg["coords"] = scale_points(kg["coords"], ref_x, ref_y, sx, sy)
                    if "Highlight" in kg:
                        kg["Highlight"] = scale_points(kg["Highlight"], ref_x, ref_y, sx, sy)
                    if "Icon" in kg and kg["Icon"] is not None:
                        kg["Icon"] = scale_points(kg["Icon"], ref_x, ref_y, sx, sy)
                    if "Vis" in kg and kg["Vis"] is not None:
                        kg["Vis"] = scale_points(kg["Vis"], ref_x, ref_y, sx, sy)
                    if "Text" in kg and kg["Text"] is not None:
                        kg["Text"] = scale_points(kg["Text"], ref_x, ref_y, sx, sy)

    return add_padding_to_layout(new_layout)