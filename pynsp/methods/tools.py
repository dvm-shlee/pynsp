import psutil
import numpy as np


def get_cluster_coordinates(coord, size=1, NN=3, mask=None):
    """
    size: number of voxels want to include from the center
    NN: 1='faces', 2='faces and edges', 3='faces, edges, and corners'
    """
    n_voxel = size + 1
    x, y, z = coord
    X = sorted([x + i for i in range(n_voxel)] + [x - i for i in range(n_voxel) if i != 0])
    Y = sorted([y + i for i in range(n_voxel)] + [y - i for i in range(n_voxel) if i != 0])
    Z = sorted([z + i for i in range(n_voxel)] + [z - i for i in range(n_voxel) if i != 0])

    if NN is 1:
        thr = size
    elif NN is 2:
        thr = np.sqrt(np.square([size] * 2).sum())
    elif NN is 3:
        thr = np.sqrt(np.square([size] * 3).sum())
    else:
        raise Exception #TODO: Exception message handler

    all_poss = [(i, j, k) for i in X for j in Y for k in Z]
    output_coord = [c for c in all_poss if cal_distance(coord, c) <= thr]

    if mask is None:
        return output_coord
    else:
        return [c for c in output_coord if c in mask]


def cal_distance(coord1, coord2):
    return np.sqrt(np.square(np.diff(np.asarray(zip(coord1, coord2)))).sum())


def optimal_split(num, cpus, scale=10):
    result = [num%(i+1) for i in range(cpus*scale)]
    return [i+1 for i, x in enumerate(result) if x == 0][-1]


def avail_cpu():
    cpu_percent = np.sum(psutil.cpu_percent(percpu=True))
    cpu_count = psutil.cpu_count()
    return int(cpu_count * (1 - ((cpu_percent / cpu_count) * 2)/100))


def extract_ts_from_coordinates(img_data, indices, n_voxels='Max', iters=None, replace=False):
    """
    Extract time-series data from ROI defined on Atlas.
    if size are provided, data will be collected from
    the randomly sampled voxels with given size.

    :param img_data: 3D+time data matrix
    :param indices: All coordinates inside the roi
    :param n_voxels: number of voxels that want to sample (default = 'Max')
    :param iters: number of iteration to perform random voxel sampling
    :type img_data: numpy.ndarray
    :type indices: 2D list
    :type n_voxels: int or 'Max'
    :type iters: int
    :return: 2 dimentional time-series data (averaged time-series data,
                                             number of iteration)
    :rtype return: numpy.ndarray
    """
    # The below code allows to use single coordinate index instead of set of indices
    if isinstance(indices, list) and isinstance(indices[0], int):
        indices = np.asarray([indices])
    elif isinstance(indices, list) and isinstance(indices[0], list):
        indices = np.asarray(indices)
    else:
        pass

    num_ind = indices.shape[0]

    if n_voxels == 'Max':
        n_voxels = num_ind

    if iters is not None:
        result = np.zeros((img_data.shape[-1], iters))
        for i in range(iters):
            rand_index = sorted(np.random.choice(num_ind, size=n_voxels, replace=replace))
            indx, indy, indz = indices[rand_index].T.tolist()
            result[:, i] = img_data[indx, indy, indz, :].mean(0)
    else:
        indx, indy, indz = indices[np.random.choice(num_ind, size=n_voxels)].T.tolist()
        result = img_data[indx, indy, indz, :].mean(0)
    return result