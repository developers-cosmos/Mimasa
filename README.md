# Mimasa - EmoteTrans [A Real-time Multilingual Face Translator] [![Build Github Pages](https://github.com/developers-cosmos/Mimasa/actions/workflows/pages.yml/badge.svg)](https://github.com/developers-cosmos/Mimasa/actions/workflows/pages.yml)

## Overview

The idea behind Mimasa is to provide a seamless translation experience for people who are communicating with individuals who speak different languages. The application uses advanced computer vision and machine learning techniques to detect and track the facial movements and speech of a person in real-time, and then uses natural language processing (NLP) to translate the speech to another language. The output audio is then synced with the facial movements of the person to provide a more natural and realistic translation experience. Additionally, Mimasa can also separate the music and speech from the video input, which allows for a more accurate translation experience. Overall, Mimasa aims to bridge the language barrier and make communication between people of different languages easier and more efficient.

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

We welcome any contributions to the project. If you would like to contribute, please fork the repository and make changes as you see fit. Once you are done, you can submit a pull request and we will review your changes. Email: ritheeshbaradwaj@gmail.com
