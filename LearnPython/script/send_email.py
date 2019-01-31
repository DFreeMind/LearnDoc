# 导入存文本
from email.mime.text import MIMEText

# MIMEText 有三个参数
# 第一个参数表示要发送的文本内容
# 第二个参数表示 MIME 内容类型，默认是 纯文本类型‘plain’
# 第三个参数表示 发送文本的编码，默认是‘us-ascii’
msg = MIMEText('终于知道邮件是怎么发送的了，O(∩_∩)O哈哈~', 'plain', 'utf-8')

# 发送人 
from_addr = 'q_w_e_r12@126.com'
password = 'a1234567890'

# 接收人
to_addr = 'q_w_e_r12@yeah.net'

# 输入SMTP服务器地址:
smtp_server = 'smtp.126.com'

# 发送邮件设置
import smtplib
server =smtplib.SMTP(smtp_server, 25)
server.set_debuglevel(1)
# 登陆发送服务器
server.login(from_addr, password)
# 发送邮件
server.sendmail(from_addr,[to_addr], msg.as_string())
# 退出
server.quit()