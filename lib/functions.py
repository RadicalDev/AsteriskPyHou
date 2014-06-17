import os
import time
import pickle
from uuid import uuid4
from syslog import syslog as log, LOG_INFO
from sms import SMS


def whisper(agi, text):
    uid = uuid4()
    rec_path = "/dev/shm/{0}.wav".format(uid)
    play_path = "/dev/shm/{0}".format(uid)
    swift_cmd = "swift '{0}' -o {1}".format(text, rec_path)
    os.system(swift_cmd)
    while not os.path.exists(rec_path):
        time.sleep(0.2)
    agi.appexec("PLAYBACK", play_path)
    os.remove(rec_path)


def sms(number, msg):
    try:
        with open("/etc/sms.p", 'r') as f:
            creds = pickle.load(f)
    except:
        return False
    return SMS(creds['user'], creds['passwd'], creds['chatpass']).send("8322611494", number, msg)

if __name__ == "__main__":
    sms("test")


