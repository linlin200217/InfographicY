def scale_creation(coordinate):
    x0 = coordinate[0][0]
    x1 = coordinate[1][0]
    y0 = coordinate[0][1]
    y1 = coordinate[2][1]

    x_w = x1 - x0
    y_h = y1 - y0
    scale = x_w / y_h
    r = round(scale, 3)

    ratio_to_dimension = {
        1.0: '1024x1024',
        1.333: '1365x1024',
        0.75: '1024x1365',
        1.5: '1536x1024',
        0.667: '1024x1536',
        1.777: '1820x1024',
        0.563: '1024x1820',
        2.0: '2048x1024',
        0.5: '1024x2048',
        1.4: '1434x1024',
        0.714: '1024x1434',
        0.8: '1024x1280',
        1.25: '1280x1024',
        0.6: '1024x1707',
        1.667: '1707x1024'
    }


    if r in ratio_to_dimension:
        return ratio_to_dimension[r]
    else:

      closest_ratio = min(ratio_to_dimension.keys(), key=lambda k: abs(k - r))
      return ratio_to_dimension[closest_ratio]