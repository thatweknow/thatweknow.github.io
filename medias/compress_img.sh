find . -type f -iname '*.jpg' | while read img; do
    magick "$img" -quality 45 "$img"
done
