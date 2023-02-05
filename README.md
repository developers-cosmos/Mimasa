# Mimasa - EmoteTrans [A Real-time Multilingual Face Translator] [![Build Python Package](https://github.com/developers-cosmos/Mimasa/actions/workflows/python-build.yml/badge.svg?branch=main)](https://github.com/developers-cosmos/Mimasa/actions/workflows/python-build.yml) [![Release](https://github.com/developers-cosmos/Mimasa/actions/workflows/release.yml/badge.svg)](https://github.com/developers-cosmos/Mimasa/actions/workflows/release.yml)

## Overview

The idea behind Mimasa is to provide a seamless translation experience for people who are communicating with individuals who speak different languages. The application uses advanced computer vision and machine learning techniques to detect and track the facial movements and speech of a person in real-time, and then uses natural language processing (NLP) to translate the speech to another language. The output audio is then synced with the facial movements of the person to provide a more natural and realistic translation experience. Additionally, Mimasa can also separate the music and speech from the video input, which allows for a more accurate translation experience. Overall, Mimasa aims to bridge the language barrier and make communication between people of different languages easier and more efficient.

## Announcement

For the latest updates and news regarding Mimasa, please follow the [Announcement thread](https://github.com/developers-cosmos/Mimasa/discussions/categories/announcements) on our Github repository.

**[Call for Support and Ideas for Mimasa Application](https://github.com/developers-cosmos/Mimasa/discussions/11)**

## Table of Contents

- [Idea](./docs/idea/concept.md)
  - [Detailed Steps](./docs/docs/idea/concept.md/#steps)
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

[![Project Status: Concept – Minimal or no implementation has been done yet.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)

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
ip install -r requirements.txt
```

6.Launch the Mimasa application.

```shell
python src/main.py
```

7.Congratulations! You have successfully installed Mimasa on your local machine.

### Troubleshooting

If you encounter any issues during the installation process, please refer to the [issues](https://github.com/developers-cosmos/Mimasa/issues) section of the Mimasa repository. If your issue is not already reported, feel free to create a new issue with a detailed description of the problem.

## Under Development

Mimasa is still in concept stage and requires planning to finalize the concept & start the development.

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

Thank you!
