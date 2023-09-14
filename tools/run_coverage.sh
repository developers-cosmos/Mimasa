#!/bin/bash

coverage run src/api/mimasa/manage.py test face_detection
coverage html
