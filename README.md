## 环境Python3.9
#### 我在这说一下关于Cookie值登录失败的问题，需要取播放界面的Cookie值，最好就取/learning/saveDatabaseIntervalTime这个接口的Cookie值
#### 关于课程secret码的问题 请滑到教程.md最下面 都是有说明的，它其实就在播放界面的地址里面 
#### 知到请求参数更新了，参数用了AES加密，且移除了用户id这个参数，将这个参数添加到了cookies里面，所以现在只用session已经登不上去了，需要直接贴cookies
#### 目前版本已知运行失败问题：
当运行时提示{'code': -12, 'message': '需要弹出滑块验证', 'data': None}时，请登录智慧树在视频播放界面进行验证滑块验证后，即可解决此问题

## 更新记录
### 1.0：
1.基本实现刷课功能
### 2.0：由用户SzLeaves更新
1.修复了XHR异常返回值导致的程序中止

2.从文件中读取cookies和secret码，修改了默认选项，可以批量刷课。可以从文件里面读取需要的值，cookies从cookies.txt中读取，secret码从id.txt中读取（一行放一个课程的secret码）
### 2.1：
1.修复了{'code': -5, 'message': '提交参数错误', 'data': None}报错

2.移除了execjs库
