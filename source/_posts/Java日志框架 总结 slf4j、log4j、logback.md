---
title: Java日志框架 总结 slf4j、log4j、logback
date: 2023-01-07 19:25:00
top: true
cover: true
toc: true
mathjax: false
categories: 后端
tags:
  - 后端
  - Java
---

@[TOC](目录)
# Java日志技术

## 1.日志的概念

### 1.1 日志文件种类

- 调试日志
- 系统日志

## 2.Java日志框架

### 2.1 为什么要使用日志框架

1. 软件复杂，设计的知识、内容、为题太多。
2. 小系统不需要使用日志框架, 使用别人的框架你就可以集中精力完成系统的业务逻辑。

### 2.2 流行的日志框架[日志门面技术]

> 日志门面技术,就是面向接口编程。多种日志框架无缝切换。[类似JDBC]

> 冷门：JCL是门面技术但也提供了实现，slf4j也提供了实现但是也不用。log4j是实现技术但也提供了门面API但是一般也不用 。

#### 2.2.1 日志门面

- JCL、slf4j

##### 日志门面的优点

- 1.面向接口编程,减少耦合 [通过导入不同的日志实现类,灵活切换框架,统一配置便于项目日志管理] 
- 2.统一的API，并隐藏了不同框架的底部的细节,隐藏了日志实现框架 的API。方便学习及使用。

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-sxkplitf-1630495502298)(/Users/admin/Documents/my-note/image-old/image-20200405110730005.png)\]](https://i-blog.csdnimg.cn/blog_migrate/ffdcc208016c1335dd38c61e3de408ee.png)




#### 2.2.2 日志实现

- JUL[jdk自带]、logback[spring默认]、log4j、log4j2[性能最好]

## 3. 日志框架从入门到不想入门

### 3.0 所有的配置文件

#### 3.0.1 JUL [核心是logManager以及Logger对象代码]

```properties
## RootLogger处理器（获取时设置）
handlers= java.util.logging.ConsoleHandler
## RootLogger处理器（打印日志时设置）
.handlers= RootLogger.java.util.logging.FileHandler
# RootLogger日志等级
.level= INFO

## TestLog日志处理器
TestLog.handlers= java.util.logging.FileHandler
# TestLog日志等级
TestLog.level= INFO
# 忽略父日志处理
TestLog.useParentHandlers=false

## 控制台处理器
# 输出日志级别
java.util.logging.ConsoleHandler.level = INFO
# 输出日志格式
java.util.logging.ConsoleHandler.formatter = java.util.logging.SimpleFormatter


## 文件处理器
# 输出日志级别
java.util.logging.FileHandler.level=INFO
# 输出日志格式
java.util.logging.FileHandler.formatter = java.util.logging.SimpleFormatter
# 输出日志文件路径
java.util.logging.FileHandler.pattern = D:\\TestLog.log
# 输出日志文件限制大小（50000字节）
java.util.logging.FileHandler.limit = 50000
# 输出日志文件限制个数
java.util.logging.FileHandler.count = 10
# 输出日志文件 是否是追加
java.util.logging.FileHandler.append=true
```

#### 3.0.2 Log4j[核心是配置文件以及Appender]

```properties
log4j.rootLogger=trace,console

# 自定义logger
log4j.logger.com.biturd = info, file
# 命名规范一般是包名,这个是自定义的
# 这个是继承rootLogger的 级别会覆盖,appender追加
log4j.logger.org.apache = error
# 日志灵活输出

log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m %n


log4j.appender.file = org.apache.log4j.FileAppender
log4j.appender.file.layout = org.apache.log4j.PatternLayout
log4j.appender.file.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.file.file = /logs/log4j.log
log4j.appender.file.encoding = UTF-8


log4j.appender.rollingFileAppender = org.apache.log4j.RollingFileAppender
log4j.appender.rollingFileAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.rollingFileAppender.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.rollingFileAppender.file = /logs/log4j.log
log4j.appender.rollingFileAppender.encoding = UTF-8
log4j.appender.rollingFileAppender.maxFileSize = 1MB
log4j.appender.rollingFileAppender.maxBackupIndex = 10

log4j.appender.dailyRollingFileAppender = org.apache.log4j.DailyRollingFileAppender
log4j.appender.dailyRollingFileAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.dailyRollingFileAppender.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.dailyRollingFileAppender.file = /logs/log4j.log
log4j.appender.dailyRollingFileAppender.encoding = UTF-8
log4j.appender.dailyRollingFileAppender.datePattern = '.'yyyy-MM-dd-HH-mm-ss

log4j.appender.dbAppender = org.apache.log4j.jdbc.JDBCAppender
log4j.appender.dbAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.dbAppender.driver = com.mysql.jdbc.Driver 
log4j.appender.dbAppender.url = jdbc:mysql:///test
# jdbc:mysql://localhost:3306/test
log4j.appender.dbAppender.user = root
log4j.appender.dbAppender.password = root
log4j.appender.dbAppender.sql = INSERT INTO LOGGING (log_date, log_level, location, message) VALUES ('%d{ISO8601}', '%-5p', '%C,%L', '%m')

```



### 3.1 JUL[实现框架]

```
两种方法输出日志
    logger.log(Level.INFO, "msg");  // 通用方法
    logger.info("123456"); // 专用方法  logger.[级别]("[信息]");
```

```
组件[非具体类]调用过程
- Application
	- Logger
		设置两个内容
		1. Level
		2. 日志消息内容
		- Handler
			指定输出路径[控制台、文件、网络]
			- Layouts[Formatters] (输出前进行格式化)
				- Filter[细粒度的日志拦截]
```

#### 日志级别控制

> 一共七个日志级别，通过值来控制,默认只输出默认取值比Logger.INFO高的。 如果手动设置Logger的级别那么就输出比手动设置的高的级别。

> Maven中的dependency如果是<scope>是test写在 main目录下面就会报错[导包找不到]

```Java
    @Test
    public void testQuick() throws Exception{
        Logger logger = Logger.getLogger("com.biturd.JULTest");  // 每一个日志记录器都需要有一个唯一标识
        logger.info("hello jul");
        logger.log(Level.INFO, "msg");

        String name = "123456";
        int a = 123456;
        logger.log(Level.INFO, "用户信息: 字符串{0}，数字{1}",new Object[]{name,a});
    }
```

```java
    public static final Level OFF = new Level("OFF",Integer.MAX_VALUE, defaultBundle);
    public static final Level SEVERE = new Level("SEVERE",1000, defaultBundle);
    public static final Level WARNING = new Level("WARNING", 900, defaultBundle);
    public static final Level INFO = new Level("INFO", 800, defaultBundle);
    public static final Level CONFIG = new Level("CONFIG", 700, defaultBundle);
    public static final Level FINE = new Level("FINE", 500, defaultBundle);
    public static final Level FINER = new Level("FINER", 400, defaultBundle);
    public static final Level FINEST = new Level("FINEST", 300, defaultBundle);	
	public static final Level ALL = new Level("ALL", Integer.MIN_VALUE, defaultBundle);
```

```java
    @Test   
    public void testLogLevel() throws Exception{
        Logger logger = Logger.getLogger("com.biturd.JULTest"); // 每一个日志记录器都需要有一个唯一标识 通常是全限定类名
        logger.severe("server");
        logger.warning("warning");
        logger.info("info");
        logger.config("config");
        logger.fine("fine");
        logger.finer("finer");
        logger.finest("finest");
    }
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/12c2d1462ad11b7366561dab71d82e54.png)

#### 底层的原理及自定义配置文件

```java
- logger
	- demandLogger
		- LogManager.getLogManager()
			-ensureLogManagerInitialized() [加载配置文件]            
            	- readConfiguration
  
    public void readConfiguration() throws IOException, SecurityException {
        checkPermission();

        // if a configuration class is specified, load it and use it.
        String cname = System.getProperty("java.util.logging.config.class");
        if (cname != null) {
            try {
                // Instantiate the named class.  It is its constructor's
                // responsibility to initialize the logging configuration, by
                // calling readConfiguration(InputStream) with a suitable stream.
                try {
                    Class<?> clz = ClassLoader.getSystemClassLoader().loadClass(cname);
                    clz.newInstance();
                    return;
                } catch (ClassNotFoundException ex) {
                    Class<?> clz = Thread.currentThread().getContextClassLoader().loadClass(cname);
                    clz.newInstance();
                    return;
                }
            } catch (Exception ex) {
                System.err.println("Logging configuration class \"" + cname + "\" failed");
                System.err.println("" + ex);
                // keep going and useful config file.
            }
        }

        String fname = System.getProperty("java.util.logging.config.file");
        if (fname == null) {
            fname = System.getProperty("java.home");
            if (fname == null) {
                throw new Error("Can't find java.home ??");
            }
            File f = new File(fname, "lib");
            f = new File(f, "logging.properties");
            fname = f.getCanonicalPath();
        }
        try (final InputStream in = new FileInputStream(fname)) {
            final BufferedInputStream bin = new BufferedInputStream(in);
            readConfiguration(bin);
        }
    }
    
 E:\Java\jre\lib\logging.properties   
 
 logManager是单例对象,所以前面后面所有的都是一个对象
 加载流肯定应用了。    
```



```java
    @Test
    public void testLogProperties() throws Exception{
        // 加载配置文件
        InputStream ins =  JULTest.class.getClassLoader().getResourceAsStream("logging.properties");
        // 创建logManager
        LogManager logManager = LogManager.getLogManager();
        // 通过logManager加载配置文件

		logManager.readConfiguration(ins);

        Logger logger = Logger.getLogger("com.biturd");
        
        logger.severe("server");
        logger.warning("warning");
        logger.info("info");
        logger.config("config");
        logger.fine("fine");
        logger.finer("finer");
        logger.finest("finest");

    }
```

#### 配置文件总览

```properties
## RootLogger处理器（获取时设置）
handlers= java.util.logging.ConsoleHandler
## RootLogger处理器（打印日志时设置）
.handlers= RootLogger.java.util.logging.FileHandler
# RootLogger日志等级
.level= INFO

## TestLog日志处理器
TestLog.handlers= java.util.logging.FileHandler
# TestLog日志等级
TestLog.level= INFO
# 忽略父日志处理
TestLog.useParentHandlers=false

## 控制台处理器
# 输出日志级别
java.util.logging.ConsoleHandler.level = INFO
# 输出日志格式
java.util.logging.ConsoleHandler.formatter = java.util.logging.SimpleFormatter


## 文件处理器
# 输出日志级别
java.util.logging.FileHandler.level=INFO
# 输出日志格式
java.util.logging.FileHandler.formatter = java.util.logging.SimpleFormatter
# 输出日志文件路径
java.util.logging.FileHandler.pattern = D:\\TestLog.log
# 输出日志文件限制大小（50000字节）
java.util.logging.FileHandler.limit = 50000
# 输出日志文件限制个数
java.util.logging.FileHandler.count = 10
# 输出日志文件 是否是追加
java.util.logging.FileHandler.append=true
```

### 3.2 Log4j[实现框架]

#### 0.代码示例

```java
    @Test
    public void QuickStartLog4j(){
        // 不使用配置文件 用默认的方式
//        BasicConfigurator.configure();
        // 获取日志记录器对象
        Logger logger = Logger.getLogger(log4jTest.class);
        // 日志记录输出
        logger.info("hello log4j");

        logger.fatal("造成系统崩溃的严重错误");   
        // 常用的
        logger.error("不会让系统停止的错误信息");
        logger.warn("可能发生错误警告信息");
        logger.info("运行信息,数据连接、网络连接、IO、操作等");
        logger.debug("调试信息,一般在开发中使用,记录程序变量参数传递信息等");

        logger.trace("追踪信息,记录程序所有的流程信息");
    }
```



#### 1.Log4j组件

- Loggers [日志记录器] 控制日志的输出级别与日志是否输出
- Appenders [输出端] 日志的输出方式
- Layout [日志格式化] 控制日志的输出格式

##### 1). Loggers日志记录器 [默认继承RootLogger]

> 早期叫Category,所以可以视为是Category类的别名

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/3d2db555bb5aab003ee4f2e1a79cf721.png)


##### 2). Appenders

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-d4FKTTiH-1630495502308)(/Users/admin/Documents/my-note/image-old/image-20200403092804928.png)\]](https://i-blog.csdnimg.cn/blog_migrate/16a5765528d3326532350a21b26ae3dd.png)


##### 3). Layouts

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-NuWbtfpo-1630495502310)(/Users/admin/Documents/my-note/image-old/image-20200403093159621.png)\]](https://i-blog.csdnimg.cn/blog_migrate/02a62fdeac5c03a6d19b680c86c59b04.png)


#### 2. 源码分析

```
- org.apache.log4j.logger
	- org.apache.log4j.logManager [读取配置信息]
	- 在Loader.getResource();读取配置文件
	- OptionConverter.selectAndConfigure();加载配置文件内部信息
		- 然后把配置信息都加到rootLogger上
		- configureRootCategory()
		- parseCategory()
			- parseCategory()解析信息 [StringTokenizer st = new StringTokenizer(value, ",");]
	
```

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-UCENH4ER-1630495502311)(/Users/admin/Documents/my-note/image-old/image-20200403115422584.png)\]](https://i-blog.csdnimg.cn/blog_migrate/49e20cfaaf1ffc113edaa811371a303a.png)

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/cc06a0480f86953765e9b517cc6f5b25.png)


>  ==不知道配置文件写什么就在这查==。<<学习框架方法论>>

> 除了这里还有就是ognl表达式 set方法

#### 3.其他

##### 3.1 Loglog: Log4j内置的日志的开关
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/16a9f64e327f284f101ef0ec5ec37bdc.png)


##### 3.2 Layout的使用

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-uUPANV7w-1630495502319)(/Users/admin/Documents/my-note/image-old/image-20200404204902538.png)\]](https://i-blog.csdnimg.cn/blog_migrate/147289f2e33891e96fe0d6efc63228c2.png)


通过ognl表达式来指定。

```properties
log4j.rootLogger=trace,console
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.layout=org.apache.log4j.PatternLayout

log4j.appender.console.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n

# %l == %c+%t+%F+%L
```

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/2ec10dd9f7b100ee1d0f564dd7f9bf2b.png)


##### 3.3 Appender的使用

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/9f702063b739d4ef771ace471fee6af0.png)


- Console
- File[两个子类,可以选择用父类或子类]
  - Rolling [按大小拆分]
  - DailyRolling [按时间拆分]

###### 3.3.1 File

> 需要指定一个输出文件

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-9LBENhsf-1630495502325)(/Users/admin/Documents/my-note/image-old/image-20200404210001421.png)\]](https://i-blog.csdnimg.cn/blog_migrate/a52b3671c9e17ac33130302672bf5b0d.png)


```properties
log4j.appender.file = org.apache.log4j.FileAppender
log4j.appender.file.layout = org.apache.log4j.PatternLayout
log4j.appender.file.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.file.file = /logs/log4j.log
log4j.appender.file.encoding = UTF-8
```

###### 3.3.2 Rolling

```properties
log4j.appender.rollingFileAppender = org.apache.log4j.RollingFileAppender
log4j.appender.rollingFileAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.rollingFileAppender.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.rollingFileAppender.file = /logs/log4j.log
log4j.appender.rollingFileAppender.encoding = UTF-8
log4j.appender.rollingFileAppender.maxFileSize = 1MB
log4j.appender.rollingFileAppender.maxBackupIndex = 10  
# [超过十个会覆盖久远的日志]
```

###### 3.3.3 DailyRolling

```properties
log4j.appender.dailyRollingFileAppender = org.apache.log4j.DailyRollingFileAppender
log4j.appender.dailyRollingFileAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.dailyRollingFileAppender.layout.conversionPattern = [%p]%r %l %d{yyyy-mm-dd HH:mm:ss.SSS} %m%n
#指定日志输出的位置[ognl表达式]
log4j.appender.dailyRollingFileAppender.file = /logs/log4j.log
log4j.appender.dailyRollingFileAppender.encoding = UTF-8
log4j.appender.dailyRollingFileAppender.datePattern = '.'yyyy-MM-dd-HH-mm-ss 
# [完全的，最合适的是按照天划分]
```

###### 3.3.4 ==JDBCAppender==

```properties
log4j.appender.dbAppender = org.apache.log4j.jdbc.JDBCAppender
log4j.appender.dbAppender.layout = org.apache.log4j.PatternLayout
log4j.appender.dbAppender.driver = com.mysql.jdbc.Driver 
log4j.appender.dbAppender.url = jdbc:mysql:///test
# jdbc:mysql://localhost:3306/test
log4j.appender.dbAppender.user = root
log4j.appender.dbAppender.password = root
log4j.appender.dbAppender.sql = INSERT INTO log(preject_name, create_date, log_level, category,file_name,thread_name,line,all_category, message) VALUES ('pro_name', '%d{yyyy-MM-dd HH:mm:ss}', '%p', '%c', '%F','%t', '%L' , '%l' ,'%m')
```

##### 3.4 自定义logger

```properties
log4j.logger.com.biturd = info, file
# 命名规范一般是包名,这个是自定义的
# 这个是继承rootLogger的 级别会覆盖,appender追加
log4j.logger.org.apache = error
# 日志灵活输出
```

默认是继承rootlogger的

- 实验前 

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-Skg5yDys-1630495502326)(/Users/admin/Documents/my-note/image-old/image-20200405082951614.png)\]](https://i-blog.csdnimg.cn/blog_migrate/5e8f07d11e5b97f7c6a0398131f7ed46.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-i55PYQ54-1630495502328)(/Users/admin/Documents/my-note/image-old/image-20200405083024130.png)\]](https://i-blog.csdnimg.cn/blog_migrate/3376842c0566e1dab643fe8056e030dd.png)


> 没有打印123456

- 实验后
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/445fd72464580d813b39ed3a09bcd130.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-1ECKDThc-1630495502333)(/Users/admin/Documents/my-note/image-old/image-20200405082824218.png)\]](https://i-blog.csdnimg.cn/blog_migrate/abcc3304395246ca6700b3fbbf51e4c9.png)


> 打印123456

可见log4j是==通过包名来判断如何使用自定义的日志记录器==

- 原理

日志打印logger对象通过包名与配置文件的多个自定义的logger对比，如果没有找到就用默认的rootlogger。

### 3.3 JCL[门面框架] [只支持这几种所以淘汰了]

> 门面框架出现背景： 初期小项目用jul-> 后期用log4j 需要切换框架，麻烦 

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-wzt2g6Pq-1630495502378)(/Users/admin/Documents/my-note/image-old/image-20200405083911433.png)\]](https://i-blog.csdnimg.cn/blog_migrate/ab0d3e6bf9ef644c99398053b755f57e.png)


```java
    @Test
    public void testQuickJCL(){
        Log log = LogFactory.getLog(JCLTest.class);
        log.info(123456);
    }
```

- 1.没有log4j依赖时，默认使用jul

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-G06jdQIr-1630495502382)(/Users/admin/Documents/my-note/image-old/image-20200405093515568.png)\]](https://i-blog.csdnimg.cn/blog_migrate/3293f90d587f9b5faa783b2ddc4997e2.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-syR2SHug-1630495502385)(/Users/admin/Documents/my-note/image-old/image-20200405093429447.png)\]](https://i-blog.csdnimg.cn/blog_migrate/2ae8fa3cab471fc09b37af632591965d.png)


- 有log4j依赖时，默认使用log4j

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-UEM2lObh-1630495502387)(/Users/admin/Documents/my-note/image-old/image-20200405093613785.png)\]](https://i-blog.csdnimg.cn/blog_migrate/cc1421e296b0da4b3e963267614e1953.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-UbPFndTo-1630495502388)(/Users/admin/Documents/my-note/image-old/image-20200405093843684.png)\]](https://i-blog.csdnimg.cn/blog_migrate/195d27205f6ca70d2abbc1207fd61dd6.png)


#### 3.3.1 原理

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-JEiU0OLG-1630495502390)(/Users/admin/Documents/my-note/image-old/image-20200405102418149.png)\]](https://i-blog.csdnimg.cn/blog_migrate/b615dc47c4ac099016513f889922571c.png)


```java
// 查找的log类的范围
private static final String[] classesToDiscover = {
            LOGGING_IMPL_LOG4J_LOGGER,
            "org.apache.commons.logging.impl.Jdk14Logger",
            "org.apache.commons.logging.impl.Jdk13LumberjackLogger",
            "org.apache.commons.logging.impl.SimpleLog"
    };
```

```java
// 查找log类的具体实现
for(int i=0; i<classesToDiscover.length && result == null; ++i) {
            result = createLogFromClass(classesToDiscover[i], logCategory, true);
        }
```

```java
// 利用反射技术根据名字字符串查找类
try {
                    c = Class.forName(logAdapterClassName, true, currentCL);
                } catch (ClassNotFoundException originalClassNotFoundException) {
    
// 如果找到了
                constructor = c.getConstructor(logConstructorSignature);
                Object o = constructor.newInstance(params);

                // Note that we do this test after trying to create an instance
                // [rather than testing Log.class.isAssignableFrom(c)] so that
                // we don't complain about Log hierarchy problems when the
                // adapter couldn't be instantiated anyway.
                if (o instanceof Log) {
                    logAdapterClass = c;
                    logAdapter = (Log) o;
                    break;
                }    
    
// 适配器将找到的log类的构造方法、以及log类的Name适配为实例属性。
        if (logAdapterClass != null && affectState) {
            // We've succeeded, so set instance fields
            this.logClassName   = logAdapterClassName;
            this.logConstructor = constructor;

            // Identify the <code>setLogFactory</code> method (if there is one)
            try {
                this.logMethod = logAdapterClass.getMethod("setLogFactory", logMethodSignature);
               .......
            }
	return logAdapter;

```

### 3.4 SLF4j[门面框架]

```
Note that SLF4J-enabling your library implies the addition of only a single mandatory dependency, namely slf4j-api.jar. If no binding is found on the class path, then SLF4J will default to a no-operation implementation.

slf4j意味着仅添加一个强制性依赖项，slf4j-api.jar。如果在类路径上没有找到绑定,他就默认无操作实现。[只是一套接口]
```

#### 3.4.1 原理：
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4c239587094bb261de0b55651e641450.png)


```java
// 如果有多个实现就打印，并使用第一个实现框架

 if (isAmbiguousStaticLoggerBinderPathSet(binderPathSet)) {
            Util.report("Class path contains multiple SLF4J bindings.");
            Iterator i$ = binderPathSet.iterator();

```

#### 3.4.2 日志桥接技术

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-UngUJ6DV-1630495502394)(/Users/admin/Documents/my-note/image-old/image-20200405232257770.png)\]](https://i-blog.csdnimg.cn/blog_migrate/0164b7232b6d79cb92ce3f46023f536f.png)


#### 3.4.3 [桥接技术]死循环的原因 [桥接不能和适配器同时出现(jar包)]

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-ekVHT1OV-1630495502395)(/Users/admin/Documents/my-note/image-old/image-20200405231826182.png)\]](https://i-blog.csdnimg.cn/blog_migrate/8cab1d572451f7dce6eb32e7002ff7dd.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-1W5SHKTY-1630495502398)(/Users/admin/Documents/my-note/image-old/image-20200405232029754.png)\]](https://i-blog.csdnimg.cn/blog_migrate/d3fd795439070d7dd97936d6f8af947b.png)


### 3.5 logback[实现框架]

https://www.cnblogs.com/gavincoder/p/10091757.html

#### 3.5.0 基础代码

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-8IOlcpJl-1630495502399)(/Users/admin/Documents/my-note/image-old/image-20200406071803831.png)\]](https://i-blog.csdnimg.cn/blog_migrate/4847baa5c4bdf916cfb6f2d59236a725.png)


![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-cjObYrM4-1630495502401)(/Users/admin/Documents/my-note/image-old/image-20200406071937720.png)\]](https://i-blog.csdnimg.cn/blog_migrate/cf3a606ef8afafc609be2fa84b144791.png)


依赖关系

```xml
    <dependency>
      <groupId>ch.qos.logback</groupId>
      <artifactId>logback-classic</artifactId>
      <version>1.2.3</version>
    </dependency>
    
    <!-- 只需要导入logback-classic就可以了,被依赖的会自动导入 -->
```

```xml
<?xml version="1.0" encoding="utf-8" ?>
<configuration debug="true">
    <property name="pattern" value="%d{HH:mm:ss.SSS} [%thread] [%-5level] %logger{36} - %msg%n"></property>
    <property name="log_back" value="/logs"></property>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <target>System.err</target>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
            <pattern>${pattern}</pattern>
        </encoder>
    </appender>

    <appender name="file" class="ch.qos.logback.core.FileAppender">
        <!-- 日志保存的位置 -->
        <file>${log_dir}/logback.log</file>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
            <pattern>${pattern}</pattern>
        </encoder>
    </appender>

    <appender name="htmlFile" class="ch.qos.logback.core.FileAppender">
        <file>${log_dir}/logback.html</file>
        <encoder class="ch.qos.logback.core.encoder.LayoutWrappingEncoder">
            <layout class="ch.qos.logback.classic.html.HTMLLayout">
                <pattern>%d{HH:mm:ss.SSS} [%thread] [%-5level] %logger{36} - %msg%n"</pattern>
            </layout>
        </encoder>
    </appender>

    <appender name="rollFile" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${log_dir}/logback.html</file>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
            <pattern>${pattern}</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${log_dir}/rolling.%d{yyyy-MM-dd}.log.gz</fileNamePattern>
            <maxFileSize>1MB</maxFileSize>
        </rollingPolicy>
    </appender>

    <root level="ALL">
        <appender-ref ref="console"></appender-ref>
    </root>
</configuration>
```



#### 3.5.1 三个模块

- logback-core: 其他两个模块的基础
- logback-classic: log4j的改良版本[ 完整实现了slf4j的api ]
- logback-access: 访问模块和servlet容器集成提供通过Http访问日志的功能

#### 3.5.2 高阶用法 [ 过滤器及异步日志、自定义logger ]

```xml
   <!-- 过滤器用法 -->
	<appender name="rollFile" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${log_dir}/logback.html</file>
        <encoder class="ch.qos.logback.classic.encoder.PatternLayoutEncoder">
            <pattern>${pattern}</pattern>
        </encoder>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>${log_dir}/rolling.%d{yyyy-MM-dd}.log.gz</fileNamePattern>
            <maxFileSize>1MB</maxFileSize>
        </rollingPolicy>
        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <level>ERROR</level>
            <onMatch>ACCEPT</onMatch>
            <onMisMatch>DENY</onMisMatch>
        </filter>
    </appender>

    <!-- 异步日志 -->
    <appender name="async" class="ch.qos.logback.classic.AsyncAppender">
        <!-- 指定一个具体的Appender -->
        <appender-ref ref="rollFile"/>
    </appender>

    <root level="ALL">
        <appender-ref ref="console"></appender-ref>
        <appender-ref ref="async"></appender-ref>
    </root>

    <!-- 自定义logger对象 additivity决定是否集成rootLogger -->
    <logger name="com.biturd" level="info" additivity="false">
        <appender-ref ref="console"/>
    </logger>
```

#### 3.5.3 log4j格式转logback [ pattern变了 ]
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e0a8282a8bcbdddae6ebc829ec675c6e.png)


#### 3.5.4 logback-access使用

> 使用这个来替换tomcat或jetty的日志
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/33e5fa9e5e78efe30f118b8005c0c178.png)


### 3.6 log4j2[实现框架]

> 虽然也是日志门面,但是习惯上还是用slf4j做日志门面

#### 1.log4j2日志门面用法[了解]

```xml
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-api</artifactId>
            <version>2.11.2</version>
        </dependency>
        <dependency>
            <groupId>org.apache.logging.log4j</groupId>
            <artifactId>log4j-core</artifactId>
            <version>2.11.2</version>
        </dependency>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--日志级别以及优先级排序: OFF > FATAL > ERROR > WARN > INFO > DEBUG > TRACE > ALL -->
<!--Configuration后面的status，这个用于设置log4j2自身内部的信息输出，可以不设置，当设置成trace时，你会看到log4j2内部各种详细输出-->
<!--monitorInterval：Log4j能够自动检测修改配置 文件和重新配置本身，设置间隔秒数-->
<configuration status="WARN" monitorInterval="30">
    <!--先定义所有的appender-->
    <appenders>
        <!--这个输出控制台的配置-->
        <console name="Console" target="SYSTEM_OUT">
            <!--输出日志的格式-->
            <PatternLayout pattern="[%d{HH:mm:ss:SSS}] [%p] - %l - %m%n"/>
        </console>
        <!--文件会打印出所有信息，这个log每次运行程序会自动清空，由append属性决定，这个也挺有用的，适合临时测试用-->
        <File name="log" fileName="log/test.log" append="false">
            <PatternLayout pattern="%d{HH:mm:ss.SSS} %-5level %class{36} %L %M - %msg%xEx%n"/>
        </File>
        <!-- 这个会打印出所有的info及以下级别的信息，每次大小超过size，则这size大小的日志会自动存入按年份-月份建立的文件夹下面并进行压缩，作为存档-->
        <RollingFile name="RollingFileInfo" fileName="${sys:user.home}/logs/info.log"
                     filePattern="${sys:user.home}/logs/$${date:yyyy-MM}/info-%d{yyyy-MM-dd}-%i.log">
            <!--控制台只输出level及以上级别的信息（onMatch），其他的直接拒绝（onMismatch）-->
            <ThresholdFilter level="info" onMatch="ACCEPT" onMismatch="DENY"/>
            <PatternLayout pattern="[%d{HH:mm:ss:SSS}] [%p] - %l - %m%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy/>
                <SizeBasedTriggeringPolicy size="100 MB"/>
            </Policies>
        </RollingFile>
        <RollingFile name="RollingFileWarn" fileName="${sys:user.home}/logs/warn.log"
                     filePattern="${sys:user.home}/logs/$${date:yyyy-MM}/warn-%d{yyyy-MM-dd}-%i.log">
            <ThresholdFilter level="warn" onMatch="ACCEPT" onMismatch="DENY"/>
            <PatternLayout pattern="[%d{HH:mm:ss:SSS}] [%p] - %l - %m%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy/>
                <SizeBasedTriggeringPolicy size="100 MB"/>
            </Policies>
            <!-- DefaultRolloverStrategy属性如不设置，则默认为最多同一文件夹下7个文件，这里设置了20 -->
            <DefaultRolloverStrategy max="20"/>
        </RollingFile>
        <RollingFile name="RollingFileError" fileName="${sys:user.home}/logs/error.log"
                     filePattern="${sys:user.home}/logs/$${date:yyyy-MM}/error-%d{yyyy-MM-dd}-%i.log">
            <ThresholdFilter level="error" onMatch="ACCEPT" onMismatch="DENY"/>
            <PatternLayout pattern="[%d{HH:mm:ss:SSS}] [%p] - %l - %m%n"/>
            <Policies>
                <TimeBasedTriggeringPolicy/>
                <SizeBasedTriggeringPolicy size="100 MB"/>
            </Policies>
        </RollingFile>
    </appenders>
    <!--然后定义logger，只有定义了logger并引入的appender，appender才会生效-->
    <loggers>
        <!--过滤掉spring和mybatis的一些无用的DEBUG信息-->
        <logger name="org.springframework" level="INFO"></logger>
        <logger name="org.mybatis" level="INFO"></logger>
        <root level="all">
            <appender-ref ref="Console"/>
            <appender-ref ref="RollingFileInfo"/>
            <appender-ref ref="RollingFileWarn"/>
            <appender-ref ref="RollingFileError"/>
        </root>
    </loggers>
</configuration>
```

#### 2. log4j2异步日志原理

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-iTd2Op1i-1630495502409)(/Users/admin/Documents/my-note/image-old/image-20200414122159052.png)\]](https://i-blog.csdnimg.cn/blog_migrate/912a18c7bf66b972a2e4cf5e7899d557.png)


两种方式

- AsyncAppender
- AsyncLogger

```xml
        <!-- log4j2异步日志需要提供的依赖 -->
		<dependency>
            <groupId>com.lmax</groupId>
            <artifactId>disruptor</artifactId>
            <version>3.3.4</version>
        </dependency>
```

![\[外链图片转存失败,源站可能有防盗链机制,建议将图片保存下来直接上传(img-zjEX5Jc3-1630495502415)(/Users/admin/Documents/my-note/image-old/image-20200414123002440.png)\]](https://i-blog.csdnimg.cn/blog_migrate/e7de474eb147917f80492f15f3a5a921.png)

### 3.7 SpringBoot中的应用

*虽然使用默认logback,可以不导入logback.xml文件，而是在application.xml里面也能设置日志框架的信息,但是一般比较粗略,所以还是需要特定的配置文件的*

> SpringBoot的Starters包含了一系列可以集成到应用里面的依赖包，你可以一站式集成Spring及其他技术，而不需要到处找示例代码和依赖包。如你想使用Spring JPA访问数据库，只要加入spring-boot-starter-data-jpa启动器依赖就能使用了。https://blog.csdn.net/qq_35974759/article/details/87168257
>
> Starters包含了许多项目中需要用到的依赖，它们能快速持续的运行，都是一系列得到支持的管理传递性依赖。

>  依赖关系: 指向谁就依赖谁

### 3.8 代码总结

#### JUL

```java
        Logger logger = Logger.getLogger("com.biturd.JULTest");  // 每一个日志记录器都需要有一个唯一标识
        logger.info("hello jul");
        logger.log(Level.INFO, "msg");
```

#### log4j

```java
        // 不使用配置文件 用默认的方式
//        BasicConfigurator.configure();
        LogLog.setInternalDebugging(true);
        // 获取日志记录器对象
        Logger logger = Logger.getLogger(log4jTest.class);
        // 日志记录输出
        logger.info("hello log4j");
        logger.fatal("造成系统崩溃的严重错误");
        // 常用的
        logger.error("不会让系统停止的错误信息");
        logger.warn("可能发生错误警告信息");
        logger.info("运行信息,数据连接、网络连接、IO、操作等");
        logger.debug("调试信息,一般在开发中使用,记录程序变量参数传递信息等");

        logger.trace("追踪信息,记录程序所有的流程信息");
```

#### JCL

```java
        Log log = LogFactory.getLog(JCLTest.class);
        log.info(123456);
```

#### slf4j[重点]

```java
public static final Logger LOGGER = LoggerFactory.getLogger(Slf4jTest.class);
    @Test
    public void testSlf4j(){
        LOGGER.warn("123456");
        LOGGER.error("123456");
    }
```

#### log4j2[自己的门面]

```java
    public static final Logger LOGGER = LogManager.getLogger(log4j2Test.class);

    @Test
    public void testQuick() throws Exception{
        LOGGER.fatal("fatal");
        LOGGER.error("error");
        LOGGER.warn("warn");
        LOGGER.info("info");
        LOGGER.debug("debug");
        LOGGER.trace("trace");
    }
```

#### slf4j的各种依赖关系[ 比较重要就再说一遍 ]

##### 1. slf4j-jdk
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/0829d39cb8294db8d13df0cec8f1c391.png)



##### 2.  slf4j-log4j
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/1c92915fb2e6dc2fa5d90cdd9b4370e1.png)



##### 3. slf4j-logback
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/452b41c1291929807a949985d517d66f.png)
#### 4.slf4j-log4j2
![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ec8f94cf7224eb550266b2a0d9e6c845.png)




#### 其他的比如桥接技术[ 详细的: https://blog.csdn.net/jeikerxiao/article/details/62423749 ]

使用slf4j统一各种日志
当项目是使用多种日志API时，可以统一适配到slf4j，然后通过slf4j适配底层实现。

中间使用slf4j进行统一项目中使用的多种日志框架的API，然后转发到slf4j,slf4j再底层用开发者想用的一个日志框架来进行日志系统的实现。从而达到了多种日志的统一实现。

- 旧日志API到slf4j的适配器

- slf4j到新日志实现的适配器

---

>  问题：目前的应用程序（application）中已经使用了以下的几种API来进行日志的编程：

1. commons-logging
2. jdk-loging
   现在想统一将日志的输出交给log4j1。

解决方法：[两种]

1. 将上面的日志系统全部转换到slf4j   [ 桥接技术 ]
   1. 移除commons-logging(可以不移除)，使用jcl-over-slf4j(桥接)将commons-logging的底层日志输出切换到sl4j.
   2. 使用jul-to-slf4j(桥接)，将jul的日志输出切换到slf4j.
2. 让slf4j选择log4j1作为底层日志输出
   1. 加入slf4j-api.jar
   2. 加入slf4j-log4j12.jar
   3. 加入log4j.jar

