"""Generate BloodTap's deterministic low-register gothic WAV effects."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import io
import math
from pathlib import Path
import random
import struct
import wave


ROOT=Path(__file__).resolve().parents[1]
AUDIO_DIR=ROOT/'docs'/'audio'
SAMPLE_RATE=16_000


@dataclass(frozen=True)
class Voice:
    start: float
    duration: float
    high: float
    low: float
    level: float
    shape: str='sine'
    attack: float=.025
    falloff: float=2.0


@dataclass(frozen=True)
class Sound:
    duration: float
    voices: tuple[Voice,...]
    noise: float=.0
    reverb: float=.12


SOUNDS={
    'echo_tap.wav':Sound(.24,(
        Voice(0,.20,78,42,.82,'rough',.004,3.2),
        Voice(0,.23,42,31,.45,'sine',.008,2.4),
    ),noise=.10,reverb=.04),
    'holding_purchase.wav':Sound(.62,(
        Voice(0,.48,146.83,82.41,.34,'triangle',.008,2.5),
        Voice(.035,.54,103.83,58.27,.58,'rough',.018,2.2),
        Voice(.10,.48,51.91,38.89,.40,'sine',.025,1.8),
    ),noise=.035,reverb=.15),
    'knowledge_acquired.wav':Sound(1.35,(
        Voice(0,1.02,196,116.54,.30,'triangle',.035,1.5),
        Voice(.08,1.12,155.56,92.50,.42,'rough',.05,1.4),
        Voice(.18,1.12,98,55,.52,'sine',.08,1.2),
    ),noise=.018,reverb=.22),
    'mark_earned.wav':Sound(1.05,(
        Voice(0,.74,174.61,103.83,.34,'triangle',.008,1.8),
        Voice(.04,.82,130.81,73.42,.46,'rough',.018,1.6),
        Voice(.12,.78,65.41,43.65,.44,'sine',.035,1.4),
    ),noise=.014,reverb=.25),
    'insight_gained.wav':Sound(1.75,(
        Voice(0,1.25,220,110,.25,'triangle',.05,1.25),
        Voice(.05,1.36,155.56,77.78,.39,'rough',.06,1.18),
        Voice(.22,1.35,73.42,41.20,.56,'sine',.09,1.05),
    ),noise=.022,reverb=.30),
    'menu_open.wav':Sound(.42,(
        Voice(0,.34,123.47,69.30,.32,'triangle',.004,2.5),
        Voice(.02,.36,82.41,46.25,.58,'rough',.008,2.1),
    ),noise=.025,reverb=.09),
    'menu_close.wav':Sound(.38,(
        Voice(0,.31,92.50,46.25,.40,'triangle',.004,2.8),
        Voice(.015,.33,61.74,34.65,.62,'rough',.007,2.3),
    ),noise=.04,reverb=.07),
    'omen_appears.wav':Sound(2.25,(
        Voice(0,1.45,233.08,116.54,.24,'triangle',.16,1.15),
        Voice(.08,1.62,164.81,82.41,.38,'rough',.18,1.05),
        Voice(.26,1.72,77.78,38.89,.58,'sine',.22,.92),
        Voice(.65,1.30,55,32.70,.42,'rough',.12,1.15),
    ),noise=.055,reverb=.34),
    'return_to_dream.wav':Sound(3.15,(
        Voice(0,1.42,196,110,.24,'triangle',.06,1.3),
        Voice(.32,1.62,146.83,82.41,.34,'rough',.10,1.16),
        Voice(.72,1.82,98,55,.49,'sine',.14,1.02),
        Voice(1.20,1.70,55,30.87,.60,'rough',.18,.92),
    ),noise=.03,reverb=.38),
}


def oscillator(shape,phase):
    fundamental=math.sin(phase)
    if shape=='triangle':return 2/math.pi*math.asin(fundamental)
    if shape=='rough':return .78*fundamental+.17*math.sin(phase*2)+.05*math.sin(phase*3)
    return fundamental


def render(sound,seed):
    frames=int(sound.duration*SAMPLE_RATE)
    samples=[0.0]*frames
    for voice in sound.voices:
        if voice.low<=0 or voice.high<voice.low:raise ValueError('Every voice must descend to a positive frequency')
        phase=0.0
        start=int(voice.start*SAMPLE_RATE)
        length=max(1,int(voice.duration*SAMPLE_RATE))
        for j in range(length):
            i=start+j
            if i>=frames:break
            x=j/max(1,length-1)
            frequency=voice.high*(voice.low/voice.high)**x
            phase+=2*math.pi*frequency/SAMPLE_RATE
            attack=1-math.exp(-(j/SAMPLE_RATE)/max(.001,voice.attack))
            envelope=attack*max(0,1-x)**voice.falloff
            samples[i]+=voice.level*envelope*oscillator(voice.shape,phase)
    if sound.noise:
        rng=random.Random(seed);smooth=0.0
        for i in range(frames):
            smooth+=(rng.uniform(-1,1)-smooth)*.035
            tail=max(0,1-i/frames)**1.7
            samples[i]+=smooth*sound.noise*tail
    dry=samples[:]
    for delay,weight in ((.071,.30),(.137,.18),(.223,.10)):
        offset=int(delay*SAMPLE_RATE)
        for i in range(offset,frames):samples[i]+=dry[i-offset]*weight*sound.reverb
    peak=max(max(abs(value) for value in samples),1e-9)
    scale=.78/peak
    pcm=b''.join(struct.pack('<h',round(max(-1,min(1,value*scale))*32767)) for value in samples)
    output=io.BytesIO()
    with wave.open(output,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(SAMPLE_RATE);wav.writeframes(pcm)
    return output.getvalue()


def rendered_assets():
    return {name:render(sound,0xB100D+index) for index,(name,sound) in enumerate(SOUNDS.items())}


def write_assets():
    AUDIO_DIR.mkdir(parents=True,exist_ok=True)
    for name,data in rendered_assets().items():(AUDIO_DIR/name).write_bytes(data)


def check_assets():
    for name,data in rendered_assets().items():
        path=AUDIO_DIR/name
        if not path.is_file() or path.read_bytes()!=data:raise SystemExit(f'Audio asset is stale: {path.relative_to(ROOT)}')
    print('Ominous audio assets are deterministic and current.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.check:check_assets()
    else:write_assets();print(f'Wrote {len(SOUNDS)} effects to {AUDIO_DIR}')


if __name__=='__main__':main()
