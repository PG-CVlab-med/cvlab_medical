def is_image_3d(arr):
    if arr is not None and len(arr.shape) == 3 and arr.shape[2] != 3:
        return True
    return False
