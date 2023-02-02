# def change_language(audio_file:str, dest_lang:str)->str:
#     """
#     This function converts the audio from a given language to another language.

#     Parameters:
#     audio_file (str): The path of the audio file.
#     dest_lang (str): The language to which the audio is to be converted.

#     Returns:
#     str: The path of the converted audio file.
#     """
#     tts = gTTS(audio_file, lang=dest_lang)
#     with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
#         tts.save(f.name)
#     return f.name

# import io
# import os
# from google.cloud import texttospeech

# def change_audio_language(audio_file, target_language='en-US'):
#     """
#     This function converts the audio from a given language to another language.

#     Parameters:
#     audio_file (str): The path of the audio file.
#     dest_lang (str): The language to which the audio is to be converted.

#     Returns:
#     str: The path of the converted audio file.
#     """
#     # Instantiates a client
#     client = texttospeech.TextToSpeechClient()

#     # Set the text input to be synthesized
#     with io.open(audio_file, 'rb') as audio:
#         content = audio.read()
#     audio = texttospeech.types.RecognitionAudio(content=content)

#     # Perform the text-to-speech request on the text input with the selected
#     # voice parameters and audio file type
#     response = client.recognize(audio)

#     # Get the text from the response
#     text = response.results[0].alternatives[0].transcript

#     # Set the text input to be synthesized
#     synthesis_input = texttospeech.types.SynthesisInput(text=text)

#     # Build the voice request, select the language code ("en-US") and the ssml
#     # voice gender ("neutral")
#     voice = texttospeech.types.VoiceSelectionParams(
#         language_code=target_language,
#         ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

#     # Select the type of audio file you want returned
#     audio_config = texttospeech.types.AudioConfig(
#         audio_encoding=texttospeech.enums.AudioEncoding.MP3)

#     # Perform the text-to-speech request on the text input with the selected
#     # voice parameters and audio file type
#     response = client.synthesize_speech(synthesis_input, voice, audio_config)

#     output_audio_file = os.path.join(os.getcwd(), "data", "videos", "output.mp3")
#     # The response's audio_content is binary.
#     with open(output_audio_file, 'wb') as out:
#         # Write the response to the output file.
#         out.write(response.audio_content)
#         print(f'Audio content written to file "{output_audio_file}"')

import subprocess

def change_audio_language(audio_file:str, dest_language:str):
    """
    This function changes the language of an audio file using eSpeak.

    Parameters:
    audio_file (str): The path of the audio file.
    dest_language (str): The destination language.

    Returns:
    None
    """
    # Create the eSpeak command
    espeak_cmd = f"espeak -v {dest_language} -w {audio_file} {audio_file}"
    # Execute the command
    subprocess.run(espeak_cmd, shell=True)
    print("Audio language changed successfully!")
    return audio_file
