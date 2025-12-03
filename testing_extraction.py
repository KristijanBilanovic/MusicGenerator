import music21
import random


stream = music21.converter.parse('MIDI_files/TSwift_22.mid')

for e in stream.parts:
    print(e.partName)

s = stream.chordify()

chords = []

for element in stream.recurse().getElementsByClass('Chord'):
    if element.pitchNames not in chords:
        chords.append(element.pitchNames)

transition = []

for i in range(len(chords)):
    transition.append([0 for _ in range(len(chords))])

first = True
last = None

for element in stream.recurse().getElementsByClass('Chord'):
    index = chords.index(element.pitchNames)
    if first:
        first = False
        last = index
    else:
        transition[last][index] += 1
        last = index

for row in transition:
    sum_row = sum(row)
    for i in range(len(row)):
        row[i] /= sum_row
    
chords2 = []

last = 0
for i in range(100):
    if i == 0:
        chords2.append(random.choice(chords))
    else:
        c1 = random.choices(chords, weights= transition[last])[0]
        c2 = random.choice(chords)
        chords2.append(random.choices([c1, c2], weights=[0.89, 0.11])[0])
        last = chords.index(chords2[i])

newStream = music21.stream.Stream()
ts = music21.meter.TimeSignature('4/4')

newStream.append(ts)

for elem in chords2:
    c = music21.chord.Chord(elem)
    c.quarterLength = random.choice([2, 3, 1])
    newStream.append(c)

newStream.show()