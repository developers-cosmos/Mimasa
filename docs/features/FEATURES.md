# Mimasa Features

Below is a list of features that needs to be implemented for Mimasa.

## 1. User Sign-up & Login

### Description

This feature will allow users to create an account on Mimasa and sign in to access the application's services.

## DoD

The acceptance criteria for this feature include creating an account using an email address and password,
signing in with the created account, and securely storing the user's credentials.

## 2. Upload Details

### Description

1. This feature will allow users to upload a video to the application. This feature allows the user to select a video
file from their device, supporting different video file formats, and storing the video file securely.
2. User should be able to select the language they want to translate the video to

### DoD

User should be able to select a video file from their device & provide necessary details and upload it to the application.

## 3. Translation Request Submission

### Description

1. User can submit a request to translate the video they uploaded.
2. Video uploaded by user will be processed by Mimasa and the result will be provided later.
3. The user is notified when the translation is ready.
4. The user should receive a notification when the translation is ready to download

### DoD

User should be able to submit a request to translate the video they uploaded, specifying the language they want it translated to.

## 4. Video Translation Processing

### Description

1. The application processes the video uploaded by the user to extract audio. The separated audio should be given to **Audio Translation**
2. The video should undergo processing, perform facial tracking.
3. The component should also takes care of pre/post processing.

### DoD

The application should accurately extract audio from the video, track facial movements.

### Datasets Reference

1. **Facial landmarks dataset:** A large dataset of face annotations that can be used for facial tracking and pre/post processing. Example: 300-W dataset, AFLW dataset.
2. **Audio classification dataset:** A dataset that can be used to separate the music and speech from the video. Example: AudioSet, UrbanSound8K.


## 5. Audio Translation Processing

### Description

1. This feature will allow users to separate the music and speech from the video input.
2. Positions of speech in the audio should be determined.
3. The extracted speech is translated to user selected language.
4. The translated text is converted to speech.
5. Overlay the translated speech with music and prepare the final audio.
6. The component should also takes care of pre/post processing.

### DoD

1. The acceptance criteria for this feature include using machine learning techniques to separate the music and speech tracks
2. Providing the user with translated audio synced with background music.

### Datasets Reference

1. **Text-to-speech (TTS) dataset:** A dataset that can be used to convert translated text to speech. Example: LJSpeech dataset, VCTK corpus.
2. **Speech recognition dataset:** A dataset that can be used to extract speech positions in the audio. Example: CommonVoice dataset, VoxCeleb dataset.

## 6. Emotion Detection & Lip Syncing

### Description

1. The Emotion Detection & Lip Syncing feature will allow users to detect emotions and sync the lip movements in the video based on the given audio.
2. The implementation of this feature will require the use of computer vision, machine learning, and speech processing technologies.

### DoD

1. The acceptance criteria for this feature include detecting emotions from facial expressions in the video
2. syncing the lip movements with the audio translation, and providing a more natural and realistic translation experience.

### Datasets Reference

1. **Facial expression recognition dataset:** A dataset that can be used to detect emotions from facial expressions. Example: EmoReact dataset, AffectNet dataset.
2. **Lip synchronization dataset:** A dataset that can be used to sync the lip movements with the audio translation. Example: LRW dataset, GRID dataset.
