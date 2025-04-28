# Credits: both swap_accidentals and note_to_number are functions originally written by Steve Hiehn
# source: https://medium.com/@stevehiehn/how-to-generate-music-with-python-the-basics-62e8ea9b99a5

def swap_accidentals(note):
    if note == 'Db':
        return 'C#'
    if note == 'D#':
        return 'Eb'
    if note == 'E#':
        return 'F'
    if note == 'Gb':
        return 'F#'
    if note == 'G#':
        return 'Ab'
    if note == 'A#':
        return 'Bb'
    if note == 'B#':
        return 'C'

    return note

def note_to_number(note: str, octave: int) -> int:
    note = swap_accidentals(note)
    assert note in NOTES, errors['notes']
    assert octave in OCTAVES, errors['notes']

    note = NOTES.index(note)
    note += (NOTES_IN_OCTAVE * octave)

    assert 0 <= note <= 127, errors['notes']

    return note

def midi_to_freq(note):
    return 440.0 * (2 ** ((note - 69) / 12))