from math import sqrt
from util import add_padding_to_layout
def layout_poster(valentine_data, W, H, margin=0, vertical_margin=0):
    """
    Lays out a poster with title and VGs stacked horizontally from left to right,
    with KGs stacked vertically within each VG.
    
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

    VGs = valentine_data["data"]

    # Calculate coefficients for the quadratic equation b x^2 + a x + c = 0
    a = 3.0 * W  # From title height 3x
    c = - H * W  # Total available area term
    b = 0.0      # Area coefficient

    for VG in VGs:
        knowledges = VG["knowledges"]
        for KG in knowledges:
            text = KG["knowledge_content"]
            highlight = KG["first_level_highlight"]
            n_images = (1 if KG["icon_keyword"] != "" else 0) + (1 if KG["visualization"]["is_visualization"] else 0)
            s_text = calculate_text_width(text, 1.0)
            s_highlight = calculate_text_width(highlight, 1.0)
            b += s_text + 4 * s_highlight + s_text * n_images

    # Solve the quadratic equation b x^2 + a x + c = 0
    discriminant = a**2 - 4 * b * c
    if discriminant < 0:
        raise ValueError("No solution for font size x")
    x = (-a + sqrt(discriminant)) / (2 * b) if b != 0 else -c / a
    if x <= 0:
        raise ValueError("Invalid font size x")

    # Calculate available height and VG areas
    h_title = 3.0 * x
    h_remain = H - h_title
    
    # Calculate total area A_VG for each VG
    A_VGs = []
    for VG in VGs:
        knowledges = VG["knowledges"]
        A_VG = 0.0
        for KG in knowledges:
            text = KG["knowledge_content"]
            highlight = KG["first_level_highlight"]
            has_icon = KG["icon_keyword"] != ""
            has_vis = KG["visualization"]["is_visualization"]
            A_text = x * calculate_text_width(text, x)
            A_highlight = 2.0 * x * calculate_text_width(highlight, 2.0 * x)
            A_icon = x * calculate_text_width(text, x) if has_icon else 0.0
            A_vis = x * calculate_text_width(text, x) if has_vis else 0.0
            A_KG = A_text + A_highlight + A_icon + A_vis
            A_VG += A_KG
        A_VGs.append(A_VG)
    
    # Calculate ideal widths for each VG
    w_VG_ideals = []
    for i, VG in enumerate(VGs):
        n_KG = len(VG["knowledges"])
        if n_KG == 1:
            denominator = h_remain - 1.5 * x
        else:
            denominator = h_remain - 1.5 * x - (n_KG - 1) * vertical_margin
        w_VG_ideal = A_VGs[i] / denominator if denominator > 0 else 0.0
        w_VG_ideals.append(w_VG_ideal)
    
    # Scale widths to fit total width W
    W_ideal = sum(w_VG_ideals)
    scaling_factor = W / W_ideal if W_ideal > 0 else 1.0
    w_VGs = [w * scaling_factor for w in w_VG_ideals]
    
    # Calculate x-positions for each VG
    x_VGs = [0.0]
    for w in w_VGs[:-1]:
        x_VGs.append(x_VGs[-1] + w)
    
    # Layout the poster
    layout = {}
    layout["Title"] = [[0.0, 0.0], [W, 0.0], [0.0, h_title], [W, h_title]]
    
    for i, VG in enumerate(VGs, 1):
        x_VG = x_VGs[i-1]
        w_VG = w_VGs[i-1]
        knowledges = VG["knowledges"]
        n_KG = len(knowledges)
        
        VG_key = f"VG{i}"
        layout[VG_key] = {}
        
        # Subtitle
        y = h_title
        layout[VG_key]["Subtitle"] = [[x_VG, y], [x_VG + w_VG, y], [x_VG, y + 1.5 * x], [x_VG + w_VG, y + 1.5 * x]]
        y += 1.5 * x
        if n_KG > 1:
            y += vertical_margin
        
        for j, KG in enumerate(knowledges, 1):
            # Determine KG width and x-position
            if n_KG == 1:
                kg_x = x_VG
                kg_width = w_VG
            else:
                kg_x = x_VG + margin
                kg_width = w_VG - 2 * margin
            
            text = KG["knowledge_content"]
            highlight = KG["first_level_highlight"]
            has_icon = KG["icon_keyword"] != ""
            has_vis = KG["visualization"]["is_visualization"]
            
            # Calculate areas
            A_text = x * calculate_text_width(text, x)
            A_highlight = 2.0 * x * calculate_text_width(highlight, 2.0 * x)
            A_icon = x * calculate_text_width(text, x) if has_icon else 0.0
            A_vis = x * calculate_text_width(text, x) if has_vis else 0.0
            A_KG = A_text + A_highlight + A_icon + A_vis
            h_KG = A_KG / kg_width if kg_width > 0 else 0.0
            
            KG_key = f"KG{j}"
            layout[VG_key][KG_key] = {}
            layout[VG_key][KG_key]["coords"] = [
                [kg_x, y], [kg_x + kg_width, y],
                [kg_x, y + h_KG], [kg_x + kg_width, y + h_KG]
            ]
            
            # Internal KG layout
            y_KG = y
            h_highlight = 2.0 * x
            w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
            layout[VG_key][KG_key]["Highlight"] = [
                [kg_x, y_KG], [kg_x + w_highlight, y_KG],
                [kg_x, y_KG + h_highlight], [kg_x + w_highlight, y_KG + h_highlight]
            ]
            layout[VG_key][KG_key]["Icon"] = None
            layout[VG_key][KG_key]["Vis"] = None
            # Added: Initialize placement_type
            layout[VG_key][KG_key]["placement_type"] = "none"

            # Image placement logic
            aspect_ratios = [
                1.0, 1.333, 0.75, 1.5, 0.667, 1.777, 0.562, 0.5, 2.0,
                1.4, 0.714, 0.8, 1.25, 0.6, 1.667
            ]

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
                if y2_b > y_KG + h_KG:  # Shouldn't happen due to bottom alignment
                    overflow_area += (y2_b - (y_KG + h_KG)) * w_b
                if x1_b < kg_x + w_highlight and y1_b < y_KG + h_highlight:
                    overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, h_highlight - (y1_b - y_KG)) if x2_b > kg_x + w_highlight else w_b * min(h_b, h_highlight - (y1_b - y_KG))
                    overflow_area += overlap_area
                return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

            # Place images and set placement_type
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
                                # Added: Set placement_type when fit is found
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
                    elif comb_idx == 1:
                        if x1_a < kg_x + w_highlight:
                            w_a = kg_width - (kg_x + w_highlight - x1_a)
                        if y2_a > y_KG + h_KG:
                            h_a = h_KG - (y1_a - y_KG)
                        w_a_new = min(w_a, h_a * r_a)
                        h_a_new = w_a_new / r_a
                        coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                        if x2_b > kg_x + kg_width:
                            w_b = kg_width - (x1_b - kg_x)
                        if y2_b > y_KG + h_KG:
                            h_b = h_KG - (y1_b - y_KG)
                        if x2_b > x1_a + w_a_new:
                            w_b = min(w_b, x1_a + w_a_new - x1_b)
                        w_b_new = min(w_b, h_b * r_b)
                        h_b_new = w_b_new / r_b
                        coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
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
                        if x1_b < kg_x + w_highlight:
                            w_b = kg_width - (kg_x + w_highlight - x1_b)
                        if y2_b > y_KG + h_KG:
                            h_b = h_KG - (y1_b - y_KG)
                        w_b_new = min(w_b, h_b * r_b)
                        h_b_new = w_b_new / r_b
                        coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                    layout[VG_key][KG_key]["Icon"] = coords_a
                    layout[VG_key][KG_key]["Vis"] = coords_b
                    # Added: Set placement_type when adjusted
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
                            # Added: Set placement_type when fit is found
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
                            w_img = kg_width - (kg_x + w_highlight - x1)
                        if y2 > y_KG + h_KG:
                            h_img = h_KG - (y1 - y_KG)
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
                    # Added: Set placement_type when adjusted
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
                            # Added: Set placement_type when fit is found
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
                            w_img = kg_width - (kg_x + w_highlight - x1)
                        if y2 > y_KG + h_KG:
                            h_img = h_KG - (y1 - y_KG)
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
                    # Added: Set placement_type when adjusted
                    layout[VG_key][KG_key]["placement_type"] = 'a' if placement_idx == 0 else 'b'

            ### BEGIN ADDED CODE ###
            # Calculate text block based on placement type
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
                if y2_highlight <= y2_a <= y2_b:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x1_a, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x1_KG, y2_a), (x1_b, y2_KG)],
                        [(x1_KG, y2_b), (x2_KG, y2_KG)]
                    ]
                elif y2_highlight <= y2_b <= y2_a:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x1_a, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x1_KG, y2_a), (x2_KG, y2_KG)],
                        [(x2_a, y2_b), (x2_KG, y2_KG)]
                    ]
                elif y2_a <= y2_highlight <= y2_b:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x1_b, y2_KG)],
                        [(x1_KG, y2_b), (x2_KG, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x2_highlight, y2_a), (x1_b, y2_KG)]
                    ]
                elif y2_a <= y2_b <= y2_highlight:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x2_highlight, y2_a), (x1_b, y2_KG)],
                        [(x2_highlight, y2_b), (x2_KG, y2_KG)]
                    ]
                elif y2_b <= y2_highlight <= y2_a:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x2_a, y2_KG)],
                        [(x1_KG, y2_a), (x2_KG, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x1_b, y2_b), (x2_KG, y2_KG)]
                    ]
                elif y2_b <= y2_a <= y2_highlight:
                    possible_blocks = [
                        [(x1_KG, y2_highlight), (x2_KG, y2_KG)],
                        [(x2_highlight, y1_KG), (x1_a, y2_KG)],
                        [(x2_highlight, y2_a), (x2_KG, y2_KG)],
                        [(x1_b, y2_b), (x2_KG, y2_KG)]
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
                    [(x1_KG, y2_highlight), (x2_KG, y2_KG)]
                ]

            # Find the block with maximum area
            max_area = -1
            best_block = None
            for (x1, y1), (x2, y2) in possible_blocks:
                # Ensure coordinates are within KG bounds
                x1 = max(x1_KG, min(x2_KG, x1))
                x2 = max(x1_KG, min(x2_KG, x2))
                y1 = max(y1_KG, min(y2_KG, y1))
                y2 = max(y1_KG, min(y2_KG, y2))
                if x1 < x2 and y1 < y2:  # Valid rectangle
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
            ### END ADDED CODE ###

            y += h_KG
            if j < n_KG:
                y += vertical_margin
        
        # Set VG coordinates to span from h_title to H
        layout[VG_key]["coords"] = [
            [x_VG, h_title], [x_VG + w_VG, h_title],
            [x_VG, H], [x_VG + w_VG, H]
        ]
    
    return add_padding_to_layout(layout)

