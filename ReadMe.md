# 上班进度条

>上班进度条，提醒你当前上班进度

## 下载地址
exe下载:[蓝奏云](https://wwde.lanzouj.com/izghA1aqjkeb) 密码:9vcf
视频演示：[哔哩哔哩](https://www.bilibili.com/video/BV1vw411w7s5/?share_source=copy_web&vd_source=31ed8bce8b402e158ab66a8191e45770)

## 基础用法

软件第一次启动会提示设置上下班时间，设置好以后，屏幕的 Top 会有一条 `1mm`高的进度条，当进度条走完后，会弹出 **Dialog** 提示你关机下班。

## 高级用法

右键托盘程序的`高级设置`，会打开配置文件`configs.ini`，设置内容如下：

```ini
[SETTINGS]
autohide = true
worktime = 08:30
offtime = 19:59
joke = false

[MESSAGES]
tip1 = 到点了，该下班了，要帮你马上关机吗
tip2 = 你已经加班了3秒了，下班吧
tip3 = 劳逸结合呀，下班吧
tip4 = 还不下班吗？
tip5 = 再不下班我放大招了
tip6 = 骗你的，刚才只是个动画，不要害怕
tip7 = 你的精神感动了我，今年的敬业福非你莫属
tip8 = 你不下班我下班，拜拜

```

 以上内容都可以更改：

+ `autohide`：是否默认隐藏到托盘，默认`false`，第一次启动，设置完上下班时间后会变为`true`
+ `worktime`：上班时间，格式默认为 `00:00`
+ `offtime`：下班时间，格式默认为 `00:00`
+ `joke`：是否开玩笑，默认`false`，设置为`true`后，关机提示会提示**[MESSAGES]**中的内容，有几个tip就弹出几次 **Dialog**，请注意，tip 数量和 gifs 文件夹下的表情包数量一致

## 注意

如果软件安装在C盘，那么需要**以管理员身份运行**，不然无法编辑配置文件`configs.ini`

## 声明

本软件完全免费，请勿相信任何付费内容！

本软件代码完全开源，任何人二次修改创作均与本人无关，请勿用作不法用途

## 联系我

欢迎关注我的公众号，获取更多有趣内容

![关注公众号](./res/关注公众号.png)
