import pvporcupine
import pyaudio
import struct

# Initialisatie van Porcupine
porcupine = None
pa = None
audio_stream = None

AccessKey = "E/nt0xDixBdsPigUSV/STlMLvAbEfvSEnkLMTngqHz77yKn6RwKX/Q=="

try:
    #porcupine = pvporcupine.create(access_key=AccessKey, keywords=["jarvis"])

    porcupine = pvporcupine.create(
    access_key=AccessKey,
    keyword_paths=['porcupine\Hallo-Na-o_nl_windows.ppn', 'porcupine\Hallo-robot_nl-windows.ppn'],
    model_path='porcupine\porcupine_params_nl.pv'
    )


    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print("Listening for the wake word...")

    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm_unpacked)

        if keyword_index >= 0:
            print("Wake word detected!")
            # Voer hier de actie uit die moet gebeuren na detectie

finally:
    if porcupine is not None:
        porcupine.delete()

    if audio_stream is not None:
        audio_stream.close()

    if pa is not None:
        pa.terminate()
