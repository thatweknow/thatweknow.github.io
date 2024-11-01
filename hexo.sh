proxy

if ! [ -n "$1" ]; then
    echo "Usage: sh hexo.sh [s|d] [option:src_dir/src_file]"
    exit
fi
cur_dir=$(pwd)

cd /Users/admin/my-project/biturd-gp/
param=$1

if [ $param == "a" ]; then
    file_name=$2
    if [ $file_name == '.' ]; then
        file_name=$cur_dir
    fi

    if [ -d $file_name ]; then
        cp -R $file_name/* data/blog/
        echo "【INFO:】 move $file_name folder to md cache folder"
        exit
    else
        cp $cur_dir/$file_name data/blog/
        echo "【INFO:】 move $file_name file to md cache folder"
        exit    
    fi
fi

if [ "$param" == "c" ]; then
    rm -rf data/blog/*
    echo "【INFO:】 md cache folder has been cleaned"
    exit
fi


src_dir=$2
if [ -n "$src_dir" ]; then
    if [ $src_dir == '.' ]; then
        src_dira=$cur_dir
    fi

    if [ -d "$src_dir" ]; then
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
    exit
fi

git add .
git commit -m "update: add new posts or update posts"
git push

# sh start.sh s /Users/admin/my-project/biturd-gp/source/_posts
# sh start.sh d /Users/admin/my-project/biturd-gp/source/_posts