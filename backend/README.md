# Backend

This directory contains the backend application for the Vote Oasis project.

## Overview

The backend is a Python-based application built using Flask. It provides an API endpoint for retrieving comments from YouTube videos.

## Dependencies

The backend application's dependencies are managed by `uv` and are listed in the `uv.lock` file.

## Getting Started

Some tools are managed by `mise`, which loads environment variables from `.env.development`.

1.  Navigate to the `backend/` directory.
2.  Create a virtual environment: `uv venv`
3.  Activate the virtual environment: `source .venv/bin/activate`
4.  Install the dependencies: `uv pip install -r requirements.txt`
5.  Run the application: `python app.py`

## API Endpoints

The backend application provides the following API endpoint:

*   `/get_youtube_comments`: This endpoint retrieves comments from a YouTube video. It accepts a `youtube_id` parameter in the request body.

## Docker

A Dockerfile is provided to build a Docker image for the backend application. To build the image, run the following command, ensuring that the `YOUTUBE_API_KEY` environment variable is set during the build process:

`docker build --build-arg YOUTUBE_API_KEY=$YOUTUBE_API_KEY -t backend .`

To run the container, run the following command:

`docker run -p 5000:5000 backend`
