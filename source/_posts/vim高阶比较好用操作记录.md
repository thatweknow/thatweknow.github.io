---
title: vim高阶比较好用操作记录
date: 2022-11-07 09:25:00
toc: true
mathjax: false
categories: 工具
tags:
  - 工具
---

## 1、普通操作
[c\d\y都同理，动作]
- dw删除到词尾、
- db删除到词首、
- dfa删除到向后查找到a的位置、
- dFa删除到向前差找到a的位置
- d/abc 删除到找到abc

## 2、标记使用
在 Vim 中，标记可以帮助您记住文本的位置。标记是在文本中设置的位置，可以使用单个字符作为名称进行标识。以下是在 Vim 中使用标记的一些常用命令：

- 设置标记: ma, mb, mc, … （将标记设置为a, b, c等等）
- 跳转到标记行首: 'a, 'b, 'c, … （跳转到标记a, b, c等等所在的行首位置）
- 跳转到标记: `a, … （跳转到标记a的位置）
- 查看所有标记: :marks （显示所有标记的列表）
- 删除标记: :delmarks a, :delmarks a b c ,（删除标记a，或删除多个标记） 删除所有标记: :delmarks!
- 删除从光标到标记：d`a   d'a【中间的行】   动作：d、c、y


在使用标记时，您可以将其用于定位文件中的重要位置，例如跳转到特定的行、函数、段落等。标记在 Vim 中非常有用，可以使您更有效地浏览和编辑文本。


## 3、操作'"[{包围的文本
diw:  d[操作]、i[范围]、w[操作对象]

其中，di( 表示“删除内部括号”，即删除圆括号内的所有文本。
da( 表示“删除包括括号”，即删除圆括号内的所有文本。

操作：
- y 复制文本
- c 修改文本
- d 删除文本
- v 选择文本
范围：
- i  内部的
- a 包括括号
- s 删除括号【vim-surround插件】
ysiw( 增加括号、	csw( cs([ 更改环绕
http://yyq123.github.io/learn-vim/learn-vim-plugin-surround.html
https://github.com/tpope/vim-surround

操作对象：
- w 词语
- p 段落
- W 词语包含空格
- [ ( { 各种括号
- ' " ` 各种引号
- <
- <tag>
- b\B	A block [(


## 4、多行操作

1、normal方式操作每一行
https://zhuanlan.zhihu.com/p/45433187

2、块选中操作每一行
ctrl+v  块选中后,  shift + i  后进入编辑模式，如下图,这时大家看到，只有第一行被修改了，下面的并没有插入//。这是没有关系的，这时只要按esc键两次,就可以发现刚选中的块都被修改了

3、multi-select插件
https://wklken.me/posts/2015/06/07/vim-plugin-multiplecursors.html


