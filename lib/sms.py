import urllib, re
from syslog import *
from syslog import syslog as log
import time

class SMSSendFailed(Exception):
    pass

class SMS(object):
    def __init__(self, user, passwd, chatpass):
        self.user = user
        self.passwd = passwd
        self.chatpass = chatpass
        self.sms_out_base = "http://smsout-api.vitelity.net/api.php"

    def call(self, base, parms):
        args = urllib.urlencode(parms)
        full_url = "{0}?{1}".format(base, args)
        response = urllib.urlopen(full_url)
        c, msg = (response.getcode(), response.read())
        return (c, msg)

    def sendsms(self, src, dst, msg):
        cmd = "sendsms"
        parms = {"cmd": cmd,
                 "login": self.user,
                 "pass": self.passwd,
                 "src": src,
                 "dst": dst,
                 "msg": msg,
                 "xml": "yes"}
        c, msg = self.call(self.sms_out_base, parms)
        if "ok" in msg.lower():
            return True
        return False

    def send(self, src, dst, msg):
        msg = msg.replace("<br />", "\r\n")
        msg = re.sub("<.*?>", "", msg)
        success = self.sendsms(src, dst, msg)
        if not success:
            raise SMSSendFailed(
                "sms: Failed to send message from {0} to {1}".format(src,
                                                                     dst))
        else:
            log(LOG_INFO,
                "SMS Send success: SRC: {0}, DST: {1} ->  {2}".format(src,
                                                                      dst,
                                                                      success))
        return success