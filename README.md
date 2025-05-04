# ContentMaster AI

ContentMaster AI is a sleek web interface for analyzing content using the Fabric CLI tool. It provides an intuitive way to extract insights, summaries, and other valuable information from both YouTube videos and text content.

## Features

- **Beautiful UI**: Clean, modern interface with an excellent user experience
- **Content Analysis**: Process YouTube videos and text with various analysis patterns
- **Multiple Analysis Types**: Executive summaries, key points, insights, action steps, and more
- **Multi-language Support**: Analyze content in English, German, French, Spanish, and Italian
- **User Authentication**: Secure login system
- **Persistent Storage**: User data stored in a Docker volume
- **Easy Deployment**: Simple Docker setup with docker-compose

## Screenshot

![ContentMaster AI Screenshot](https://example.com/contentmaster-screenshot.png)

## Simplified Architecture

ContentMaster has been streamlined for simplicity while maintaining all functionality:

- **Single Flask Application**: All processing is handled directly by Flask
- **No Microservices**: Removed the separate FastAPI component for simpler maintenance
- **Direct Command Execution**: Fabric CLI commands execute directly within the container
- **Containerized**: Easy deployment with Docker or docker-compose

## Quick Start

The easiest way to run ContentMaster is with Docker Compose:

```bash
# Clone the repository
git clone https://github.com/yourusername/contentmaster.git
cd contentmaster

# Start the application
docker-compose up -d

# Access the application at http://localhost:8700
```

## Default Credentials

The application comes with three default users:
- Username: `admin`, Password: `IamAdmin2411`
- Username: `Arezou`, Password: `123Arezou456`
- Username: `Jalal`, Password: `147Jalal369`

**Important**: For production use, change these default credentials.

## Manual Setup

If you prefer to run without Docker:

1. Install system dependencies:
   - Python 3.9+
   - Go (for Fabric CLI)

2. Install Fabric CLI:
   ```bash
   go install github.com/danielmiessler/fabric@latest
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Run the Flask application:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8700 app:app
   ```

## Project Structure

```
contentmaster/
├── app.py                  # Main Flask application
├── db_handler.py           # Database models and helper functions
├── init_db.py              # Database initialization script
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base template with common elements
│   ├── index.html          # Main application interface
│   └── login.html          # Login page
└── static/                 # Static files (CSS, JS, etc.)
```

## Environment Variables

- `FLASK_ENV`: Set to 'production' for production, 'development' for dev mode
- `SECRET_KEY`: Secret key for session security (auto-generated if not provided)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgments

- [Fabric CLI](https://github.com/danielmiessler/fabric) for content analysis
- [Flask](https://flask.palletsprojects.com/) web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components