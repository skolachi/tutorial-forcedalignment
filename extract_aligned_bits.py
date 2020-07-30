
import argparse
import json
import re
import sys
import subprocess

def sentence_splitter(text): # simple sentence splitter
    return list(filter(None, [s.strip() for s in re.split('[\n\.\!\?]+',text)]))

def extract_utterances(transcript, alignment): # extract utterances with time stamp
    aligned = json.loads(open(alignment).read())
    sentences = sentence_splitter(open(transcript).read())
    utterances_timestamp = []
    timestamp = []
    i = 0
    for s in sentences:
        words = s.replace('-',' ').split()
        for w in words:
            w = w.replace(',','')
            a = aligned['words'][i]['word']
            if a == w:
                if aligned['words'][i]['case'] == 'success':
                    timestamp.append([w, aligned['words'][i]['start'], aligned['words'][i]['end']])
                else:
                    timestamp.append([w, 'n/a', 'n/a'])
            else:
                print('Word mismatch: %s %s'%(w,a))
            i += 1
        utterances_timestamp.append(timestamp)
        timestamp = []

    return utterances_timestamp

def extract_audio_bits(audio, transcript, alignment): # extract audio bits for utterances 
    utterances_timestamp = extract_utterances(transcript, alignment)
    j = 0
    for u in utterances_timestamp:
        if u[0][1] != 'n/a' and u[-1][2] != 'n/a': # extract audio bit only if first and last word are aligned
            start = str(u[0][1])
            end = str(u[-1][2])
            text = ' '.join([w[0] for w in u])
            with open('utterance-%s.txt'%(str(j+1)),'w') as f:
                f.write(text)
            subprocess.run(['ffmpeg','-i',audio,'-ss',start,'-to',end,'utterance-%s.wav'%(str(j+1))])
            j += 1

def main():
    parser = argparse.ArgumentParser(description='Extract aligned audio bits')
    parser.add_argument("--audio",help="audio file", required=True)
    parser.add_argument("--transcript",help="transcript file", required=True)
    parser.add_argument("--alignment",help="json output of gentle", required=True)
    args = parser.parse_args()
    extract_audio_bits(args.audio, args.transcript, args.alignment)

if __name__ == "__main__":
    main()
