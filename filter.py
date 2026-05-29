from pathlib import Path

import cv2
import numpy as np

try:
    from scipy.signal import wiener
except ImportError:
    wiener = None


IMAGE_PATH = "input_image.jpg"


def show_result(title, image):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(8, 5))
    if len(image.shape) == 2:
        plt.imshow(image, cmap="gray")
    else:
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis("off")
    plt.show()


def to_gray(image):
    if len(image.shape) == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def gaussian_filter(image, kernel_size=5):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def median_filter(image, kernel_size=5):
    return cv2.medianBlur(image, kernel_size)


def bilateral_filter(image, diameter=9, sigma_color=75, sigma_space=75):
    return cv2.bilateralFilter(image, diameter, sigma_color, sigma_space)


def nl_means_filter(
    image, h_luminance=10, h_color=10, template_window=7, search_window=21
):
    return cv2.fastNlMeansDenoisingColored(
        image, None, h_luminance, h_color, template_window, search_window
    )


def clahe_enhance(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced_l = clahe.apply(l_channel)
    enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def gamma_correction(image, gamma=1.2):
    inv_gamma = 1.0 / max(gamma, 1e-6)
    table = np.array(
        [((index / 255.0) ** inv_gamma) * 255 for index in range(256)],
        dtype=np.uint8,
    )
    return cv2.LUT(image, table)


def unsharp_mask(image, sigma=1.0, strength=1.5):
    blurred = cv2.GaussianBlur(image, (0, 0), sigmaX=sigma, sigmaY=sigma)
    return cv2.addWeighted(image, 1.0 + strength, blurred, -strength, 0)


def apply_wiener_deconvolution(image, kernel_size=(5, 5)):
    if wiener is None:
        return None

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    restored_channels = [wiener(rgb_image[:, :, idx], kernel_size) for idx in range(3)]
    restored = cv2.merge(restored_channels)
    return cv2.convertScaleAbs(restored)


def blind_deconvolution_note():
    return "Research only: blind deconvolution needs PSF estimation and validation."


def save_image(output_path, image):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), image)


def main():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {IMAGE_PATH}")

    results = {
        "Original": img,
        "Gaussian Denoise": gaussian_filter(img),
        "Median Filter": median_filter(img),
        "NL Means Filter": nl_means_filter(img),
        "Bilateral Filter": bilateral_filter(img),
        "CLAHE": clahe_enhance(img),
        "Unsharp Mask": unsharp_mask(img),
    }

    wiener_result = apply_wiener_deconvolution(img)
    if wiener_result is not None:
        results["Wiener Deconvolution"] = wiener_result
    else:
        print("Skipping Wiener deconvolution because scipy is not installed.")

    print(blind_deconvolution_note())

    for title, image in results.items():
        show_result(title, image)


if __name__ == "__main__":
    main()
