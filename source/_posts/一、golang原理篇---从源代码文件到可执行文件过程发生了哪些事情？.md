---
title: 一、golang原理篇---从源代码文件到可执行文件过程发生了哪些事情？.
date: 2024-10-07 19:25:00
top: true
cover: true
toc: true
mathjax: false
categories: 后端
tags:
  - 后端
  - Golang
  - 源码
---

主要过程：
- 前端编译
	1. 根据架构初始化不同的链接器Link结构体
	2. 根据一些参数  比如，go compile后用户输入的参数初始化Link结构体里面的一些字段
	3. 词法分析、语法分析 生成ast抽象语法树，类型检查。一些关键字转换为runtime里的函数
	4. 逃逸分析
- 后端编译
	1. 初始化生成中间代码的配置。ssaconfig
	2. 编译顶层函数，生成、优化ssa。
	3. 汇编代码生成机器码

@[TOC]( 目录)

## 1. compile包为编译器的入口

【本文的go代码为1.16，更高版本的可能文件差别很大】

https://github.com/golang/go，golang源代码中路径为

`src/cmd/compile`的包即为compile的全部代码，承担了将golang从.go文件编译成为二进制可执行文件的全部过程。

`src/cmd/compile/main.go`即为编译器程序的入口文件。

```go
func main() {
	// disable timestamps for reproducible output
	log.SetFlags(0)
	log.SetPrefix("compile: ")
	// objabi.GOARCH获取硬件平台，然后根据硬件平台选择不同的archInit初始函数
	archInit, ok := archInits[objabi.GOARCH]
	if !ok {
		fmt.Fprintf(os.Stderr, "compile: unknown architecture %q\n", objabi.GOARCH)
		os.Exit(2)
	}
	// 这个函数是根据硬件平台进行编译的全过程
	gc.Main(archInit)
	gc.Exit(0)
}
```

## 2. 词法、语法分析

`lines := parseFiles(flag.Args())`对输入的文件进行词法与语法分析得到对应的抽象语法树。

```
cmd/compile/main.go:main()->
	gc.Main(archInit)
  cmd/compile/internal/gc/main.go:Main(archInit func(*Arch))->
    lines := parseFiles(flag.Args())
    cmd/compile/internal/gc/noder.go:parseFiles()->
			syntax.Parse(base, f, p.error, p.pragma, syntax.CheckBranches)
      cmd/compile/internal/syntax/syntax.go:Parse(base *PosBase, src io.Reader.......)->
      	p.fileOrNil()
      	cmd/compile/internal/syntax/parser.go:(p *parser) fileOrNil() *File ->
```

### 2.1 文法分析

`cmd/compile/internal/syntax/parser.go:func (p *parser) fileOrNil() *File `是整个文法分析的过程。这个过程中是夹杂着词法分析的。

```go
SourceFile = PackageClause ";" { ImportDecl ";" } { TopLevelDecl ";" } 
```

每个 Go 源代码文件最终都会被解析成一个独立的抽象语法树，所以语法树最顶层的结构或者开始符号都是 SourceFile
每一个文件都包含一个 package 的定义以及可选的 import 声明和其他的顶层声明（TopLevelDecl）
每一个 SourceFile 在编译器中都对应一个` cmd/compile/internal/syntax.File` 结构体

这个过程的代码中，`p.next() got() want()`都是词法分析的过程。

### 2.2 词法分析

Go 语言的词法解析是通过 `src/cmd/compile/internal/syntax/scanner.go` 文件中的 `cmd/compile/internal/syntax.scanner` 结构体实现的，这个结构体会持有当前扫描的数据源文件、启用的模式和当前被扫描到的 Token。

`parser结构体就是p既是语法解析器，又是词法解析器【结构体内嵌】,p.next()惰性加载进行词法分析为token作为语法分析的输入。`

`src/cmd/compile/internal/syntax/tokens.go` 文件中定义了 Go 语言中支持的全部 Token 类型, 通过next()方法进行判断。s.next()又调用了s.nextch()获取文件中最近的未被解析的字符，然后根据当前字符的不同执行不同的 case。

在 for 循环中不断获取最新的字符，将字符通过` cmd/compile/internal/syntax.source.nextch` 方法追加到 `cmd/compile/internal/syntax.scanner` 持有的缓冲区中。



## 3. 类型检查
### 3.1 静态、动态类型
- 静态类型检查是基于对源代码的分析来确定运行程序类型安全的过程，如果我们的代码能够通过静态类型检查，那么当前程序在一定程度上可以满足类型安全的要求，它能够减少程序在运行时的类型检查，也可以被看作是一种代码优化的方式。

