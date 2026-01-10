from DataTrainer import DataTrainer

def main():
    dt = DataTrainer(data_path='MIDI_files')

    print(dt.all_instruments)

if __name__ == '__main__':
    main()