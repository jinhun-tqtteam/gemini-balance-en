# Gemini Balance - Gemini API Proxy and Load Balancer

## Project Overview

Gemini Balance is a Python FastAPI application that serves as a proxy and load balancer for the Google Gemini API. It enables users to manage multiple Gemini API Keys, implement key rotation, and handle authentication. The application also supports proxying requests in the OpenAI API format, making it compatible with a wider range of tools and services. Key features include:

*   **Multi-Key Load Balancing:** Automatically rotates through a list of Gemini API keys.
*   **Dual API Compatibility:** Supports both Gemini and OpenAI `v1/chat/completions` API endpoints.
*   **Image Generation:** Includes capabilities for image generation and hosting.
*   **Status Monitoring:** Provides a dashboard to monitor the status of API keys.
*   **Configuration:** Can be configured via a `.env` file or environment variables.

The project is built with Python 3.9+ and FastAPI, and it can be deployed using Docker or run locally.

## Building and Running

### Local Development

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Environment:**
    Create a `.env` file based on `.env.example` and populate it with your Gemini API keys and other settings.
3.  **Run the Application:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

### Docker

1.  **Build the Docker Image:**
    ```bash
    docker build -t gemini-balance .
    ```
2.  **Run with Docker Compose:**
    ```bash
    docker-compose up -d
    ```
    (Ensure your `.env` file is configured, especially for database settings if you are using MySQL).

### Testing

The project does not appear to have a dedicated test suite in the `tests` directory. To verify functionality, you can use the provided API endpoints.

## Development Conventions

*   **Code Style:** The project follows standard Python coding conventions (PEP 8).
*   **Configuration:** Application settings are managed through `app/config/config.py` and loaded from environment variables or a `.env` file.
*   **Modularity:** The application is structured into modules for different functionalities (e.g., `database`, `router`, `service`).
*   **API Versioning:** The API endpoints are versioned (e.g., `/gemini/v1beta`, `/openai/v1`).
*   **Contributing:** The `README.md` encourages contributions via Pull Requests and Issues.
