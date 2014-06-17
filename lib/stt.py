import requests, os, math, json
from syslog import syslog as log, LOG_INFO

MYCAPTION_ASR_API="https://mycaption-prod.apigee.net/v1/asr?apikey={0}&audio_duration={1}&reference={2}&audio_format={3}&callback={4}"
MYCAPTION_PREMIUM_API="https://mycaption-prod.apigee.net/v1/audio?apikey={0}&audio_duration={1}&reference={2}&audio_format={3}&callback={4}"
CALLBACK='http://54.186.252.119/speech_to_text?response=True'
KEY=open("/etc/mc", 'r').read().strip()

try:
    import pysox

    def getAudioDuration(path):
        audio = pysox.CSoxStream(path)
        signal = audio.get_signal()
        del audio
        info = signal.get_signalinfo()
        length = info['length']
        samples = length / info['channels']
        duration = samples / info['rate']
        return int(math.ceil(duration))
except:
    def getAudioDuration(path):
        return 11


def genURL(apikey, duration, reference, fmt, callback):
    url = MYCAPTION_PREMIUM_API
    url = url.format(apikey, duration, reference, fmt, callback)
    return url


def getFormat(path):
    root, fmt = os.path.splitext(path)
    return fmt.lstrip(".")


def requestCaption(session, uuid, path):
    reference = uuid
    callback = CALLBACK
    apikey = KEY
    try:
        duration = getAudioDuration(path)
    except:
        duration = 10
    log(LOG_INFO,
        "{0}: mycaption.requestCaption: Sending {1} for MyCaption transcription".format(
            session, path))

    fmt = getFormat(path)
    if not fmt:
        raise Exception("Unable to determine file format")

    log(LOG_INFO,
        "{0}: mycaption.requestCaption: File format: {1}".format(session, fmt))

    url = genURL(apikey, duration, reference, fmt, callback)
    if not url:
        raise Exception("Unable to generate URL")

    data = open(path, 'rb').read()
    size = len(data)
    if size <= 100:
        log(LOG_INFO,
            "{0}: mycaption.requestCaption: File size indicates empty file!".format(
                session))
        return False
    log(LOG_INFO,
        "{0}: mycaption.requestCaption: Read in {1} bytes of audio data".format(
            session, size))

    headers = {'content-type': 'application/octet-stream'}
    log(LOG_INFO,
        "{0}: mycaption.requestCaption: Sending request to MyCaption".format(
            session))
    res = requests.post(url=url, data=data, headers=headers)
    log(LOG_INFO,
        "{0}: mycaption.requestCaption: Got a response! {1}".format(session,
                                                                    res.content))
    try:
        response = json.loads(res.content)
    except:
        response = {}

    if 'status' in response and response['status'] == '200':
        for key, value in response.iteritems():
            log(LOG_INFO,
                "{0}: mycaption.requestCaption: {1} - {2}".format(session, key,
                                                                  value))
        return True
    else:
        log(LOG_INFO,
            "{0}: mycaption.requestCaption: Transmission failed.".format(
                session))
    return False
