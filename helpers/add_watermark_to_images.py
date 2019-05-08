import argparse
import os
import subprocess


here = os.path.dirname(os.path.abspath(__file__))
watermark_image = os.path.join(here, "watermark_leica.png")


def main(photos_dir: str):
    """
    Apply watermark to all images in `photos_dir`. Swap space with underscore
    in image names.
    """
    for img_name in sorted(os.listdir(photos_dir)):
        if " " in img_name:
            new_img_name = img_name.replace(" ", "_")
            new_image_path = os.path.join(photos_dir, new_img_name)
            old_image_path = os.path.join(photos_dir, img_name)
            os.rename(old_image_path, new_image_path)
            img_name = new_img_name

        img_path = os.path.join(photos_dir, img_name)
        command = (
            "composite -gravity SouthEast -quality 100 "
            f"( {watermark_image} -resize 20% ) {img_path} {img_path}"
        )
        subprocess.check_output(command.split())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--photos-dir", required=True, help="Photos dir absolute path"
    )
    args = parser.parse_args()
    main(args.photos_dir)
