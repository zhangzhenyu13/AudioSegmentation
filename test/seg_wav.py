import os
import argparse
from AudioSubtitleSegmentation.DataHandler.DataReader import DataIO, WavVttContainer
from AudioSubtitleSegmentation.DataHandler.DataSegmentation import SegmentationHandler
from AudioSubtitleSegmentation.TextNormailzation.normalize_transcription import TextNormalizer

def runVtt():
    #vwdata.loadVTT(vtt_file)
    vtt_file=""
    wav_file=""
    wvdata = WavVttContainer(vtt_file, wav_file)

    print("len_vtt: ", len(wvdata.vtt_list))
    print(wvdata.vtt_list[:3])
    print(wvdata.transcript)
    tn = TextNormalizer.normalize_vtt(wvdata.transcript)
    print(tn)
    tns = tn["TN"].split("[SEP]")
    print(len(tns), tns[:3])
    tns = list(map(lambda txt: TextNormalizer.remove_punct(txt), tns))
    print(tns[:5])

def runSeg(vtt_file, wav_file, out_dir):
    print("Segmenting-->",vtt_file, wav_file, out_dir)
    if os.path.exists(vtt_file) == False or os.path.exists(wav_file) == False:
        return
    wvdata = WavVttContainer(vtt_file, wav_file)

    segments=SegmentationHandler.cutOnMaxSents(wvdata,args.sents_num, args.words_num)
    folder= out_dir#wav_file[:wav_file.rfind("/")]+".seg"
    name=wav_file[1+wav_file.rfind("/"):wav_file.rfind(".")]
    os.makedirs(folder, exist_ok=True)

    for i in range(len(segments)):
        seg=segments[i]
        vtt, wav, txt=seg["vtt"], seg["wav"], seg["plain"]
        vtt_out=os.path.join(folder,name+"-"+str(i)+".vtt")
        wav_out=os.path.join(folder,name+"-"+str(i)+".wav")
        txt_out=os.path.join(folder, name+"-"+str(i)+".txt")
        DataIO.writeVtt(vtt, vtt_out)
        wav_data=(wav,wvdata.nchannels, wvdata.sampwidth, wvdata.framerate, wvdata.nframes, wvdata.comptype, wvdata.compname)
        DataIO.writeWav(wav_data, wav_out)
        DataIO.writeTxt(txt, txt_out)


def segment_dir(vtt_dir, wav_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for entry in os.listdir(vtt_dir):
        vtt_entry = os.path.join(vtt_dir, entry)
        wav_entry = os.path.join(wav_dir, entry)
        out_entry = os.path.join(out_dir, entry)
        if os.path.isdir(vtt_entry):
            segment_dir(vtt_entry, wav_entry, out_entry)
        elif os.path.splitext(entry)[1] == args.vtt_ext:
            entry_fn = os.path.splitext(entry)[0]
            entry_fn, lan = os.path.splitext(entry_fn)
            #assert(lan == '.en')
            wav_entry = os.path.join(wav_dir, entry_fn + '.wav')
            out_entry = os.path.join(out_dir, entry_fn)
            #segment_wav(vtt_entry, wav_entry, out_entry)
            runSeg(vtt_file= vtt_entry, wav_file= wav_entry, out_dir=out_entry)

if __name__ == '__main__':

    parser=argparse.ArgumentParser()
    parser.add_argument("--vtt_dir", default="../data/")
    parser.add_argument("--wav_dir", default="../data/")
    parser.add_argument("--vtt_ext", default=".vtt")

    parser.add_argument("--sents_num", default=30, type=int)
    parser.add_argument("--words_num", default=25, type=int)

    args=parser.parse_args()

    vtt_dir = args.vtt_dir
    wav_dir = args.wav_dir
    out_dir = vtt_dir + ".seg" if vtt_dir[-1]!='/' else vtt_dir[:-1]+".seg"
    #runVtt()

    #runSeg(vtt_dir, wav_dir, out_dir)
    segment_dir(vtt_dir, wav_dir, out_dir)
