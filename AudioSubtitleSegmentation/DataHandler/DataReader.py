import wave
import webvtt
from datetime import datetime, timedelta
from AudioSubtitleSegmentation.TextNormailzation.normalize_transcription import TextNormalizer


class DataIO(object):
    @staticmethod
    def readWav(wav_file):
        with wave.open(wav_file, 'rb') as wave_read:
            nchannels, sampwidth, framerate, nframes, comptype, compname = wave_read.getparams()
            print('nchannels: {}'.format(nchannels))
            print('sampwidth: {}'.format(sampwidth))
            print('framerate: {}'.format(framerate))
            print('nframes: {}'.format(nframes))
            print('comptype: {}'.format(comptype))
            print('compname: {}'.format(compname))
            assert (nchannels == 1)
            assert (sampwidth == 2)
            assert (framerate == 16000)

            data = wave_read.readframes(nframes)

        return (
            data, nchannels, sampwidth, framerate, nframes, comptype, compname
        )

    @staticmethod
    def writeWav(wav_data, wav_file):
        wav_data, nchannels, sampwidth, framerate, nframes, comptype, compname=wav_data
        with wave.open(wav_file, 'wb') as wave_write:
            wave_write.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
            wave_write.writeframes(wav_data)

    @staticmethod
    def readVtt(vtt_file):
        return webvtt.read(vtt_file)

    @staticmethod
    def writeVtt(vtt_list, vtt_file):
        vtt = webvtt.WebVTT()
        captions = map(lambda vtt: webvtt.Caption(
            start=vtt["start"], end=vtt["end"], text=vtt["text"]),
                       vtt_list
                       )
        for cap in captions:
            vtt.captions.append(cap)

        with open(vtt_file, "w") as f:
            vtt.write(f)

    @staticmethod
    def writeTxt(txt, txt_file):
        with open(txt_file, "w") as f:
            f.write(txt)

VIDEO_START_TIME = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')

class WavVttContainer(object):

    def __init__(self,vtt_file, wav_file):
        self.vtt_list=[]
        self.vtt_dict={}
        self.transcript=""
        self.wav_data=None
        self.loadVTT(vtt_file)
        self.loadWav(wav_file)

    def loadVTT(self, vtt_file):
        segments = []
        start = end = ''
        start_ms = end_ms = 0
        text = ''

        captions=DataIO.readVtt(vtt_file)

        for caption in captions:
            caption_start_ms = (datetime.strptime(caption.start, '%H:%M:%S.%f') - VIDEO_START_TIME) // timedelta(
                milliseconds=1)
            caption_end_ms = (datetime.strptime(caption.end, '%H:%M:%S.%f') - VIDEO_START_TIME) // timedelta(
                milliseconds=1)
            caption_text = caption.text.replace('\n', ' ')
            # print('{} / {} ms'.format(caption.start, caption_start_ms))
            # print('{} / {} ms'.format(caption.end, caption_end_ms))
            # print(caption_text)
            if start_ms == 0:
                start = caption.start
                end = caption.end
                start_ms = caption_start_ms
                end_ms = caption_end_ms
                text = caption_text
            else:
                appended_text = text + ' ' + caption_text
                if len(appended_text.split()) > 0:
                    # if caption_start_ms - end_ms > 10:
                    segments.append({'start': start, 'end': end, 'start_ms': start_ms, 'end_ms': end_ms, 'text': text})
                    start = caption.start
                    end = caption.end
                    start_ms = caption_start_ms
                    end_ms = caption_end_ms
                    text = caption_text
                else:
                    end = caption.end
                    end_ms = caption_end_ms
                    text = appended_text

        if text is not '':
            segments.append({'start': start, 'end': end, 'start_ms': start_ms, 'end_ms': end_ms, 'text': text})

        transcripts=map(lambda seg_vtt:seg_vtt["text"].replace("\n"," "),segments)
        transcript="[SEP]".join(transcripts)

        self.vtt_list=segments
        self.transcript=transcript

    def loadWav(self, wav_file):

        self.wav_data, self.nchannels, self.sampwidth, self.framerate, self.nframes, self.comptype, self.compname= \
            DataIO.readWav(wav_file)