> 作为一个开发者来说，静态类型检查能够帮助我们在编译期间发现程序中出现的类型错误，一些动态类型的编程语言都会有社区提供的工具为这些编程语言加入静态类型检查，例如 JavaScript 的 [Flow](https://flow.org/)[4](https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-typecheck/#fn:4)，这些工具能够在编译期间发现代码中的类型错误。
>
> 相信很多读者也都听过『动态类型一时爽，代码重构火葬场』，使用 Python、Ruby 等编程语言的开发者一定对这句话深有体会，静态类型为代码在编译期间提供了约束，编译器能够在编译期间约束变量的类型。
>
> 静态类型检查在重构时能够帮助我们节省大量时间并避免遗漏，但是如果编程语言仅支持动态类型检查，那么就需要写大量的单元测试保证重构不会出现类型错误。当然这里并不是说测试不重要，我们写的**任何代码都应该有良好的测试**，这与语言没有太多的关系。

- 动态类型检查是在运行时确定程序类型安全的过程，它需要编程语言在编译时为所有的对象加入类型标签等信息，运行时可以使用这些存储的类型信息来实现动态派发、向下转型、反射以及其他特性。动态类型检查能为工程师提供更多的操作空间，让我们能在运行时获取一些类型相关的上下文并根据对象的类型完成一些动态操作。

> 只使用动态类型检查的编程语言叫做动态类型编程语言，常见的动态类型编程语言就包括 JavaScript、Ruby 和 PHP，虽然这些编程语言在使用上非常灵活也不需要经过编译，但是有问题的代码不会因为更加灵活就会减少错误，该出错时仍然会出错，它们在提高灵活性的同时，也提高了对工程师的要求。

- 静态类型检查和动态类型检查不是完全冲突和对立的，很多编程语言都会同时使用两种类型检查，例如：Java 不仅在编译期间提前检查类型发现类型错误，还为对象添加了类型信息，在运行时使用反射根据对象的类型动态地执行方法增强灵活性并减少冗余代码。

### 3.2 go语言

Go 语言的编译器不仅使用静态类型检查来保证程序运行的类型安全，还会在编程期间引入类型信息，让工程师能够使用反射来判断参数和变量的类型。当我们想要将 `interface{}` 转换成具体类型时会进行动态类型检查，如果无法发生转换就会发生程序崩溃。


类型检查是 Go 语言编译的第二个阶段，在词法和语法分析之后我们得到了每个文件对应的抽象语法树，随后的类型检查会遍历抽象语法树中的节点，对每个节点的类型进行检验，找出其中存在的语法错误，在这个过程中也可能会对抽象语法树进行改写，这不仅能够去除一些不会被执行的代码、对代码进行优化以提高执行效率，而且也会修改 `make`、`new` 等关键字对应节点的操作类型。

`make` 和 `new` 这些内置函数其实并不会直接对应某些函数的实现，它们会在编译期间被转换成真正存在的其他函数。

## 4. 中间代码生成

词法与语法分析以及类型检查两个部分都属于编译器前端，它们负责对源代码进行分析并检查其中存在的词法和语法错误，经过这两个阶段生成的抽象语法树已经不存在语法错误了。

而中间代码生成则属于编译器的后端工作。


为什么需要中间代码：

编译器面对的复杂场景，很多编译器需要将源代码翻译成多种机器码，直接翻译高级编程语言相对比较困难。将编程语言到机器码的过程拆成中间代码生成和机器码生成两个简单步骤可以简化该问题，中间代码是一种更接近机器语言的表示形式，对中间代码的优化和分析相比直接分析高级编程语言更容易。

Go 语言编译器的中间代码具有静态单赋值（SSA）的特性，一个变量只会被赋值一次，进而优化执行的步骤。

这些用于遍历抽象语法树的函数会将一些关键字和内建函数转换成函数调用，
例如： 上述函数会将 panic、recover 两个内建函数转换成 runtime.gopanic 和 runtime.gorecover 两个真正运行时函数，
而关键字 new 也会被转换成调用 runtime.newobject 函数。

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-g5F57sq4-1641023703277)(img/2019-02-05-golang-keyword-and-builtin-mapping.png)\]](https://i-blog.csdnimg.cn/blog_migrate/4c37fa8c0c037a4b09d1d629ff7390f4.png)


上图是从关键字或内建函数到运行时函数的映射，其中涉及 Channel、哈希、make、new 关键字以及控制流中的关键字 select 等。
转换后的全部函数都属于运行时包，我们能在 src/cmd/compile/internal/gc/builtin/runtime.go 文件中找到函数对应的签名和定义。

```go
func makemap64(mapType *byte, hint int64, mapbuf *any) (hmap map[any]any)
func makemap(mapType *byte, hint int, mapbuf *any) (hmap map[any]any)
func makemap_small() (hmap map[any]any)
func mapaccess1(mapType *byte, hmap map[any]any, key *any) (val *any)
...
func makechan64(chanType *byte, size int64) (hchan chan any)
func makechan(chanType *byte, size int) (hchan chan any)
...
```

这里的定义只是让 Go 语言完成编译，它们的实现都在另一个 [`runtime`](https://github.com/golang/go/tree/master/src/runtime) 包中。简单总结一下，编译器会将 Go 语言关键字转换成运行时包中的函数，也就是说关键字和内置函数的功能是由编译器和运行时共同完成的。



遍历节点时几个 Channel 操作是如何转换成运行时对应方法的，首先介绍向 Channel 发送消息或者从 Channel 接收消息两个操作，编译器会分别使用 `OSEND` 和 `ORECV` 表示发送和接收消息两个操作，在 [`cmd/compile/internal/gc.walkexpr`](https://draveness.me/golang/tree/cmd/compile/internal/gc.walkexpr) 函数中会根据节点类型的不同进入不同的分支：

```go
func walkexpr(n *Node, init *Nodes) *Node {
	...
	case OSEND:
		n1 := n.Right
		n1 = assignconv(n1, n.Left.Type.Elem(), "chan send")
		n1 = walkexpr(n1, init)
		n1 = nod(OADDR, n1, nil)
		n = mkcall1(chanfn("chansend1", 2, n.Left.Type), nil, init, n.Left, n1)
	...
}
```

当遇到 OSEND 操作时，会使用 cmd/compile/internal/gc.mkcall1 创建一个操作为 OCALL 的节点，这个节点包含当前调用的函数 runtime.chansend1 和参数，新的 OCALL 节点会替换当前的 OSEND 节点，这就完成了对 OSEND 子树的改写。

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-tmGnS3zD-1641023703278)(img/2019-12-23-15771129929846-golang-ocall-node.png)\]](https://i-blog.csdnimg.cn/blog_migrate/54d5a5a1811e7f73fe3d30263d1afaa2.png)




首先，从 AST 到 SSA 的转化过程中，编译器会生成将函数调用的参数放到栈上的中间代码，处理参数之后才会生成一条运行函数的命令 ssa.OpStaticCall：[cmd/compile/internal/obj.LSym，表示该方法已经注册到运行时包中]

1. 当使用 defer 关键字时，插入 runtime.deferproc 函数；
2. 当使用 go 关键字时，插入 runtime.newproc 函数符号；
3. 在遇到其他情况时会插入表示普通函数对应的符号；

cmd/compile/internal/gc/ssa.go 这个拥有将近 7000 行代码的文件包含用于处理不同节点的各种方法，编译器会根据节点类型的不同在一个巨型 switch 语句处理不同的情况，这也是我们在编译器这种独特的场景下才能看到的现象。







中间代码的生成过程是从 AST 抽象语法树到 SSA 中间代码的转换过程，在这期间会对语法树中的关键字再进行改写，改写后的语法树会经过多轮处理转变成最后的 SSA 中间代码，相关代码中包括了大量 switch 语句、复杂的函数和调用栈，阅读和分析起来也非常困难。

很多 Go 语言中的关键字和内置函数都是在这个阶段被转换成运行时包中方法的，作者在后面的章节会从具体的语言关键字和内置函数的角度介绍一些数据结构和内置函数的实现。





## 5. 机器码生成

机器码的生成在 Go 的编译器中主要由两部分协同工作，其中一部分是负责 SSA 中间代码降级和根据目标架构进行特定处理的 [`cmd/compile/internal/ssa`](https://github.com/golang/go/tree/master/src/cmd/compile/internal/ssa) 包，另一部分是负责生成机器码的 [`cmd/internal/obj`](https://github.com/golang/go/tree/master/src/cmd/internal/obj)[4](https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-machinecode/#fn:4)：

- [`cmd/compile/internal/ssa`](https://github.com/golang/go/tree/master/src/cmd/compile/internal/ssa) 主要负责对 SSA 中间代码进行降级、执行架构特定的优化和重写并生成 [`cmd/compile/internal/obj.Prog`](https://draveness.me/golang/tree/cmd/compile/internal/obj.Prog) 指令；
- [`cmd/internal/obj`](https://github.com/golang/go/tree/master/src/cmd/internal/obj) 作为汇编器会将这些指令转换成机器码完成这次编译；

SSA 降级 

SSA 降级是在中间代码生成的过程中完成的，其中将近 50 轮处理的过程中，`lower` 以及后面的阶段都属于 SSA 降级这一过程，这么多轮的处理会将 SSA 转换成机器特定的操作：

```go
var passes = [...]pass{
	...
	{name: "lower", fn: lower, required: true},
	{name: "lowered deadcode for cse", fn: deadcode}, // deadcode immediately before CSE avoids CSE making dead values live again
	{name: "lowered cse", fn: cse},
	...
	{name: "trim", fn: trim}, // remove empty blocks
}
```

SSA 降级执行的第一个阶段就是 `lower`，该阶段的入口方法是 [`cmd/compile/internal/ssa.lower`](https://draveness.me/golang/tree/cmd/compile/internal/ssa.lower)函数，它会将 SSA 的中间代码转换成机器特定的指令：

```go
func lower(f *Func) {
	applyRewrite(f, f.Config.lowerBlock, f.Config.lowerValue)
}
```

向 [`cmd/compile/internal/ssa.applyRewrite`](https://draveness.me/golang/tree/cmd/compile/internal/ssa.applyRewrite) 传入的两个函数 `lowerBlock` 和 `lowerValue` 是在[中间代码生成](https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-ir-ssa/)阶段初始化 SSA 配置时确定的，这两个函数会分别转换函数中的代码块和代码块中的值。

假设目标机器使用 x86 的架构，最终会调用 [`cmd/compile/internal/ssa.rewriteBlock386`](https://draveness.me/golang/tree/cmd/compile/internal/ssa.rewriteBlock386) 和 [`cmd/compile/internal/ssa.rewriteValue386`](https://draveness.me/golang/tree/cmd/compile/internal/ssa.rewriteValue386) 两个函数，这两个函数是两个巨大的 switch 语句，前者总共有 2000 多行，后者将近 700 行，用于处理 x86 架构重写的函数总共有将近 30000 行代码，你能在 [`cmd/compile/internal/ssa/rewrite386.go`](https://github.com/golang/go/blob/master/src/cmd/compile/internal/ssa/rewrite386.go) 这里找到文件的全部内容，我们只节选其中的一段展示一下：

```go
func rewriteValue386(v *Value) bool {
	switch v.Op {
	case Op386ADCL:
		return rewriteValue386_Op386ADCL_0(v)
	case Op386ADDL:
		return rewriteValue386_Op386ADDL_0(v) || rewriteValue386_Op386ADDL_10(v) || rewriteValue386_Op386ADDL_20(v)
	...
	}
}

func rewriteValue386_Op386ADCL_0(v *Value) bool {
	// match: (ADCL x (MOVLconst [c]) f)
	// cond:
	// result: (ADCLconst [c] x f)
	for {
		_ = v.Args[2]
		x := v.Args[0]
		v_1 := v.Args[1]
		if v_1.Op != Op386MOVLconst {
			break
		}
		c := v_1.AuxInt
		f := v.Args[2]
		v.reset(Op386ADCLconst)
		v.AuxInt = c
		v.AddArg(x)
		v.AddArg(f)
		return true
	}
	...
}
```

重写的过程会将通用的 SSA 中间代码转换成目标架构特定的指令，上述的 `rewriteValue386_Op386ADCL_0` 函数会使用 `ADCLconst` 替换 `ADCL` 和 `MOVLconst` 两条指令，它能通过对指令的压缩和优化减少在目标硬件上执行所需要的时间和资源。




## 6. 汇编学习

```
go tool compile -S hello.go
go tool objdump
```

`go build -work -debug-actiongraph=graph.json print.go// -n 参数展示命令不执行  -x  展示执行的命令 -work 保留中间目录 `

在这个过程中compile调用的就是 cmd/compile。
```
[
   {
      "执行过程": "编译过程从下往上，从最后一个阶段往第一个阶段合并。",
      "ID": 0,
      "Mode": "link-install",
      "Package": "command-line-arguments",
      "Deps": [
         1
      ],
      "Objdir": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/",
      "Target": "print",
      "Priority": 36,
      "Built": "print",
      "BuildID": "s3kSPuGqMFL1ltXka1-1/7T8ELBT1aC0tc7iktmm4/zG8NbUygi2kJFAzeDqMj/EQ04B5akVd2353iztOUr",
      "TimeReady": "2021-11-13T22:49:46.10052+08:00",
      "TimeStart": "2021-11-13T22:49:46.100523+08:00",
      "TimeDone": "2021-11-13T22:49:46.100701+08:00",
      "Cmd": null
   },
   {
      "ID": 1,
      "Mode": "link",
      "Package": "command-line-arguments",
      "Deps": [
         2,
       .......
         34
      ],
      "Objdir": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/",
      "Target": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/exe/a.out",
      "Priority": 35,
      "Built": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/exe/a.out",
      "ActionID": "s3kSPuGqMFL1ltXka1-1",
      "BuildID": "s3kSPuGqMFL1ltXka1-1/7T8ELBT1aC0tc7iktmm4/zG8NbUygi2kJFAzeDqMj/EQ04B5akVd2353iztOUr",
      "TimeReady": "2021-11-13T22:49:45.98116+08:00",
      "TimeStart": "2021-11-13T22:49:45.981173+08:00",
      "TimeDone": "2021-11-13T22:49:46.10052+08:00",
      "Cmd": [
         "/Users/admin/biturd/code-knowledge/源码学习/Go/go/pkg/tool/darwin_arm64/link -o /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/exe/a.out -importcfg /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/importcfg.link -buildmode=exe -buildid=s3kSPuGqMFL1ltXka1-1/7T8ELBT1aC0tc7iktmm4/zG8NbUygi2kJFAzeDqMj/s3kSPuGqMFL1ltXka1-1 -extld=clang /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/_pkg_.a"
      ],
      "CmdReal": 99474959,
      "CmdUser": 74461000,
      "CmdSys": 11050000
   },
   {
      "ID": 2,
      "Mode": "build",
      "Package": "command-line-arguments",
      "Deps": [
         3,
         4,
         5,
         35
      ],
      "Objdir": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/",
      "Priority": 34,
      "NeedBuild": true,
      "ActionID": "7T8ELBT1aC0tc7iktmm4",
      "BuildID": "7T8ELBT1aC0tc7iktmm4/zG8NbUygi2kJFAzeDqMj",
      "TimeReady": "2021-11-13T22:49:45.964123+08:00",
      "TimeStart": "2021-11-13T22:49:45.964128+08:00",
      "TimeDone": "2021-11-13T22:49:45.981158+08:00",
      "Cmd": [
         "/Users/admin/biturd/code-knowledge/源码学习/Go/go/pkg/tool/darwin_arm64/compile -o /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/_pkg_.a -trimpath \"/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001=\u003e\" -shared -p main -lang=go1.16 -complete -buildid 7T8ELBT1aC0tc7iktmm4/7T8ELBT1aC0tc7iktmm4 -goversion go1.16.9 -D _/Users/admin/biturd/code-knowledge/源码学习/Go/go/biturd/print -importcfg /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/importcfg -pack /Users/admin/biturd/code-knowledge/源码学习/Go/go/biturd/print/print.go /var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b001/_gomod_.go"
      ],
      "CmdReal": 13654375,
      "CmdUser": 4983000,
      "CmdSys": 4563000
   },
   {
      "ID": 3,
      "Mode": "build",
      "Package": "fmt",
      "Deps": [
         6,
         .........
         14
      ],
      "Objdir": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b002/",
      "Priority": 32,
      "NeedBuild": true,
      "ActionID": "k_-3MKKPQcoJhVBcf-tD",
      "BuildID": "k_-3MKKPQcoJhVBcf-tD/VyKAvsHRPs5gK-4oxWx_",
      "TimeReady": "2021-11-13T22:49:45.963446+08:00",
      "TimeStart": "2021-11-13T22:49:45.963451+08:00",
      "TimeDone": "2021-11-13T22:49:45.964121+08:00",
      "Cmd": null
   },
   ........
   	{
		"ID": 35,
		"Mode": "nop",
		"Package": "",
		"Deps": [
			3,
			......
			34
		],
		"Priority": 33,
		"TimeReady": "2021-11-13T22:49:45.964121+08:00",
		"TimeStart": "2021-11-13T22:49:45.964123+08:00",
		"TimeDone": "2021-11-13T22:49:45.964123+08:00",
		"Cmd": null
	},
	{
		"ID": 36,
		"Mode": "built-in package",
		"Package": "unsafe",
		"Objdir": "/var/folders/57/8f4zkqd54qn4f8c_btvcs9zc0000gn/T/go-build1635635154/b006/",
		"NeedBuild": true,
		"TimeReady": "2021-11-13T22:49:45.915029+08:00",
		"TimeStart": "2021-11-13T22:49:45.915053+08:00",
		"TimeDone": "2021-11-13T22:49:45.915053+08:00",
		"Cmd": null
	}
]
```




参考链接：
https://draveness.me/golang/docs/part1-prerequisite/ch02-compile/golang-compile-intro/
