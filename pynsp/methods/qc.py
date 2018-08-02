def calc_displacements(volreg):
    """
    This function calculate volume displacement from motion parameter
    """
    import numpy as np
    import pandas as pd

    output = dict()
    columns = volreg.columns
    # Framewise displacement
    output['FD'] = np.abs(np.insert(np.diff(volreg, axis=0), 0, 0, axis=0)).sum(axis=1)
    # Absolute rotational displacement
    output['ARD'] = np.abs(np.insert(np.diff(volreg[columns[:3]], axis=0), 0, 0, axis=0)).sum(axis=1)
    # Absolute translational displacement
    output['ATD'] = np.abs(np.insert(np.diff(volreg[columns[3:]], axis=0), 0, 0, axis=0)).sum(axis=1)
    return pd.DataFrame(output)


def convert_radian2distance(volreg, mean_radius):
    import numpy as np
    volreg[['Roll', 'Pitch', 'Yaw']] *= (np.pi / 180 * mean_radius)
    return volreg


def calc_BOLD_properties(img_data, indices):
    import numpy as np
    import pandas as pd

    output = dict()
    diff_img = np.square(np.diff(img_data, axis=3))
    x, y, z, dt = diff_img.shape
    DVARS = np.sqrt(np.mean(diff_img.reshape([x * y * z, dt]), axis=0))
    DVARS = np.insert(DVARS, 0, np.nan)
    output['DVgs'] = DVARS

    vw_intensity = np.zeros([len(indices), img_data.shape[-1]])
    for idx, coord in enumerate(indices):
        i, t, k = coord
        vw_intensity[idx, :] = img_data[i, t, k, :]
    output['SDgs'] = vw_intensity.std(0)
    output['GS'] = vw_intensity.mean(0)

    output = pd.DataFrame(output)
    return output, vw_intensity


def calc_STD(img_obj, img_data):
    import numpy as np
    import pandas as pd
    x, y, z, t = img_data.shape
    flatten_data = img_data.reshape([x * y * z, t])
    output = np.zeros(t)


    for dt in range(t):
        vol = flatten_data[:, dt]
        vol = vol[np.nonzero(vol)]
        output[dt] = vol.std()
    df = pd.DataFrame(output, index=None, columns=['SDgs'])
    return df