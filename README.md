# PyMima

- GUI Password Manager by PyQt5 
- 这是一个简单，但基本功能完整的桌面单机版密码管理软件
- 采用SQLite，全部数据保存在单个文件中 (pymima.db)，便于备份


## 最大特点：保留修改历史记录

- 删除项目时，先移到回收站，可随时恢复
- 从回收站里删除项目，才是彻底删除，因此确保不会不小心错删
- 很多密码管理软件都有回收站功能，但有修改历史的却不多
- 使用本软件每次对项目进行修改，均保留修改历史
- 由于保留修改历史，过去曾经用过的密码全部保留！


## 采用 PyQt5 编写：开源、容易修改、跨平台

- Python 是一种简洁易读的语言，Qt 文档非常详细
- 采用 PyQt5 编写的程序，三大桌面平台均可轻松运行
- PyQt5 用来写些自用的带 GUI 界面的小软件，是一个很好的选择
- 本软件虽然简单但一些常用的桌面GUI基用法都用到了，完全可以作为一个入门参考示例
- 当然，水平有限，只能算是抛砖引玉，代码质量不高


## 基本功能

- 虽然只是个简单的小软件，界面也不现代化，但使用起来还是很方便的
- 比如：
  * 对于常用项目，可以双击加星顶置
  * 用户名、密码等可以双击复制
  * 有简陋的搜索功能
  * 有简陋的生成随机密码功能
  * 显示密码时，数字用不同颜色显示，便于辨认
  * 定时锁定功能也是有的（以防临时离开忘记关闭而泄密）
- 特别是回收站和修改历史，这两个功能用 excel 或文本文件等土办法保存密码就不容易实现


## 关于安全

- 加密方法采用 NaCl 的 secretbox，主要是考虑到这种方式对编程比较友好，容易正确处理，不容易出差错，安全性也是完全足够的，具体加密强度可以自行搜索研究。
- 如上所述，由于加密方法具有较高的安全性，请记住主密码，一旦忘记我也没办法帮你破解。
- NaCl是一个受到广泛支持的加密库，比如 Ruby, Go, JavaScript 等，都可以方便地使用 NaCl，因此只要有密码，用别的语言也可以方便地写个解密程序处理 pymima.db，因此本软件并不会对你造成限制，你可以轻松迁移。
- 本软件提供了双击复制用户名或密码的功能，方便使用，但要注意：
  * 并没有自动清空剪贴板功能，因此，复制密码后，要注意自己清空剪贴板
  * 之所以不自动清空剪贴板，因为复制本身就是有安全隐患的，别的程序可以监控剪贴板，防不胜防。还有不少人会使用剪贴板辅助软件，会自动保留剪贴板历史方便随时粘帖前几次复制的东西。
  * 但一般来说在自己的电脑里，问题不会很大，不用太紧张，我自己图方便也是直接双击复制的。
- 所有数据都经过加密后保存在 pymima.db 里，该文件可以随意保存到移动硬盘或网盘上备份，只要使用了强密码，一般人是无法破解的。强密码是指包含大小写字母和数字的12位以上的密码（不能用电话号码、生日等个人信息），理论上很难暴力破解。
- 没有绝对的安全，我连源码都公开了，万一有什么泄密、损失之类的，我一概不负责任。（这个你用别的任何密码管理软件都是一样的，都没有绝对安全）


## 安装和使用

1. 安装 Python
2. `pip install PyQt5`
3. `pip install PyNaCl`
4. 下载本程序源代码
  - https://github.com/ahui2016/PyMima/archive/master.zip
5. `python create_default_account.py`
  - 这一步会创建一个默认账户，同时生产 pymima.db
  - 初始密码就在 `create_default_account.py` 里，可以先修改后再创建
  - 创建账户后，记得删除该文件里的密码
6. `python mainwindow.py`
  - 这一步正式运行程序
  - Windows用户可以修改该文件的缀名 mainwindow.pyw，然后双击该文件即可启动程序
7. `python change_master_password.py`
  - 当需要更改主密码时，使用该命令
  - 修改前，建议先备份 pymima.db
  - 先编辑文件，填写旧密码和新密码，再执行该文件
  - 修改成功后，记得删除该文件里的密码
