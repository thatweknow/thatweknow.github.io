---
title: wrk压测工具使用
date: 2022-09-07 09:25:00
top: true
cover: true
toc: true
mathjax: false
categories: 性能优化
tags:
  - 压测
  - 性能优化
---

## 1、wrk命令行使用
```
Usage: wrk <options> <url>
  Options:
    -c, --connections <N>  Connections to keep open  // 连接数量、并发数量
    -d, --duration    <T>  Duration of test // 持续时间
    -t, --threads     <N>  Number of threads to use // 线程数量

    -s, --script      <S>  Load Lua script file  // 运行、lua脚本的位置
    -H, --header      <H>  Add header to request   // 添加请求头
        --latency          Print latency statistics  // 延时
        --timeout     <T>  Socket/request timeout // 超时的时间
    -v, --version          Print version details

  Numeric arguments may include a SI unit (1k, 1M, 1G)   // 数字单位
  Time arguments may include a time unit (2s, 2m, 2h) // 时间单位
```

wrk -c 30 -d 5s -t 10 --latency --timeout 2s http://baidu.com
以30个连接 压测5s用10个线程  ，超时设置为2s，打印耗时分布


```
> wrk -t4 -c30 -d30s --latency -s ./wrk.lua  http://localhost:8082/v1/gen
Running 30s test @ http://localhost:8082/v1/gen

  4 threads and 30 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    71.19ms  223.75ms   1.89s    93.06%
    Req/Sec   732.64    764.31     2.43k    77.51%
  Latency Distribution
     50%    4.61ms
     75%   13.88ms
     90%  140.69ms
     99%    1.18s 
  36497 requests in 30.04s, 7.87MB read
  Socket errors: connect 0, read 0, write 0, timeout 116
Requests/sec:   1215.05
Transfer/sec:    268.17KB
```

## 2、wrk 的lua脚本编写
其他的内置变量：https://www.cnblogs.com/paul8339/p/6283279.html
官方示例脚本：https://github.com/wg/wrk/tree/master/scripts

```
-- type: story-uimage,timestamp: 1666085563746, signature: VB64XLKEZ8OG1W7T:f5a440d2ceb8e8f7b6d4f1753db39c7b
-- https://www.escapelife.site/posts/4b014d0b.html
-- # 实现上传文件测试与json类似
-- # 同样是设置wrk.body和wrk.headers的值, 只是body较麻烦一些
--  https://www.runoob.com/lua/lua-basic-syntax.html

-- wrk -t8 -c10000 -d60s --latency -s ./wrk.lua  http://localhost:8082/v1/s3/url/signature
-- go tool pprof -http :8090 http://localhost:8082/debug/pprof/heap

-- genObject
params = {
    ["timestamp"] = "1666256428050",
    ["type"]="test-type"
}


-- getSignature
-- params = {
--     ["timestamp"] = "1666181475552",
--     ["signature"] = "test-signature",
-- }

-- 1、拼装form-data
form = ""
for key, value in pairs(params) do
    form = form .. "------WebKitFormBoundaryX3bY6PBMcxB1vCan\r\n"
    form = form .. "Content-Disposition: form-data; name="" .. key .. ""\r\n\r\n"
    form = form .. value .. "\r\n"
end
form = form .. "------WebKitFormBoundaryX3bY6PBMcxB1vCan--"

wrk.method = "POST"
wrk.headers["Content-Type"] = "multipart/form-data;boundary=------WebKitFormBoundaryX3bY6PBMcxB1vCan"
wrk.body = form

--curl -H 'BaseUrlModule: ossmanager' -H 'Host: clotho-kr.spatio.inc' -H 'User-Agent: okhttp/4.8.0' -H 'ApiName: /ossmanager/image/pub/s3/gen' -H 'Cookie: JSESSIONID={ogtydvjtsdbnmevxnwu}1b214bda2934cf3cb3ae15317be757bae4' -H 'X-Spatio-Timezone: +0800' -H 'X-Spatio-Language: zh-CN' -H 'X-Spatio-Region: kr' -H 'X-Spatio-Timestamp: 1666251461505' -H 'tp: 1666251461506' -H 'sk: 51733C934F95818E0CCDAAAB47ACD461' -H 'once: 8fT91P' -H 'Content-Type: application/json' --data-binary '{"tok":"Da1SR6uR7m0FZPaoHLW23O6BIqLf-lgpD2a2HXD06SXxy_bJpLGX1JsjuWqGRzDOXVpTkEMAnfLJ-LaOmREKiS76S_TBWZeJTXoiJhtCmEVhmfZBxXeE-qZqZ57ek0GblA03e8taLY4l9yQGFcRCCVi72d6BUl24pUPLkxK1TLlRRtm2owt9oe2gtNV5MA0pg4EWBwctP3hFtoDiCptJCw"}' --compressed 'http://clotho-kr.spatio.inc/ossmanager/image/pub/s3/gen?=&uv=1.0.0&net_type=wifi&uev=1&api_version=100000&distribution=default&mobile_model=M2012K11AC&pkg=1&platform=1&cv=1.0.0.176&appid=localside&uq_id=0502e89e0323fa642d4ae8929abf1615371d&request_id=localside_MMPP10101010101000000000_1666251461505&brand=Redmi'


-- 2、x-www-form
-- wrk.body = "foo=bar&baz=quux"
-- wrk.headers["Content-Type"] = "application/x-www-form-urlencoded"

-- 3、json
-- wrk.body = "{"foo":"bar","baz":"quux"}"
-- wrk.headers["Content-Type"] = "application/json"
```
