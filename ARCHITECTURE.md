# Relaylist Setup Guide

Complete installation and setup instructions for Relaylist.

## System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Internet**: Required for Spotify API access

## Installation Steps

### 1. Python Installation

#### Windows
```bash
# Download from python.org or use Chocolatey
choco install python --version=3.11.0
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/relaylist.git
cd relaylist
```

### 3. Create Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Download NLTK Data

Run Python and execute:
```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
```

Or run this one-liner:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 6. Configure Spotify API

Follow the [API Setup Guide](API_SETUP.md) to:
1. Create a Spotify Developer account
2. Register your application
3. Get API credentials
4. Set up environment variables

### 7. Initialize Database

```bash
python -c "from utils.database import init_database; init_database()"
```

### 8. Run Application

```bash
streamlit run Home_Page.py
```

The app should open in your browser at `http://localhost:8501`

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError

**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. NLTK Data Not Found

**Problem**: `LookupError: Resource punkt not found`

**Solution**:
```python
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
```

#### 3. Spotify Authentication Failed

**Problem**: `ValueError: Spotify credentials not found!`

**Solution**:
1. Verify `.env` file exists in project root
2. Check credentials are correct
3. Ensure no extra spaces or quotes
4. See [API Setup Guide](API_SETUP.md)

#### 4. Port Already in Use

**Problem**: `Port 8501 is already in use`

**Solution**:
```bash
# Use different port
streamlit run Home_Page.py --server.port 8502

# Or kill process on port 8501
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8501 | xargs kill -9
```

#### 5. CSV Parsing Errors

**Problem**: `ValueError: CSV must contain columns: ...`

**Solution**:
- Verify CSV has required columns: Type, Date, Name / Number, Sender, Content
- Check date format matches: `M/D/YYYY H:MM`
- Ensure UTF-8 encoding
- Remove any header rows above column names

## Directory Structure

After setup, your project should look like:

```
relaylist/
├── venv/                    # Virtual environment (not in git)
├── data/                    # Database storage (not in git)
│   └── relaylist.db
├── .env                     # Environment variables (not in git)
├── .spotify_cache          # Spotify auth cache (not in git)
└── [other project files]
```

## Configuration Options

### Streamlit Configuration

Create `.streamlit/config.toml` for custom settings:

```toml
[theme]
primaryColor = "#1DB954"
backgroundColor = "#121212"
secondaryBackgroundColor = "#181818"
textColor = "#FFFFFF"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 50
```

### Environment Variables

Available options in `.env`:

```env
# Required
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
SPOTIFY_REDIRECT_URI=http://localhost:8501/callback

# Optional
DATABASE_PATH=data/relaylist.db
DEBUG_MODE=False
MAX_FILE_SIZE_MB=50
ENABLE_ANALYTICS=False
```

## Development Setup

For development with hot-reloading:

```bash
streamlit run Home_Page.py --server.runOnSave true
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

## Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets in dashboard:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REDIRECT_URI`

### Docker (Optional)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Home_Page.py"]
```

Build and run:
```bash
docker build -t relaylist .
docker run -p 8501:8501 --env-file .env relaylist
```

## Performance Optimization

### For Large Conversations

1. **Increase memory limit**:
```bash
streamlit run Home_Page.py --server.maxUploadSize 200
```

2. **Use chunked processing**:
   - App automatically handles large files
   - Processes messages in batches

3. **Cache results**:
   - Analysis cached in SQLite database
   - Spotify API responses cached

## Security Best Practices

1. **Never commit sensitive data**:
   - Add `.env` to `.gitignore`
   - Use environment variables for secrets

2. **Validate user input**:
   - CSV files validated before processing
   - File size limits enforced

3. **API key rotation**:
   - Rotate Spotify credentials periodically
   - Revoke unused apps from dashboard

## Getting Help

- **Documentation**: Check `/docs` folder
- **Issues**: GitHub Issues page
- **Community**: Discussions tab
- **Email**: your-email@example.com

## Next Steps

After setup:
1. Read [Usage Guide](USAGE.md)
2. Review [Architecture Documentation](ARCHITECTURE.md)
3. Try the example conversation in `/examples`
4. Explore customization options

## Updating

To update to latest version:

```bash
git pull origin main
pip install -r requirements.txt --upgrade
python -c "from utils.database import init_database; init_database()"
streamlit run Home_Page.py
```

---

**Need help?** Open an issue on GitHub or consult the documentation.