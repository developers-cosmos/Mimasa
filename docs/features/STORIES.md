# Mimasa Stories

Below is a list of stories that needs to implemented for Mimasa.

**NOTE: The below stories are tentative and not accurate**

## User Story 1: User Sign-up

### Description

This user story is about allowing users to create an account on Mimasa by providing basic details such as name, email address, and password.

### DoD

1. The user should be able to enter their name, email address, and password on the sign-up page.
2. The user should be able to confirm the email address by clicking a link sent to the email address provided.
3. The user's password should be encrypted and securely stored in the database.

### Implementation Details

1. **Front-end:** The sign-up page can be created using HTML, CSS, and JavaScript.
A form can be used to capture the user's details and a button to submit the form.
The form can be validated using JavaScript to ensure that all fields are filled in correctly.
2. **Back-end:** A server can be set up to handle the sign-up request. The server can be implemented using a technology such as Node.js or Ruby on Rails.
The server can use a database such as MySQL or MongoDB to store the user's details securely. The server can use a library such as bcrypt to encrypt the
user's password before storing it in the database. An email service such as SendGrid or Mailgun can be used to send the confirmation link to the user's email address.
3. **Authentication:** An authentication system can be implemented to keep track of the user's login status.
A technology such as JSON Web Tokens (JWT) or Sessions can be used for this purpose.

## User Story 2: User Login

### Description

This user story is about allowing users to sign in to their Mimasa account to access the application's services.

### DoD

1. The user should be able to enter their email address and password on the login page
2. The user's email address and password should be verified against the database
3. The user should be redirected to the dashboard if the email address and password are correct, and a message should be displayed if they are incorrect

### Implementation Details

1. **Front-end:** The login page can be created using HTML, CSS, and JavaScript. A form can be used to capture the user's email address and password,
and a button to submit the form. The form can be validated using JavaScript to ensure that both fields are filled in correctly.
2. **Back-end:** A server can be set up to handle the login request. The server can use the same technology and database as in the User Sign-up story #1.
The server can use a library such as bcrypt to compare the encrypted password in the database with the encrypted version of the password entered by the user.
If the passwords match, the user can be logged in and redirected to the dashboard. If the passwords don't match, a message can be displayed to the user.
3. **Authentication:** The authentication system can be used to keep track of the user's login status, as described in the User Sign-up story #1.

### Tech Stack Suggestions

1. **Front-end:** HTML, CSS, JavaScript, and a front-end framework such as React or Angular
2. **Back-end:** Node.js, Ruby on Rails, or Django
3. **Database:** MySQL, MongoDB, or PostgreSQL
4. **Authentication:** JSON Web Tokens (JWT) or Sessions
5. **Email Service:** SendGrid or Mailgun
6. **Encryption:** bcrypt or Argon2

## User Story 3: User can submit a request to translate the video they uploaded

### Description

1. This user story is about allowing the user to initiate the translation process for their uploaded video.
2. The user should be able to select the video they want to translate and specify the target language.

### DoD

1. The user should be able to select the video they want to translate.
2. The user should be able to specify the target language.
3. The translation request should be sent to the backend.
4. The backend should initiate the translation process if available or schedule the job.

### Implementation Details

1. Create a form or interface where the user can select the video they want to translate and specify the target language.
2. The form should send a request to the backend, where the translation process is initiated.
3. The backend can use an API or a service to perform the translation.
4. Store the translation request in a database for tracking and processing.

## User Story 4: Video uploaded by user will be processed by Mimasa and the result will be provided later

### Description

1. This user story is about processing the video uploaded by the user and providing the result.
2. The backend should perform the translation and return the translated video.

### DoD

1. The backend should retrieve the translation request.
2. The translation process should be performed.
3. The translated video should be generated & stored.

### Implementation Details

1. The backend should retrieve the translation request from the database.
2. Use an API or a service to perform the translation.
3. Process the video to extract the audio and perform the translation.
4. Generate the translated video.
5. Store the translated video in a database or file system.

## User Story 5: The user is notified when the translation is ready

### Description

1. This user story is about notifying the user when the translation is ready.
2. The backend should send a notification to the user that the translated video is ready.

### DoD

1. The user should receive a notification that the translated video is ready.
2. The notification should be sent via a specified method.
3. The notification should be stored for tracking purposes.

### Implementation Details

1. When the translated video is generated, send a notification to the user.
2. The notification can be sent via email, SMS, push notification, or any other method.
3. Store the notification in a database or file system for tracking purposes.

## User Story 6: The user should receive a notification when the translation is ready to download

### Description

1. This user story is about notifying the user when the translated video is ready to download.
2. The user should receive a notification with a link to download the translated video.

### DoD

1. The user should receive a notification with a link to download the translated video.
2. The link should be a secure URL or a unique identifier to download the video.
3. The notification and download link should be stored for tracking purposes.

### Implementation Details

1. When the translated video is ready, send a notification to the user with a link to download the video.
2. The link can be a secure URL or a unique identifier to download the video.
3. Store the notification and download link in a database or file system for tracking purposes.

## User Story 7: Audio Extraction

### Description

The application should extract the audio from the video uploaded by the user.

### DoD

1. The application should accurately extract the audio from the video file uploaded by the user.
2. The extracted audio should be of high quality and free of any distortion.
3. The extracted audio should be in the proper format that can be consumed by the next component of the system.

### Implementation Details

1. This functionality can be implemented using FFmpeg, which is a powerful open-source multimedia framework capable of audio and video format conversions.
2. The extracted audio can be stored as a separate file in the file system or in a cloud-based storage service like Amazon S3 or Google Cloud Storage.
3. The extracted audio can be passed on to the next component of the system, which is the Audio Translation Processing.

