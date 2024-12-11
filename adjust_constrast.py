import imageio
from pathlib import Path
import numpy as np

def adjust_contrast(SOURCE_FOLDER, DEST_FOLDER, std_reduction=.75):

    files = list(Path(SOURCE_FOLDER).iterdir())
    n_images = len(files)
    shape_images = imageio.imread(files[0]).shape
    # images = np.zeros((n_images,) + shape_images, dtype=float)
    images = []
    for i, filename in enumerate(files):
        im = imageio.imread(filename).astype(float)
        if im.ndim == 3:  # Check if the image has multiple channels
            im = np.dot(im[..., :3], [0.2989, 0.5870, 0.1140])  # Use the standard grayscale conversion formula
        images.append(im)


    STD_REDUCTION = std_reduction
    flat_images = np.concatenate([im.flatten() for im in images])
    grand_mean_intensity = flat_images.mean()
    grand_mean_std = flat_images.std() * STD_REDUCTION
    for i in range(n_images):
        image_mean = images[i].mean()
        image_std = images[i].std()
        
        print(f'{i}: intensity={images[i].mean()}, contrast={images[i].std()}')
        images[i] -= image_mean
        images[i] /= image_std / grand_mean_std
        images[i] += grand_mean_intensity
        images[i] = np.clip(images[i], 0, 255)


    for i in range(n_images):
        print(f'{i}: intensity={images[i].mean()}, contrast={images[i].std()}')
        
    for i, filename in enumerate(files):
        im = np.array(images[i], dtype=np.uint8)
        if not Path(DEST_FOLDER).exists():
            Path(DEST_FOLDER).mkdir()
        imageio.imwrite(Path(DEST_FOLDER) / filename.name, im)

    print(f'Read {n_images} images with shape {shape_images} from {SOURCE_FOLDER}.')
    
if __name__ == '__main__':
    adjust_contrast('./stimuli/setA', './stimuli/setA_contrast_adjusted', std_reduction=.75)
    adjust_contrast('./stimuli/setB', './stimuli/setB_contrast_adjusted', std_reduction=.75)
    adjust_contrast('./stimuli/setC', './stimuli/setC_contrast_adjusted', std_reduction=.75)