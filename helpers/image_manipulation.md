# Prepare images for web

1. select images and copy 'em all to a directory
1. resize to image size (700x525)
2. add watermark
3. resize watermarked images to thumbnail size (150x100)

```
mkdir ~/Desktop/ig5_selected_images
mkdir -p ~/Desktop/ig5_web_images/images
mkdir -p ~/Desktop/ig5_web_images/thumbnails
# Resize all JPGs in ~/Desktop/ig5_selected_images/ to 700x525.
mogrify -path ~/Desktop/ig5_web_images/images -format jpg -resize 700x525 ~/Desktop/ig5_selected_images/*
# Add watermark to resized images.
python3 helpers/add_watermark_to_images.py -p $HOME/Desktop/ig5_web_images/images
# Resize watermarked images to thumbnails.
mogrify -path ~/Desktop/ig5_web_images/thumbnails -format jpg -resize 150x100 ~/Desktop/ig5_web_images/images/*
```

Used `mogrify` commands follow the pattern

```
mogrify -path <output_dir> -format jpg -resize <width>x<height> <source_dir>
```


## Dependencies

`mogrify` and `composite` (used by `add_watermark_to_images.py`) are part of
`ImageMagick` package. Use `apt install -y build-essential imagemagick` or
google how to install it if that doesn't work.
