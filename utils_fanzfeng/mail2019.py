# -*- coding: utf-8 -*-
"""
@author: FanZhengfeng
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Email(object):
    def __init__(self):
        self.mail_host = "smtp.sina.com"
        self.mail_user = "just_test_fan@sina.com"
        self.mail_pass = "feng1991"
        self.mail_postfix = "sina.com"
        self.mail_prefix = 'just_test_fan'
        self.port_config = {"simple": 25, "ssl": 465}
        self.sender_name = "fanzfeng"
        self.html_template = './mail_template'

    def data_html(self, say_hai, text, table_str):
        with open(self.html_template, encoding='utf-8') as fp:
            return fp.read() % (say_hai, text, table_str)

    def send_mail(self, mail_to, mail_subject, method="ssl", insert_data=True, say_hai="", text="", table_str=""):
        if insert_data and len(table_str) > 0:
            mail_content = self.data_html(say_hai, text, table_str)
            context = MIMEText(mail_content, _subtype='html', _charset='utf-8')
            msg = MIMEMultipart()
            msg.attach(context)
        else:
            mail_content = say_hai+"\n"+text
            msg = MIMEText(mail_content, _subtype='plain')
        msg['Subject'] = mail_subject
        me = self.sender_name + "<" + self.mail_prefix + "@" + self.mail_postfix + ">"
        msg['From'] = me
        msg['To'] = ";".join(mail_to)
        try:
            if method == "ssl":
                server = smtplib.SMTP_SSL("{}:{}".format(self.mail_host, self.port_config["ssl"]))
            elif method == "simple":
                server = smtplib.SMTP("{}:{}".format(self.mail_host, self.port_config["simple"]))
            server.ehlo()
            server.starttls()
            server.login(self.mail_user, self.mail_pass)
            server.sendmail(me, mail_to, msg.as_string())
            server.close()
            return "Mail sucess"
        except Exception as e:
            return "Mail failed with log {}".format(str(e))
