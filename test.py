import music21

score = music21.converter.parse('./MIDI_files/TSwift_Bejeweled.mid')
score = music21.instrument.partitionByInstrument(score)

newScore = music21.stream.Score()  


print("Extracting all melodic parts...\n")

for i, part in enumerate(score.parts):
    newPart = music21.stream.Part()

    if part.getInstrument().instrumentName == 'Sampler':
        for element in part.recurse():
            if isinstance(element, music21.note.NotRest):
                newPart.append(element)
                print(element.getInstrument())
        newPart.makeMeasures()

    print('.................................................................')
    newScore.append(newPart)


newScore.show('midi')