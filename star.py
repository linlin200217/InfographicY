from math import sqrt

from util import add_padding_to_layout

def layout_poster(valentine_data, W, H, margin=0, vertical_margin=0):
    """
    Lays out a poster with a title, Super Groups (SGHs and SGVs) containing Visual Groups (VGs),
    and Knowledge Groups (KGs) within VGs. SGHs stack VGs horizontally, SGVs stack VGs vertically.
    The virtual VG's area is 1/4 of the non-subtitle parts of all VGs.

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

    # Helper function to define layout structure based on number of original VGs
    def get_layout_structure(n):
        if n == 1:
            return [('SGH', [2, 1])]
        elif n == 2:
            return [('SGH', [3, 1]), ('SGH', [2])]
        elif n == 3:
            return [('SGH', [1, 4, 2]), ('SGH', [3])]
        elif n == 4:
            return [('SGH', [1]), ('SGH', [2, 5, 3]), ('SGH', [4])]
        elif n == 5:
            return [('SGH', [1, 2]), ('SGH', [3, 6, 4]), ('SGH', [5])]
        elif n == 6:
            return [('SGH', [1, 2]), ('SGH', [3, 7, 4]), ('SGH', [5, 6])]
        elif n == 7:
            return [('SGH', [1, 2, 3]), ('SGH', [4, 8, 5]), ('SGH', [6, 7])]
        elif n == 8:
            return [('SGH', [1, 2]), ('SGH', [('SGV', [3, 4]), 9, ('SGV', [5, 6])]), ('SGH', [7, 8])]
        elif n == 9:
            return [('SGH', [1, 2, 3]), ('SGH', [('SGV', [4, 5]), 10, ('SGV', [6, 7])]), ('SGH', [8, 9])]
        elif n == 10:
            return [('SGH', [1, 2, 3]), ('SGH', [('SGV', [4, 5]), 11, ('SGV', [6, 7])]), ('SGH', [8, 9, 10])]
        else:
            raise ValueError("Number of VGs must be between 1 and 10")

    # Helper function to map VG label to index
    def get_vg_idx(label, n_original):
        return label - 1 if label <= n_original else n_original

    # Helper function to calculate VG height
    def calculate_vg_height(vg_idx, w_VG, VGs, x, margin, vertical_margin):
        VG = VGs[vg_idx]
        if VG.get("is_virtual", False):
            return 0.0
        knowledges = VG["knowledges"]
        n_KG = len(knowledges)
        kg_width = w_VG if n_KG == 1 else w_VG - 2 * margin
        h_VG = 1.5 * x  # Subtitle height
        if n_KG > 1:
            h_VG += vertical_margin
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
            h_KG = A_KG / kg_width if kg_width > 0 else 0.0
            h_VG += h_KG
            if n_KG > 1:
                h_VG += vertical_margin
        if n_KG > 1:
            h_VG -= vertical_margin  # Remove extra margin at the end
        return h_VG

    # Helper function to calculate element area
    def get_element_area(element, vg_areas, n_original):
        if isinstance(element, int):
            vg_idx = get_vg_idx(element, n_original)
            return vg_areas[vg_idx]
        elif isinstance(element, tuple) and element[0] == 'SGV':
            return sum(vg_areas[get_vg_idx(label, n_original)] for label in element[1])
        return 0.0

    # Helper function to calculate element height
    def calculate_element_height(element, w_element, VGs, x, margin, vertical_margin, n_original):
        if isinstance(element, int):
            vg_idx = get_vg_idx(element, n_original)
            return calculate_vg_height(vg_idx, w_element, VGs, x, margin, vertical_margin)
        elif isinstance(element, tuple) and element[0] == 'SGV':
            vg_indices = [get_vg_idx(label, n_original) for label in element[1]]
            return sum(calculate_vg_height(vg_idx, w_element, VGs, x, margin, vertical_margin) for vg_idx in vg_indices)
        return 0.0

    # Helper function to layout a VG
    def layout_vg(vg_idx, x_start, y_start, w_VG, h_VG, VGs, x, margin, vertical_margin, layout):
        VG = VGs[vg_idx]
        VG_key = f"VG{vg_idx + 1}"
        layout[VG_key] = {"coords": [[x_start, y_start], [x_start + w_VG, y_start], [x_start, y_start + h_VG], [x_start + w_VG, y_start + h_VG]]}
        if VG.get("is_virtual", False):
            return  # Virtual VG has no content
        knowledges = VG["knowledges"]
        n_KG = len(knowledges)
        kg_width = w_VG if n_KG == 1 else w_VG - 2 * margin
        kg_x = x_start if n_KG == 1 else x_start + margin

        # Subtitle
        layout[VG_key]["Subtitle"] = [
            [x_start, y_start], [x_start + w_VG, y_start],
            [x_start, y_start + 1.5 * x], [x_start + w_VG, y_start + 1.5 * x]
        ]
        y_VG = y_start + 1.5 * x
        if n_KG > 1:
            y_VG += vertical_margin

        ### BEGIN ADDED CODE ###
        # Helper function to calculate area of a rectangle
        def calculate_area(x1, y1, x2, y2):
            return (x2 - x1) * (y2 - y1)
        ### END ADDED CODE ###

        # Layout KGs
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
            layout[VG_key][KG_key] = {
                "coords": [
                    [kg_x, y_VG], [kg_x + kg_width, y_VG],
                    [kg_x, y_VG + h_KG], [kg_x + kg_width, y_VG + h_KG]
                ],
                "Highlight": [
                    [kg_x, y_VG], [kg_x + min(calculate_text_width(highlight, 2.0 * x), kg_width), y_VG],
                    [kg_x, y_VG + 2.0 * x], [kg_x + min(calculate_text_width(highlight, 2.0 * x), kg_width), y_VG + 2.0 * x]
                ],
                "Icon": None,
                "Vis": None,
                ### BEGIN ADDED CODE ###
                "placement_type": None  # Initialize placement_type
                ### END ADDED CODE ###
            }

            # Image placement logic
            aspect_ratios = [1.0, 1.333, 0.75, 1.5, 0.667, 1.777, 0.562, 0.5, 2.0, 1.4, 0.714, 0.8, 1.25, 0.6, 1.667]

            def try_placement_a(r, A_img):
                w_img = sqrt(A_img * r)
                h_img = sqrt(A_img / r)
                x1 = kg_x + kg_width - w_img
                y1 = y_VG
                x2 = kg_x + kg_width
                y2 = y_VG + h_img
                coords = [[x1, y1], [x2, y1], [x1, y2], [x2, y2]]
                overflow_area = 0
                if y2 > y_VG + h_KG:
                    overflow_area += (y2 - (y_VG + h_KG)) * w_img
                if x1 < kg_x + min(calculate_text_width(highlight, 2.0 * x), kg_width):
                    overlap_area = (min(x2, kg_x + min(calculate_text_width(highlight, 2.0 * x), kg_width)) - x1) * h_img if x2 > kg_x + min(calculate_text_width(highlight, 2.0 * x), kg_width) else w_img * h_img
                    overflow_area += overlap_area
                return True if overflow_area == 0 else False, coords, overflow_area

            def try_placement_b(r, A_img):
                w_img = sqrt(A_img * r)
                h_img = sqrt(A_img / r)
                x1 = kg_x
                y1 = y_VG + 2.0 * x
                x2 = kg_x + w_img
                y2 = y_VG + 2.0 * x + h_img
                coords = [[x1, y1], [x2, y1], [x1, y2], [x2, y2]]
                overflow_area = 0
                if y2 > y_VG + h_KG:
                    overflow_area += (y2 - (y_VG + h_KG)) * w_img
                if x2 > kg_x + kg_width:
                    overflow_area += (x2 - (kg_x + kg_width)) * h_img
                return True if overflow_area == 0 else False, coords, overflow_area

            def try_combination_1(r_a, r_b):
                w_a = sqrt(A_icon * r_a)
                h_a = sqrt(A_icon / r_a)
                w_b = sqrt(A_vis * r_b)
                h_b = sqrt(A_vis / r_b)
                x1_a = kg_x + kg_width - w_a
                y1_a = y_VG
                x2_a = kg_x + kg_width
                y2_a = y_VG + h_a
                coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                x1_b = kg_x + kg_width - w_a - w_b
                y1_b = y_VG
                x2_b = kg_x + kg_width - w_a
                y2_b = y_VG + h_b
                coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                overflow_area = 0
                if y2_a > y_VG + h_KG:
                    overflow_area += (y2_a - (y_VG + h_KG)) * w_a
                if y2_b > y_VG + h_KG:
                    overflow_area += (y2_b - (y_VG + h_KG)) * w_b
                w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                if x1_a < kg_x + w_highlight and y1_a < y_VG + 2.0 * x:
                    overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, 2.0 * x) if x2_a > kg_x + w_highlight else w_a * min(h_a, 2.0 * x)
                    overflow_area += overlap_area
                if x1_b < kg_x + w_highlight and y1_b < y_VG + 2.0 * x:
                    overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, 2.0 * x) if x2_b > kg_x + w_highlight else w_b * min(h_b, 2.0 * x)
                    overflow_area += overlap_area
                return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

            def try_combination_2(r_a, r_b):
                w_a = sqrt(A_icon * r_a)
                h_a = sqrt(A_icon / r_a)
                w_b = sqrt(A_vis * r_b)
                h_b = sqrt(A_vis / r_b)
                x1_a = kg_x + kg_width - w_a
                y1_a = y_VG
                x2_a = kg_x + kg_width
                y2_a = y_VG + h_a
                coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                x1_b = kg_x
                y1_b = y_VG + 2.0 * x
                x2_b = kg_x + w_b
                y2_b = y_VG + 2.0 * x + h_b
                coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                overflow_area = 0
                if y2_a > y_VG + h_KG:
                    overflow_area += (y2_a - (y_VG + h_KG)) * w_a
                if y2_b > y_VG + h_KG:
                    overflow_area += (y2_b - (y_VG + h_KG)) * w_b
                w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                if x1_a < kg_x + w_highlight and y1_a < y_VG + 2.0 * x:
                    overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, 2.0 * x) if x2_a > kg_x + w_highlight else w_a * min(h_a, 2.0 * x)
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
                y1_a = y_VG
                x2_a = kg_x + kg_width
                y2_a = y_VG + h_a
                coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                x1_b = kg_x + kg_width - w_b
                y1_b = y_VG + h_a
                x2_b = kg_x + kg_width
                y2_b = y_VG + h_a + h_b
                coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                overflow_area = 0
                if y2_a > y_VG + h_KG:
                    overflow_area += (y2_a - (y_VG + h_KG)) * w_a
                if y2_b > y_VG + h_KG:
                    overflow_area += (y2_b - (y_VG + h_KG)) * w_b
                w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                if x1_a < kg_x + w_highlight and y1_a < y_VG + 2.0 * x:
                    overlap_area = (min(x2_a, kg_x + w_highlight) - x1_a) * min(h_a, 2.0 * x) if x2_a > kg_x + w_highlight else w_a * min(h_a, 2.0 * x)
                    overflow_area += overlap_area
                if x1_b < kg_x + w_highlight and y1_b < y_VG + 2.0 * x:
                    overlap_area = (min(x2_b, kg_x + w_highlight) - x1_b) * min(h_b, 2.0 * x - (y1_b - y_VG)) if x2_b > kg_x + w_highlight else w_b * min(h_b, 2.0 * x - (y1_b - y_VG))
                    overflow_area += overlap_area
                return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

            def try_combination_4(r_a, r_b):
                w_a = sqrt(A_icon * r_a)
                h_a = sqrt(A_icon / r_a)
                w_b = sqrt(A_vis * r_b)
                h_b = sqrt(A_vis / r_b)
                x1_a = kg_x
                y1_a = y_VG + 2.0 * x
                x2_a = kg_x + w_a
                y2_a = y_VG + 2.0 * x + h_a
                coords_a = [[x1_a, y1_a], [x2_a, y1_a], [x1_a, y2_a], [x2_a, y2_a]]
                x1_b = kg_x + kg_width - w_b
                y1_b = y_VG + h_KG - h_b
                x2_b = kg_x + kg_width
                y2_b = y_VG + h_KG
                coords_b = [[x1_b, y1_b], [x2_b, y1_b], [x1_b, y2_b], [x2_b, y2_b]]
                overflow_area = 0
                if y2_a > y_VG + h_KG:
                    overflow_area += (y2_a - (y_VG + h_KG)) * w_a
                if x2_a > kg_x + kg_width:
                    overflow_area += (x2_a - (kg_x + kg_width)) * h_a
                if x1_b < kg_x:
                    overflow_area += (kg_x - x1_b) * h_b
                if y1_b < y_VG:
                    overflow_area += (y_VG - y1_b) * w_b
                w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                if x1_b < kg_x + w_highlight and y1_b < y_VG + 2.0 * x:
                    overlap_width = (min(x2_b, kg_x + w_highlight) - x1_b) if x2_b > kg_x + w_highlight else w_b
                    overlap_height = min(h_b, 2.0 * x - (y1_b - y_VG))
                    overflow_area += overlap_width * overlap_height
                return True if overflow_area == 0 else False, coords_a, coords_b, overflow_area

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
                                ### BEGIN ADDED CODE ###
                                layout[VG_key][KG_key]["placement_type"] = f"comb{idx + 1}"
                                ### END ADDED CODE ###
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
                    w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                    h_highlight = 2.0 * x
                    if comb_idx == 0:
                        if x1_a < kg_x + w_highlight:
                            w_a = kg_width - (kg_x + w_highlight - x1_a)
                        if y2_a > y_VG + h_KG:
                            h_a = h_KG - (y1_a - y_VG)
                        w_a_new = min(w_a, h_a * r_a)
                        h_a_new = w_a_new / r_a
                        coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                        if x1_b < kg_x + w_highlight:
                            w_b = kg_width - (kg_x + w_highlight - x1_b)
                        if y2_b > y_VG + h_KG:
                            h_b = h_KG - (y1_b - y_VG)
                        w_b_new = min(w_b, h_b * r_b)
                        h_b_new = w_b_new / r_b
                        coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                    # elif comb_idx == 1:
                    #     if x1_a < kg_x + w_highlight:
                    #         w_a = kg_width - (kg_x + w_highlight - x1_a)
                    #     if y2_a > y_VG + h_KG:
                    #         h_a = h_KG - (y1_a - y_VG)
                    #     w_a_new = min(w_a, h_a * r_a)
                    #     h_a_new = w_a_new / r_a
                    #     coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                    #     if x2_b > kg_x + kg_width:
                    #         w_b = kg_width - (x1_b - kg_x)
                    #     if y2_b > y_VG + h_KG:
                    #         h_b = h_KG - (y1_b - y_VG)
                    #     w_b_new = min(w_b, h_b * r_b)
                    #     h_b_new = w_b_new / r_b
                    #     coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                    elif comb_idx == 1:  # Combination 2
                        # Resize Icon (A), anchored at top-right
                        if x1_a < kg_x + w_highlight:
                            w_a = kg_width - (kg_x + w_highlight - x1_a)  # Max width from Highlight's right edge
                        if y2_a > y_VG + h_KG:
                            h_a = h_KG - (y1_a - y_VG)  # Max height within KG
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
                        if y2_b > y_VG + h_KG:
                            h_b = h_KG - (y1_b - y_VG)  # Max height within KG
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
                        if y2_a > y_VG + h_KG:
                            h_a = h_KG - (y1_a - y_VG)
                        w_a_new = min(w_a, h_a * r_a)
                        h_a_new = w_a_new / r_a
                        coords_a = [[x1_a, y1_a], [x1_a + w_a_new, y1_a], [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]]
                        if x1_b < kg_x + w_highlight:
                            w_b = kg_width - (kg_x + w_highlight - x1_b)
                        if y2_b > y_VG + h_KG:
                            h_b = h_KG - (y1_b - y_VG)
                        w_b_new = min(w_b, h_b * r_b)
                        h_b_new = w_b_new / r_b
                        coords_b = [[x1_b, y1_b], [x1_b + w_b_new, y1_b], [x1_b, y1_b + h_b_new], [x1_b + w_b_new, y1_b + h_b_new]]
                    elif comb_idx == 3:  # Combination 4
                        # Resize Icon (A), anchored at top-left
                        if x2_a > kg_x + kg_width:
                            w_a = kg_width - (x1_a - kg_x)  # Max width within KG
                        if y2_a > y_VG + h_KG:
                            h_a = h_KG - (y1_a - y_VG)  # Max height within KG
                        w_a_new = min(w_a, h_a * r_a)  # Preserve aspect ratio
                        h_a_new = w_a_new / r_a
                        coords_a = [
                            [x1_a, y1_a], [x1_a + w_a_new, y1_a],
                            [x1_a, y1_a + h_a_new], [x1_a + w_a_new, y1_a + h_a_new]
                        ]
                        # Resize Visualization (B), anchored at bottom-right
                        if x1_b < kg_x:
                            w_b = kg_width  # Max width if exceeding left edge
                        if y1_b < y_VG:
                            h_b = h_KG  # Max height if exceeding top
                        # Initial aspect ratio adjustment
                        w_b_new = min(w_b, h_b * r_b)
                        h_b_new = w_b_new / r_b
                        # Check Highlight overlap and scale if necessary
                        x1_b_tentative = x2_b - w_b_new  # Tentative left edge
                        y1_b_tentative = y2_b - h_b_new  # Tentative top edge
                        if x1_b_tentative < kg_x + w_highlight and y1_b_tentative < y_VG + h_highlight:
                            ratio_x = (kg_width - w_highlight) / w_b
                            ratio_y = (h_KG - h_highlight) / h_b
                            scale = max(ratio_x, ratio_y)
                            w_b_new = w_b * scale
                            h_b_new = h_b * scale
                        # Check if Icon's bottom-right corner overlaps Visualization's top-left corner
                        x1_b_tentative = x2_b - w_b_new  # Recalculate tentative left edge after scaling
                        y1_b_tentative = y2_b - h_b_new  # Recalculate tentative top edge
                        if x1_a + w_a_new > x1_b_tentative and y1_a + h_a_new > y1_b_tentative:
                            w_b_new = min(w_b_new, kg_x + kg_width - (x1_a + w_a_new))  # Limit width to avoid overlap
                            h_b_new = w_b_new / r_b  # Recalculate height to maintain aspect ratio
                        # Final coordinates for Visualization, anchored at bottom-right
                        x1_b_new = x2_b - w_b_new
                        y1_b_new = y2_b - h_b_new
                        coords_b = [
                            [x1_b_new, y1_b_new], [x2_b, y1_b_new],
                            [x1_b_new, y2_b], [x2_b, y2_b]
                        ]
                    layout[VG_key][KG_key]["Icon"] = coords_a
                    layout[VG_key][KG_key]["Vis"] = coords_b
                    ### BEGIN ADDED CODE ###
                    layout[VG_key][KG_key]["placement_type"] = f"comb{comb_idx + 1}"
                    ### END ADDED CODE ###
            elif has_icon:
                min_overflow = float('inf')
                best_layout = None
                placement_funcs = [try_placement_a, try_placement_b]
                for idx, placement in enumerate(placement_funcs):
                    for r in aspect_ratios:
                        fit, coords, overflow = placement(r, A_icon)
                        if fit:
                            layout[VG_key][KG_key]["Icon"] = coords
                            ### BEGIN ADDED CODE ###
                            layout[VG_key][KG_key]["placement_type"] = 'a' if idx == 0 else 'b'
                            ### END ADDED CODE ###
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
                    w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                    if placement_idx == 0:
                        if x1 < kg_x + w_highlight:
                            w_img = kg_width - w_highlight
                        if y2 > y_VG + h_KG:
                            h_img = h_KG - (y1 - y_VG)
                        w_img_new = min(w_img, h_img * r)
                        h_img_new = w_img_new / r
                        coords = [
                                [x2 - w_img_new, y1],  # New top-left
                                [x2, y1],              # New top-right
                                [x2 - w_img_new, y1 + h_img_new],              # New bottom-left
                                [x2, y1 + h_img_new]                           # Bottom-right (fixed)
                            ]
                    elif placement_idx == 1:
                        if x2 > kg_x + kg_width:
                            w_img = kg_width - (x1 - kg_x)
                        if y2 > y_VG + h_KG:
                            h_img = h_KG - (y1 - y_VG)
                        w_img_new = min(w_img, h_img * r)
                        h_img_new = w_img_new / r
                        coords = [
                            [x1, y1], [x1 + w_img_new, y1],
                            [x1, y1 + h_img_new], [x1 + w_img_new, y1 + h_img_new]
                        ]
                    layout[VG_key][KG_key]["Icon"] = coords
                    ### BEGIN ADDED CODE ###
                    layout[VG_key][KG_key]["placement_type"] = 'a' if placement_idx == 0 else 'b'
                    ### END ADDED CODE ###
            elif has_vis:
                min_overflow = float('inf')
                best_layout = None
                placement_funcs = [try_placement_a, try_placement_b]
                for idx, placement in enumerate(placement_funcs):
                    for r in aspect_ratios:
                        fit, coords, overflow = placement(r, A_vis)
                        if fit:
                            layout[VG_key][KG_key]["Vis"] = coords
                            ### BEGIN ADDED CODE ###
                            layout[VG_key][KG_key]["placement_type"] = 'a' if idx == 0 else 'b'
                            ### END ADDED CODE ###
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
                    w_highlight = min(calculate_text_width(highlight, 2.0 * x), kg_width)
                    if placement_idx == 0:
                        if x1 < kg_x + w_highlight:
                            w_img = kg_width - w_highlight
                        if y2 > y_VG + h_KG:
                            h_img = h_KG - (y1 - y_VG)
                        w_img_new = min(w_img, h_img * r)
                        h_img_new = w_img_new / r
                        coords = [
                                [x2 - w_img_new, y1],  # New top-left
                                [x2, y1],              # New top-right
                                [x2 - w_img_new, y1 + h_img_new],              # New bottom-left
                                [x2, y1 + h_img_new]                           # Bottom-right (fixed)
                            ]
                    elif placement_idx == 1:
                        if x2 > kg_x + kg_width:
                            w_img = kg_width - (x1 - kg_x)
                        if y2 > y_VG + h_KG:
                            h_img = h_KG - (y1 - y_VG)
                        w_img_new = min(w_img, h_img * r)
                        h_img_new = w_img_new / r
                        coords = [
                            [x1, y1], [x1 + w_img_new, y1],
                            [x1, y1 + h_img_new], [x1 + w_img_new, y1 + h_img_new]
                        ]
                    layout[VG_key][KG_key]["Vis"] = coords
                    ### BEGIN AD enhanced CODE ###
                    layout[VG_key][KG_key]["placement_type"] = 'a' if placement_idx == 0 else 'b'
                    ### END ADDED CODE ###

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

            y_VG += h_KG
            if j < n_KG:
                y_VG += vertical_margin

    # Main layout logic
    original_VGs = valentine_data["data"]
    n_original_VG = len(original_VGs)
    virtual_VG = {"knowledges": [], "is_virtual": True}
    VGs = original_VGs + [virtual_VG]

    # Calculate coefficients for b * x^2 + a * x + c = 0
    if n_original_VG in [1, 2, 3, 4, 5, 6, 7]:
        a = 3.0 * W + 1.5 * len(get_layout_structure(n_original_VG)) * W
    elif n_original_VG in [8, 9, 10]:
        a = 3.0 * W + 1.5 * (len(get_layout_structure(n_original_VG)) + 1) * W
    b = 0.0
    c = -H * W
    vg_areas = []

    # Compute vg_areas and b for original VGs
    for VG in original_VGs:
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
            b += s_KG
        vg_areas.append(sum_s_KG)

    b *= 5/4
    vg_areas.append(sum(vg_areas) / 4 if n_original_VG > 0 else 0.0)

    for VG in original_VGs:
        n_KG = len(VG["knowledges"])
        if n_KG > 1:
            c += (n_KG - 1) * vertical_margin * W

    discriminant = a**2 - 4 * b * c
    if discriminant < 0:
        raise ValueError("No solution for font size x")
    x = (-a + sqrt(discriminant)) / (2 * b) if b != 0 else -c / a
    if x <= 0:
        raise ValueError("Invalid font size x")

    structure = get_layout_structure(n_original_VG)
    layout = {"Title": [[0.0, 0.0], [W, 0.0], [0.0, 3.0 * x], [W, 3.0 * x]]}
    y = 3.0 * x

    for sgh in structure:
        assert sgh[0] == 'SGH'
        elements = sgh[1]
        total_area_in_sgh = sum(get_element_area(elem, vg_areas, n_original_VG) for elem in elements)
        element_widths = [W * (get_element_area(elem, vg_areas, n_original_VG) / total_area_in_sgh) if total_area_in_sgh > 0 else W / len(elements) for elem in elements]
        element_heights = [calculate_element_height(elem, w_elem, VGs, x, margin, vertical_margin, n_original_VG) for w_elem, elem in zip(element_widths, elements)]
        h_SGH = max(element_heights) if element_heights else 0.0
        x_start = 0.0

        for elem, w_elem in zip(elements, element_widths):
            if isinstance(elem, int):
                vg_idx = get_vg_idx(elem, n_original_VG)
                layout_vg(vg_idx, x_start, y, w_elem, h_SGH, VGs, x, margin, vertical_margin, layout)
            elif isinstance(elem, tuple) and elem[0] == 'SGV':
                vg_indices = [get_vg_idx(label, n_original_VG) for label in elem[1]]
                y_sgv = y
                for vg_idx in vg_indices:
                    h_VG = calculate_vg_height(vg_idx, w_elem, VGs, x, margin, vertical_margin)
                    layout_vg(vg_idx, x_start, y_sgv, w_elem, h_VG, VGs, x, margin, vertical_margin, layout)
                    y_sgv += h_VG
            x_start += w_elem

        y += h_SGH

    return add_padding_to_layout(layout)