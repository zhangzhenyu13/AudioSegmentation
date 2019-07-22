import argparse
import os
import wave
import audioop
import pydub


def convert_wav(infile, outfile):
    print('{} -> {}'.format(infile, outfile))
    if os.path.exists(outfile):
        return

    with wave.open(infile, 'rb') as wave_read:
        nchannels, sampwidth, framerate, nframes, comptype, compname = wave_read.getparams()
        print('nchannels: {}'.format(nchannels))
        print('sampwidth: {}'.format(sampwidth))
        print('framerate: {}'.format(framerate))
        print('nframes: {}'.format(nframes))
        print('comptype: {}'.format(comptype))
        print('compname: {}'.format(compname))

        data = wave_read.readframes(nframes)
        data = audioop.ratecv(data, sampwidth, nchannels, framerate, 16000, None)
        data = audioop.tomono(data[0], sampwidth, 1, 0)

    with wave.open(outfile, 'wb') as wave_write:
        wave_write.setparams((1, sampwidth, 16000, nframes, comptype, compname))
        wave_write.writeframes(data)


def convert_m4a(infile, outfile):
    tmpfile = os.path.splitext(infile)[0] + '.wav'
    print('{} -> {}'.format(infile, tmpfile))

    track = pydub.AudioSegment.from_file(infile, 'm4a')
    track.export(tmpfile, format='wav')
    convert_wav(tmpfile, os.path.splitext(outfile)[0] + '.wav')
    os.remove(tmpfile)

def convert_dir(indir, outdir):
    os.makedirs(outdir, exist_ok=True)
    for entry in os.listdir(indir):
        inentry = os.path.join(indir, entry)
        outentry = os.path.join(outdir, entry)
        if os.path.isdir(inentry):
            convert_dir(inentry, outentry)
        else:
            _, ext = os.path.splitext(entry)
            if ext == '.wav':
                convert_wav(inentry, outentry)
            if ext == '.m4a':
                convert_m4a(inentry, outentry)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', default='../data2',
                        type=str, help='Data directory')
    args = parser.parse_args()

    indir = args.data_dir
    outdir = (args.data_dir +'.16k_mono') if args.data_dir[-1]!="/"else (args.data_dir[:-1]+".16k_mono")
    convert_dir(indir, outdir)

if __name__ == '__main__':
    main()
