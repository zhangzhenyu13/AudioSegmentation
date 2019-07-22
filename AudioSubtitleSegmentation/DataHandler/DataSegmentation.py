from datetime import datetime
from AudioSubtitleSegmentation.DataHandler.DataReader import WavVttContainer
from AudioSubtitleSegmentation.TextNormailzation.normalize_transcription import TextNormalizer

VIDEO_START_TIME = datetime.strptime('00:00:00.000', '%H:%M:%S.%f')

class SegmentationHandler(object):
    @staticmethod
    def cutOnMaxSents(wvdata:WavVttContainer, sents_num):
        results=[]
        blocks=[]
        sent=""
        num=0
        cache=[]
        segments=[]
        start, end, start_ms, end_ms=None, None, None, None
        for vtt in wvdata.vtt_list:
            cache.append(vtt)
            if sent=="":
                start, start_ms=vtt["start"], vtt["start_ms"]

            sent+=vtt["text"]+" "
            if TextNormalizer.endSent(vtt["text"]):
                num+=1
                sent+="\n"
            if num>=sents_num:
                end, end_ms=vtt["end"], vtt["end_ms"]
                blocks.append(
                    {"start":start, "end":end, "start_ms":start_ms, "end_ms":end_ms, "text":sent[sent.find(":")+1:]}
                )
                sent=""
                segments.append(cache)
                cache=[]
                num=0

        if len(cache)>0:
            segments.append(cache)
            end, end_ms = cache[-1]["end"], cache[-1]["end_ms"]
            blocks.append(
                {"start": start, "end": end, "start_ms": start_ms, "end_ms": end_ms, "text": sent[sent.find(":") + 1:]}
            )


        #segments=[wvdata.vtt_list[i:i+sents_num] for i in range(0, len(wvdata.vtt_list), sents_num)]

        for i in range(len(segments)):
            seg=segments[i]

            begin_time=datetime.strptime(seg[0]["start"],'%H:%M:%S.%f')
            start_ms=seg[0]["start_ms"]
            end_ms=seg[-1]["end_ms"]

            vtt_seg=list(map(
                (
                    lambda vtt: {"text":vtt["text"],
                                 "start": (VIDEO_START_TIME+(datetime.strptime(vtt['start'],'%H:%M:%S.%f')-begin_time)).strftime('%H:%M:%S.%f'),
                                 "end": (VIDEO_START_TIME+(datetime.strptime(vtt['end'],'%H:%M:%S.%f')-begin_time)).strftime('%H:%M:%S.%f')
                                 }
                ),
                seg
            ))


            start_id = start_ms * wvdata.sampwidth * wvdata.framerate // 1000
            end_id = end_ms * wvdata.sampwidth * wvdata.framerate // 1000

            wav_seg = wvdata.wav_data[start_id:end_id]

            block_seg=blocks[i]["text"]
            block_seg=TextNormalizer.remove_vivid(block_seg)
            #block_seg=TextNormalizer.remove_person(block_seg)
            block_seg = TextNormalizer.remove_punct( block_seg )

            results.append({"vtt":vtt_seg, "wav":wav_seg, "plain": block_seg})

        return results


