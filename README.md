# WifiMage

![WifiMage Banner](https://i.imgur.com/d84YpdA.png)

## About
WifiMage is a powerful tool for managing wireless network interfaces on Linux systems. Developed to provide a user-friendly interface and advanced features for WiFi network administration.

## Features
- 🎯 Monitor and Managed Mode
- 📡 Network scanning
- 🔍 Real-time monitoring
- 🔒 Security analysis
- 🛠️ Connection diagnostics
- 💾 Save scan results
- 🎨 Colorful and intuitive interface

## Requirements
- Python 3.x
- Linux
- Superuser permissions (sudo)
- Python packages:
  - colorama

## Installation
```bash
# Clone the repository
git clone https://github.com/your-username/wifimage.git

# Enter the directory
cd wifimage

# Install dependencies
pip install -r requirements.txt

# Give execution permission
chmod +x wifimage.py
```

## Usage
```bash
# List available interfaces
python3 wifimage.py -l

# Show detailed interface information
python3 wifimage.py -i wlan0

# Set interface to monitor mode
python3 wifimage.py -mon wlan0

# Set interface to managed mode
python3 wifimage.py -man wmg0mon

# Scan available networks
python3 wifimage.py -s wlan0

# Monitor networks in real-time
python3 wifimage.py -rt wlan0

# Analyze interface security
python3 wifimage.py -sec wlan0

# Diagnose connection issues
python3 wifimage.py -d wlan0
```

## Available Options
- `-r, --rename`: Rename an interface
- `-mon, --monitor`: Set interface to monitor mode
- `-man, --managed`: Set interface to managed mode
- `-l, --list`: List available interfaces
- `-i, --info`: Show detailed interface information
- `-s, --scan`: Scan available networks
- `-save, --save-scan`: Save scan results
- `-rt, --realtime`: Start real-time monitoring
- `-sec, --security`: Analyze security settings
- `-d, --diagnose`: Diagnose connection issues

## Contributing
Contributions are welcome! Feel free to open issues or send pull requests.

## Author
- **Br3noAraujo** - [GitHub](https://github.com/your-username)

## Acknowledgments
- Python Community
- Library developers
- All project contributors 
