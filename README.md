# Steam Deals Finder 🎮

A Python desktop application that searches for Steam game deals and sends automated email notifications when new discounts are available. Features a modern GUI built with CustomTkinter, intelligent duplicate detection, and daily scheduled searches.

<img width="1175" height="993" alt="image" src="https://github.com/user-attachments/assets/aecd26f7-c2a8-4249-b1fd-82c9feac22d9" />

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features ✨

- 🔍 **Smart Search**: Search Steam store for games with customizable minimum discount percentages (0-100%)
- 📧 **Multi-Recipient Emails**: Send personalized deal notifications to multiple email addresses
- 🤖 **Intelligent Filtering**: Only sends emails for new or changed deals - no duplicate notifications
- ⏰ **Daily Scheduler**: Automated daily searches at your preferred time
- 🎯 **Per-Recipient Tracking**: Each recipient has their own deal history for personalized notifications
- 👁️ **Secure Credentials**: Built-in password visibility toggle for secure credential management
- 🖱️ **Smooth Scrolling**: Mouse wheel support for easy navigation
- 💾 **Persistent Storage**: JSON-based tracking system for game deals

## Screenshots 📸

The application features a clean two-column layout:
- **Left Panel**: Discount slider, search button, and scrollable results
- **Right Panel**: Email credentials, recipient management, and daily scheduler

## Prerequisites 📋

- **Python 3.8 or higher**
- **Gmail account** with App Password enabled (for sending emails)
- **Internet connection** (for scraping Steam and sending emails)

## Installation 🚀

### 1. Clone or Download the Repository

```bash
git clone https://github.com/Ludovico98/Steam-Deals-Finder.git
cd Steam-Deals-Finder
```

### 2. Install Python

#### **Windows**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and **check "Add Python to PATH"**
3. Verify installation:
   ```cmd
   python --version
   ```

#### **macOS**
1. Install using Homebrew (recommended):
   ```bash
   brew install python3
   ```
   Or download from [python.org](https://www.python.org/downloads/)
2. Verify installation:
   ```bash
   python3 --version
   ```

#### **Linux (Ubuntu/Debian)**
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
```

#### **Linux (Fedora/RHEL)**
```bash
sudo dnf install python3 python3-pip
python3 --version
```

### 3. Install Required Python Packages

Navigate to the project directory and install dependencies:

#### **Windows**
```cmd
pip install customtkinter requests beautifulsoup4
```

#### **macOS/Linux**
```bash
pip3 install customtkinter requests beautifulsoup4
```

### Required Dependencies:
- `customtkinter` - Modern UI framework
- `requests` - HTTP library for web scraping
- `beautifulsoup4` - HTML parsing for Steam store data

## Gmail App Password Setup 🔐

To send emails, you need a Gmail App Password (NOT your regular Gmail password).

### Step-by-Step Guide:

1. **Enable 2-Factor Authentication** (required for App Passwords):
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Under "How you sign in to Google", select **2-Step Verification**
   - Follow the setup process

2. **Generate an App Password**:
   - Visit [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Sign in if prompted
   - Select app: **Mail**
   - Select device: **Other (Custom name)** - enter "Steam Deals Finder"
   - Click **Generate**
   - Copy the 16-character password (remove spaces)

3. **Use in Application**:
   - Enter your full Gmail address (e.g., `youremail@gmail.com`)
   - Paste the 16-character App Password in the password field
   - Click the eye icon (👁️) to toggle password visibility if needed

### Important Notes:
- ⚠️ **Never use your regular Gmail password** - it won't work and may compromise security
- ⚠️ **Keep your App Password secure** - treat it like a password
- 📖 Full Guide: [Sign in with App Passwords - Google Account Help](https://support.google.com/accounts/answer/185833)

## Running the Application 🎯

### Windows
```cmd
cd Steam-Deals-Finder\SteamEmailSender\scripts
python UISteamSearch.py
```

### macOS/Linux
```bash
cd Steam-Deals-Finder/SteamEmailSender/scripts
python3 UISteamSearch.py
```

## Usage Guide 📖

### Basic Search
1. **Set Minimum Discount**: Use the slider to select your minimum discount percentage (0-100%)
2. **Enter Credentials**: 
   - Add your Gmail address
   - Enter your Gmail App Password
3. **Add Recipients**: Enter email addresses and click "➕ Add"
4. **Search**: Click "🔍📧 Search & Send Email"

### Daily Scheduler
1. **Set Time**: Enter hour (HH) and minute (MM) in 24-hour format (e.g., 14:30 for 2:30 PM)
2. **Activate**: Click "✅ Activate" to start daily automated searches
3. **Deactivate**: Click "🛑 Deactivate" to stop the scheduler

### How It Works
- **First Search**: All deals matching your criteria are sent via email
- **Subsequent Searches**: Only NEW deals or deals with CHANGED discounts are sent
- **Per-Recipient Tracking**: Each recipient gets personalized notifications based on their history
- **No Email Mode**: Search without recipients to browse deals (still tracks for future searches)

## Project Structure 📁

```
Steam-Deals-Finder/
├── SteamEmailSender/
│   ├── Email/
│   │   └── SendEmail.py           # Email sending & tracking
│   ├── Records/
│   │   └── RecordsGamesEmails     # JSON tracking file (auto-created)
│   └── scripts/
│       ├── UISteamSearch.py       # Main UI application
│       └── steam_search.py        # Steam scraping logic
└── README                         # This file
```

## Troubleshooting 🔧

### "Import Error: No module named 'customtkinter'"
**Solution**: Install missing package
```bash
pip3 install customtkinter
```

### "535 Bad Credentials" Email Error
**Solution**: 
- Ensure you're using Gmail App Password, NOT regular password
- Verify 2-Factor Authentication is enabled
- Generate a new App Password if needed

### "No games found"
**Solution**:
- Check your internet connection
- Try lowering the minimum discount percentage
- Steam's HTML structure may have changed (web scraping limitation)

### Application Won't Start
**Solution**:
- Verify Python version: `python3 --version` (should be 3.8+)
- Reinstall dependencies: `pip3 install --upgrade customtkinter requests beautifulsoup4`
- Check you're in the correct directory: `Steam-Deals-Finder/SteamEmailSender/scripts/`

### Scheduler Not Working
**Solution**:
- Verify time format is HH:MM in 24-hour format
- Check credentials are entered before activating
- Ensure at least one recipient email is added

## Data Privacy & Security 🔒

- **No Data Collection**: All data stays local on your machine
- **Credentials**: Stored in memory only while application runs (not saved to disk)
- **Game Tracking**: Stored locally in `SteamEmailSender/Records/RecordsGamesEmails` JSON file
- **Email Security**: Uses TLS encryption (port 587) for Gmail SMTP

## Limitations ⚠️

- **Web Scraping**: Relies on Steam's current HTML structure; may break if Steam updates their site
- **Gmail Only**: Currently configured for Gmail SMTP (port 587)
- **Rate Limiting**: Steam may rate-limit requests if searching too frequently
- **Deal Limit**: Fetches up to 50 games per search

## Future Enhancements 💡

Potential improvements for future versions:
- Price range filtering
- Wishlist integration
- Database storage instead of JSON
- Steam API integration (more reliable than web scraping)
- HTML email templates with images
- Adding a pubsub

## Contributing 🤝

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer ⚖️

This application uses web scraping to gather Steam store data. Use responsibly and in accordance with Steam's Terms of Service. The developers are not responsible for any misuse or violations.

## Support 💬

Having issues? Check the Troubleshooting section above or open an issue in the repository.

---

**Happy Gaming!** 🎮 Enjoy finding the best Steam deals!
