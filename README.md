# Action Recorder & Replayer

A powerful Python toolkit for recording and replaying keyboard and mouse actions. Perfect for automation, testing, demonstrations, training, and repetitive task automation.

## Features

### 🎥 Recording (`record.py`)
- **Real-time Recording**: Capture all keyboard and mouse actions with precise timing
- **Hotkey Controls**: Start/stop recording with customizable keyboard shortcuts
- **Smart Filtering**: Reduces noise by filtering insignificant mouse movements
- **Multiple Formats**: Save recordings as structured JSON files
- **Background Operation**: Continue recording while using other applications
- **Recording Management**: List, view, and organize multiple recordings

### 🎬 Replaying (`play.py`)
- **Precise Timing**: Maintains exact timing between actions from original recording
- **Speed Control**: Replay at any speed (0.1x to 10x)
- **Repetition Control**: Repeat recordings multiple times (1-100 repetitions)
- **Progress Tracking**: Real-time progress updates during playback
- **Flexible Input**: Support for command-line arguments and interactive mode
- **Safe Interruption**: Stop playback anytime with Ctrl+C

## Installation

### Prerequisites
- Python 3.6 or higher
- `pynput` library for cross-platform input control

### Setup
1. Clone this repository:
```bash
git clone https://github.com/yourusername/action-recorder-replayer.git
cd action-recorder-replayer
```

2. Install required dependencies:
```bash
pip install pynput
```

3. **Platform-specific permissions**:
   - **macOS**: Go to `System Preferences > Security & Privacy > Privacy > Accessibility` and add your Terminal/IDE
   - **Linux**: May require `sudo` or adding user to `input` group
   - **Windows**: Run as administrator if needed

## Quick Start

### Recording Actions

1. **Start the recorder**:
```bash
python record.py
```

2. **Begin recording**:
   - Press `Ctrl+Shift+R` to start recording
   - Perform your actions (keyboard typing, mouse clicks, movements)
   - Press `Ctrl+Alt+S` to stop recording (or `ESC` for emergency stop)

3. **Your recording** is automatically saved as `recordings/recording_YYYYMMDD_HHMMSS.json`

### Replaying Actions

1. **Command-line usage** (recommended):
```bash
python play.py recordings/your_recording.json
```

2. **Interactive mode**:
```bash
python play.py
# Enter file path when prompted
```

3. **Choose replay options**:
   - Quick replay (normal speed, once)
   - Custom speed and repetition settings
   - Analyze recording details

## Usage Examples

### Basic Recording Session
```bash
# Start recorder
python record.py

# In the program:
# 1. Choose "Start recording"
# 2. Press Ctrl+Shift+R when ready
# 3. Perform your actions
# 4. Press Ctrl+Alt+S to stop
```

### Flexible Replay Options
```bash
# Normal speed replay
python play.py my_recording.json

# Using program menu for custom settings:
# - Speed: 0.5x (half speed) to 10x (very fast)
# - Repetitions: 1 to 100 times
# - Real-time progress tracking
```

### Advanced Examples
```bash
# Record a complex workflow
python record.py
# Custom filename: "login_sequence.json"

# Replay for testing (slow and repeated)
python play.py recordings/login_sequence.json
# Settings: 0.5x speed, 5 repetitions

# Replay for demonstration (fast)
python play.py recordings/demo_actions.json  
# Settings: 2x speed, 1 repetition
```

## Use Cases

### 🎯 **Automation & Testing**
- Automate repetitive tasks
- Create test scenarios for applications  
- Regression testing workflows
- UI automation scripts

### 📚 **Training & Documentation**  
- Record software tutorials
- Create step-by-step demonstrations
- Training material for new users
- Document complex procedures

### 🎮 **Gaming & Entertainment**
- Record gaming sequences
- Create macro commands
- Speedrun practice
- Consistent input patterns

### 💼 **Professional Workflows**
- Data entry automation
- Software demonstrations
- Quality assurance testing
- Process documentation

## File Format

Recordings are saved as JSON files with this structure:
```json
{
  "recording_info": {
    "start_time": "2025-01-15T10:30:00",
    "duration": 45.67,
    "total_actions": 234
  },
  "actions": [
    {
      "type": "key_press",
      "timestamp": 1.234,
      "key": "a",
      "modifiers": ["ctrl"]
    },
    {
      "type": "mouse_click", 
      "timestamp": 2.456,
      "x": 500,
      "y": 300,
      "button": "left",
      "pressed": true
    }
  ]
}
```

## Keyboard Shortcuts

### During Recording
- `Ctrl+Shift+R` - Start recording
- `Ctrl+Alt+S` - Stop recording  
- `ESC` - Emergency stop
- `Ctrl+C` - Force quit program

### During Replay
- `Ctrl+C` - Stop current replay
- Menu navigation with number keys

## Command-Line Reference

### record.py
```bash
python record.py
# Interactive mode with menu options
# Recordings saved to ./recordings/ by default
```

### play.py  
```bash
python play.py <json_file>

# Examples:
python play.py recording.json
python play.py recordings/my_session.json
python play.py "C:\My Files\automation.json"
```

## Troubleshooting

### Common Issues

**Permission Denied**: 
- Ensure accessibility permissions are granted (see Installation section)
- Try running with elevated privileges

**Recording Not Starting**:
- Check that hotkey combination `Ctrl+Shift+R` is pressed correctly
- Verify no other applications are intercepting these keys

**Replay Actions Not Working**:
- Confirm the target application is in focus
- Check that screen resolution matches recording environment
- Verify JSON file is not corrupted

**High CPU Usage During Recording**:
- Mouse movement recording is optimized, but very active usage may increase CPU
- Consider shorter recording sessions for high-activity workflows

### Performance Tips
- Close unnecessary applications during recording/replay
- Use SSD storage for better file I/O performance
- Shorter recordings (< 5 minutes) work best for complex sequences

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v2.0
- ✅ Added custom speed control (0.1x - 10x)
- ✅ Multiple repetition support (1-100x)
- ✅ Command-line argument support
- ✅ Enhanced progress tracking
- ✅ Improved error handling
- ✅ Better cross-platform compatibility

### v1.0
- ✅ Basic recording and replay functionality
- ✅ JSON file format
- ✅ Hotkey controls
- ✅ Mouse and keyboard support

## Acknowledgments

- Built with [pynput](https://github.com/moses-palmer/pynput) for cross-platform input handling
- Inspired by automation needs in software testing and training environments
- This project is collaboration with Claude Sonnet 4
