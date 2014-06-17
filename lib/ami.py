from asterisk import manager
from syslog import syslog as log, LOG_ERR

AMI_USER = "PyHouAMIUser"
AMI_PASSWD = "GuidoVanRossumIsAwesome"

class AMI(object):
    def __init__(self):
        self.ami = self.connect()

    def connect(self):
        self.ami = manager.Manager()
        self.ami.connect("127.0.0.1")
        self.ami.login(AMI_USER, AMI_PASSWD)
        return self.ami

    def __del__(self):
        self.ami.logoff()
        self.ami.close()

    def create_call(self, src, dst, cid, context, xid="None"):
        try:
            self.ami.originate(
                "SIP/1{0}@outbound".format(src),
                dst,
                context,
                '1',
                '',
                cid,
                True,
                xid
            )
        except Exception, e:
            log(LOG_ERR, "Exception occurred in create_call: {0}".format(e))


if __name__ == "__main__":
    ami = AMI()
    src = '8325893444'
    dst = '8324770424'
    cid = '8322611494'
    ami.create_call(src, dst, cid, xid=src)
