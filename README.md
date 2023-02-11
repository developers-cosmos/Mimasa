# [Mimasa - EmoteTrans [A Real-time Multilingual Face Translator]](https://github.com/developers-cosmos/Mimasa) [![Build Python Package](https://github.com/developers-cosmos/Mimasa/actions/workflows/python-build.yml/badge.svg?branch=main)](https://github.com/developers-cosmos/Mimasa/actions/workflows/python-build.yml) [![Release](https://github.com/developers-cosmos/Mimasa/actions/workflows/release.yml/badge.svg)](https://github.com/developers-cosmos/Mimasa/actions/workflows/release.yml)

## Overview

The idea behind Mimasa is to provide a seamless translation experience for people who are communicating with individuals who speak different languages. The application uses advanced computer vision and machine learning techniques to detect and track the facial movements and speech of a person in real-time, and then uses natural language processing (NLP) to translate the speech to another language. The output audio is then synced with the facial movements of the person to provide a more natural and realistic translation experience. Additionally, Mimasa can also separate the music and speech from the video input, which allows for a more accurate translation experience. Overall, Mimasa aims to bridge the language barrier and make communication between people of different languages easier and more efficient.

## Announcement

For the latest updates and news regarding Mimasa, please follow the [Announcement thread](https://github.com/developers-cosmos/Mimasa/discussions/categories/announcements) on our Github repository.

**[Call for Support and Ideas for Mimasa Application](https://github.com/developers-cosmos/Mimasa/discussions/11)**

## Table of Contents

- [Idea](./docs/idea/concept.md)
  - [Detailed Steps](./docs/idea/concept.md/#steps)
  - [Tools & Technologies](./docs/idea/concept.md/#tools--technologies)
  - [Steps With Examples](./docs/idea/concept.md/#overview)
- [Design](./docs/design/DESIGN.md)
  - [Mimasa Components](./docs/design/DESIGN.md/#design-of-mimasa-components)
    - [User Interaction](./docs/design/DESIGN.md#user-uploading-video--requesting-translation)
    - [Video Translation - Part 1](./docs/design/DESIGN.md/#video-translation---part-1)
    - [Video Translation - Part 2](./docs/design/DESIGN.md/#video-translation---part-2)
  - [Components & their Relationship](./docs/design/DESIGN.md#design-of-components)
  - [Mimasa State Behavior](./docs/design/DESIGN.md#mimasa-state-behavior)

## Status

[![Project Status: WIP – Initial development is in progress.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Installation Guide

### Prerequisites

- [Python 3.10.x](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installation/)
- Update the [settings](https://github.com/developers-cosmos/Mimasa/blob/main/src/common/config.py) for the application

### Steps

1. Clone the repository:

```bash
git clone https://github.com/developers-cosmos/Mimasa.git
```

2.Navigate to the cloned repository directory.

```bash
cd Mimasa
```

3.Create a virtual environment.

```bash
python3 -m venv venv
```

4.Activate the virtual environment.

```bash
source venv/bin/activate
```

5.Install the required packages using pip.

```shell
pip install -r requirements.txt
```

6.Launch the Mimasa application.

```shell
python src/main.py
```

7.Congratulations! You have successfully installed Mimasa on your local machine.

## Django App Installation Guide for Mimasa

The Django app for Mimasa is a web-based application that allows users to interact with the Mimasa EmoteTrans Translation unit and perform real-time multilingual face translations. In this guide, we will walk through the steps required to install and run the Mimasa Django app on your local machine.

**NOTE:** Please note that the current implementation is only demo and not all components will work properly

### Prerequisites

- Python 3.10.x
- pip
- Django 4.x
- Redis
- Celery

### Steps

After following the above steps to setup Mimasa locally, you will need to install the following:

1. Run the migrations

```shell
python src/api/mimasa/manage.py makemigrations
python src/api/mimasa/manage.py migrate
```

2. Run the Django server

```shell
python src/api/mimasa/manage.py runserver
```

3. Download the Redis ZIP archive from the official Redis website (https://github.com/microsoftarchive/redis/releases)

4. Extract the contents of the ZIP archive to a folder of your choice. Open the Command Prompt and navigate to the folder where you extracted Redis.
Run the following command to start Redis:

```shell
redis-server.exe redis.windows.conf
```

5. Open another Command Prompt window and navigate to the same folder. Run the following command to start the Redis CLI.

```shell
redis-cli.exe
```

6. Next step is to start celery worker to perform transaction tasks for Mimasa.
Run the following command to start a Celery worker:

```shell
cd src/api/mimasa
celery -A mimasa worker -l info -P eventlet
```

7. Congratulations! You have successfully completed the setup for Mimasa Django App, now you can perform translations at http:localhost:8000

### Troubleshooting

If you encounter any issues during the installation process, please refer to the [issues](https://github.com/developers-cosmos/Mimasa/issues) section of the Mimasa repository. If your issue is not already reported, feel free to create a new issue with a detailed description of the problem.

## Demo

A demo of the Mimasa Django App (from Mimasa v1.1.0) can be seen from below link: [Mimasa -EmoteTrans Django App Demo Setup](https://drive.google.com/file/d/1uG8pZMbJExo8oxWyOHEuLonoIt1pZ99S/view?usp=sharing). This demo version provides a limited functionality of the actual application, but should give you an idea of how the application works.

<a href="https://drive.google.com/file/d/1uG8pZMbJExo8oxWyOHEuLonoIt1pZ99S/view">
  <img src="data/images/mimasa-logo.png" alt="Mimasa - EmoteTrans Django App Demo Setup" width="250" height="250">
</a>

## Under Development

Mimasa is still under development and some features may not be fully functional.

## Contribution

We welcome any contributions to the project. If you're interested in making a contribution, follow these steps:

If you're interested in making a contribution, follow these steps:

1. Fork the repository to your own GitHub account
2. Clone the forked repository to your local machine
3. Create a branch for the feature or bug fix you want to work on
4. Make changes and commit them to your branch
5. Push your changes to your forked repository
6. Create a pull request to the main repository for review and merge

## Contact Information

We appreciate your interest in Mimasa Application and welcome any questions or feedback you may have. You can reach us through the following channels:

- Email: ritheeshbaradwaj@gmail.com
- [GitHub Issues](https://github.com/developers-cosmos/Mimasa/issues)

## Thank you
