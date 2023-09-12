# Change Log

All notable changes to this package will be documented in this file.
This package adheres to [Semantic Versioning](http://semver.org/).

## 1.1.0 release

### Features

* Add Django App for Mimasa to perform translations
* Add asynchronous functionality to detect faces and separate audio
* Add translation units for mimasa app and video, audio interfaces
* Improve face detection performance with asynchronous approaches added

### Documentation

* Document expected features and stories
* Document performance results

### Bug Fixes

* Fix labeler workflow for PRs
* Added tests results for performance of face detection & audio separation
* Prepare a demo video for Mimasa Django App

## 1.0.0 release

### Features

* Initial implementation of Mimasa App with FaceDetector component implemented
* Implement AudioSeparator component with NUSSL Separator

### Documentation

* Design documentation is added including components relationship, mimasa-state behavior and sequence diagrams
* Prepared the concept of Mimasa Application
