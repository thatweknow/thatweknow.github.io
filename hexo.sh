if ! [ -n "$1" ]; then
    echo "Usage: sh hexo.sh [s|d] [option:src_dir/src_file]"
    exit
fi

param=$1
cd /Users/admin/my-project/biturd-gp/
src_dir=$2
if [ -n "$src_dir" ]; then
    if [ "$src_dir" == '.' ]; then
       echo "【ERROR:】 src_dir is .， relative path is not supported"
       exit 1
    elif [ -d "$src_dir" ]; then
        cp -r "$src_dir"/* data/blog/
    else
        cp  $src_dir data/blog/
    fi
fi


python3 install_pic.py
python3 format_hexo_md.py
rm -rf data/blog/*

if [ "$param" == "d" ]; then
    hexo clean && hexo g && hexo d
else
    hexo clean && hexo g && hexo s
fi

# sh start.sh s /Users/admin/my-project/biturd-gp/source/_posts
# sh start.sh d /Users/admin/my-project/biturd-gp/source/_posts