## User Story 8: Facial Tracking

### Description

The application should track the facial movements in the video uploaded by the user.

### DoD

1. The application should accurately track the facial movements in the video.
2. The facial tracking information should be of high quality and free of any distortion.
3. The facial tracking information should be stored in a format that can be consumed by other components of the system.

### Implementation Details

1. This functionality can be implemented using computer vision techniques like OpenCV.
2. The application should detect the faces in the video and then track their movements over time.
3. The tracking information can be stored in a database for future use.

## User Story 9: Pre/Post Processing

### Description

The application should perform any pre-processing or post-processing necessary to enhance the quality of the audio and video.

### DoD

1. The application should perform any necessary pre-processing or post-processing on the audio and video.
2. The pre-processing and post-processing should enhance the quality of the audio and video.
3. The pre-processing and post-processing should be performed in a manner that does not cause any distortion or degradation in the audio and video quality.

### Implementation Details

1. This functionality can be implemented using various audio and video processing techniques like noise reduction, gain adjustment, etc.
2. The pre-processing step can be used to enhance the quality of the audio and video before it undergoes translation.
3. The post-processing step can be used to further enhance the quality of the audio and video after it has been translated.

## User Story 10: Separate Music and Speech from Video Input

### Description

The user will provide a audio as input, and the application should be able to separate the music and speech from the given audio.

### DoD

The audio files separated from the input should be able to play as separate audio files.

### Implementation Details

1. To separate the music and speech from the audio, we can use techniques like source separation.
2. Source separation is a technique used to separate an audio mixture into individual source signals.
3. We can use existing models for this purpose, for example, Open-Unmix.

### Steps

1. Accept the audio input from the user.
2. Pass the audio input through a source separation algorithm to separate the music and speech.
3. Store the separated audio files.

### Tech Stack

1. Python programming language.
2. Open-Unmix, a source separation algorithm.

## User Story 11: Determine Positions of Speech in Audio

### Description

The application should determine the positions of speech in the audio.

### DoD

The positions of speech in the audio should be accurately determined.

### Implementation Details

1. To determine the positions of speech in the audio, we can use speech activity detection (SAD) algorithms.
2. The SAD algorithm takes audio as input and outputs a segment of speech and non-speech.

### Steps

1. Accept the separated audio file from User Story #10.
2. Pass the audio file through a SAD algorithm to determine the positions of speech in the audio.
3. Store the positions of speech in the audio.

### Tech Stack

1. Python programming language.
2. An SAD algorithm, for example, webrtcvad.

## User Story 12: Audio Speech Translation

### Description

1. The user will provide the input speech audio.
2. The component will use machine learning models to identify and translate the speech into the desired language.
3. The component should handle pre-processing of the audio to improve translation accuracy.
4. The component should use Text-to-Speech technology to convert the translated text back to speech.

### DoD

1. The audio speech should be accurately recognized and transcribed into text.
2. The text should be accurately translated to the target language.
3. The text-to-speech output should sound natural and have correct pronunciation.

### Implementation Details

1. **Pre-processing:** The audio will be pre-processed to remove background noise and improve audio quality for speech recognition.
2. **Speech Recognition:** The audio speech will be recognized and transcribed into text.
3. **Text Translation:** The transcribed text will be translated to the target language.
4. **Text-to-Speech:** The translated text will be transformed into speech using Text-to-Speech technology.
5. **Post-processing:** The final audio will be post-processed to improve audio quality and volume.

### Tech Stack

1. Tensorflow or PyTorch for Pre-processing and Speech Recognition models.
2. Google Cloud Translation API or OpenNMT for Text Translation
3. gTTS (Google Text-to-Speech) for Text-to-Speech conversion.

## User Story 13: Overlay Music with Translated Speech

### Description

1. The component will overlay the translated speech with the background music.
2. The component should handle pre-processing of the audio to improve accuracy.

### DoD

1. The translated speech should be overlaid with the background music seamlessly.
2. The final audio should have good audio quality and volume.

### Implementation Details

1. **Pre-processing:** The audio will be pre-processed to remove background noise and improve audio quality.
2. **Overlay:** The translated speech will be overlaid with the background music.
3. **Post-processing:** The final audio will be post-processed to improve audio quality and volume.

### Tech Stack

1. OpenCV or MoviePy for Overlaying audio.
2. Librosa or Pydub for Post-processing.

## User Story 14: Detect Emotions in Video

### Description

1. The first step in this feature is to detect emotions from the facial expressions in the video.
2. This will be achieved through the use of computer vision and machine learning algorithms.
3. The system will process the video frame by frame, extract features from each frame, and use
those features to predict the emotional state of the person in the frame.

### DoD

The system should accurately detect emotions from the facial expressions in the video.

### Implementation Details

1. Use OpenCV for video frame processing.
2. Use pre-trained deep learning models like VGG-Face, Facenet, etc. to extract features from the frames.
3. Train a machine learning model on an annotated dataset of emotions to predict the emotional state of the person in each frame.

### Techstack

1. OpenCV
2. Tensorflow, Keras or PyTorch for deep learning models
3. Annotated dataset for emotion recognition

## User Story 15: Lip Syncing with Audio Translation

### Description

1. Once the emotions have been detected, the system will then sync the lip movements in the video with the audio translation.
2. This will be achieved by processing the audio, extracting speech information, and using it to control the movement of the lips in the video.

### DoD

The lip movements in the video should be synced with the audio translation, providing a more natural and realistic translation experience.

### Implementation Details

1. Use computer vision techniques to detect the lips in the video and track their movement.
2. Use the speech information to control the movement of the lips in the video.

### Techstack

1. OpenCV for computer vision techniques
2. Machine learning algorithms for lip movement prediction based on speech information
