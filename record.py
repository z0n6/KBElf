import json
import time
import threading
import os
from datetime import datetime
from pathlib import Path
from pynput import keyboard, mouse
from pynput.keyboard import Key
from pynput.mouse import Button

class ActionRecorder:
    def __init__(self, output_dir="recordings", output_file=None):
        self.output_dir = Path(output_dir)
        self.output_file = output_file
        self.actions = []
        self.start_time = None
        self.recording = False
        self.keyboard_listener = None
        self.mouse_listener = None
        self.pressed_keys = set()
        self.stop_requested = False
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def start_recording(self):
        """Start recording keyboard and mouse actions"""
        print("Starting recording...")
        print("Press Ctrl+Alt+S to stop recording")
        print("Or press ESC as emergency stop")
        print("You can now switch to other applications - recording will continue in background")
        
        self.recording = True
        self.stop_requested = False
        self.start_time = time.time()
        self.actions = []
        self.pressed_keys = set()
        
        try:
            # Create listeners with suppress=False to allow normal operation
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release,
                suppress=False  # Don't suppress normal key behavior
            )
            
            self.mouse_listener = mouse.Listener(
                on_click=self.on_mouse_click,
                on_move=self.on_mouse_move,
                on_scroll=self.on_mouse_scroll,
                suppress=False  # Don't suppress normal mouse behavior
            )
            
            # Start listeners in daemon mode
            self.keyboard_listener.daemon = True
            self.mouse_listener.daemon = True
            self.keyboard_listener.start()
            self.mouse_listener.start()
            
            # Keep recording until stop is requested
            print("Recording started! Listening for events...")
            while self.recording and not self.stop_requested:
                time.sleep(0.1)
                # Check if listeners are still running
                if not (self.keyboard_listener.running or self.mouse_listener.running):
                    break
                
        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self.stop_recording()
    
    def stop_recording(self):
        """Stop recording and save to file"""
        if self.recording:
            self.recording = False
            
            # Stop listeners safely
            if self.keyboard_listener and self.keyboard_listener.running:
                self.keyboard_listener.stop()
            if self.mouse_listener and self.mouse_listener.running:
                self.mouse_listener.stop()
            
            self.save_actions()
            print(f"\nRecording stopped. Actions saved to {self.get_output_filepath()}")
            print(f"Total actions recorded: {len(self.actions)}")
    
    def get_output_filepath(self):
        """Generate output file path"""
        if self.output_file:
            # Use custom filename if provided
            filename = self.output_file
        else:
            # Generate filename with timestamp
            timestamp = datetime.fromtimestamp(self.start_time).strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.json"
        
        return self.output_dir / filename
    
    def get_timestamp(self):
        """Get timestamp relative to start time"""
        return time.time() - self.start_time if self.start_time else 0
        """Get timestamp relative to start time"""
        return time.time() - self.start_time if self.start_time else 0
    
    def on_key_press(self, key):
        """Handle key press events"""
        if not self.recording:
            return
        
        try:
            # Track pressed keys
            self.pressed_keys.add(key)
            
            # Check for stop combination: Ctrl+Alt+S
            ctrl_pressed = any(k in self.pressed_keys for k in [Key.ctrl_l, Key.ctrl_r, Key.ctrl])
            alt_pressed = any(k in self.pressed_keys for k in [Key.alt_l, Key.alt_r, Key.alt])
            s_pressed = (hasattr(key, 'char') and key.char and key.char.lower() == 's') or key == Key.esc
            
            # Also check if 's' was pressed recently
            if not s_pressed:
                s_pressed = any(hasattr(k, 'char') and k.char and k.char.lower() == 's' for k in self.pressed_keys)
            
            if ctrl_pressed and alt_pressed and s_pressed:
                print(f"\nStop combination detected! Stopping recording...")
                self.stop_requested = True
                return False  # Stop the listener
            
            # Alternative: ESC key as emergency stop
            if key == Key.esc:
                esc_count = sum(1 for k in self.pressed_keys if k == Key.esc)
                if esc_count >= 1:  # Single ESC press
                    print(f"\nESC pressed - Stopping recording...")
                    self.stop_requested = True
                    return False
            
            # Record the key press
            action = {
                "type": "key_press",
                "timestamp": round(self.get_timestamp(), 3),
                "key": self.format_key(key),
                "modifiers": self.get_active_modifiers()
            }
            self.actions.append(action)
            
        except Exception as e:
            print(f"Error in key press handler: {e}")
    
    def on_key_release(self, key):
        """Handle key release events"""
        if not self.recording:
            return
        
        try:
            # Remove from pressed keys
            self.pressed_keys.discard(key)
            
            # Record the key release
            action = {
                "type": "key_release",
                "timestamp": round(self.get_timestamp(), 3),
                "key": self.format_key(key),
                "modifiers": self.get_active_modifiers()
            }
            self.actions.append(action)
            
        except Exception as e:
            print(f"Error in key release handler: {e}")
    
    def on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.recording:
            return
        
        try:
            action = {
                "type": "mouse_click",
                "timestamp": round(self.get_timestamp(), 3),
                "x": x,
                "y": y,
                "button": button.name,
                "pressed": pressed,
                "modifiers": self.get_active_modifiers()
            }
            self.actions.append(action)
            
        except Exception as e:
            print(f"Error in mouse click handler: {e}")
    
    def on_mouse_move(self, x, y):
        """Handle mouse move events"""
        if not self.recording:
            return
        
        try:
            # Only record significant movements to avoid too much data
            if (len(self.actions) == 0 or 
                self.actions[-1]["type"] != "mouse_move" or 
                abs(self.actions[-1]["x"] - x) > 10 or 
                abs(self.actions[-1]["y"] - y) > 10 or
                self.get_timestamp() - self.actions[-1]["timestamp"] > 0.5):
                
                action = {
                    "type": "mouse_move",
                    "timestamp": round(self.get_timestamp(), 3),
                    "x": x,
                    "y": y
                }
                self.actions.append(action)
                
        except Exception as e:
            print(f"Error in mouse move handler: {e}")
    
    def on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        if not self.recording:
            return
        
        try:
            action = {
                "type": "mouse_scroll",
                "timestamp": round(self.get_timestamp(), 3),
                "x": x,
                "y": y,
                "dx": dx,
                "dy": dy,
                "modifiers": self.get_active_modifiers()
            }
            self.actions.append(action)
            
        except Exception as e:
            print(f"Error in mouse scroll handler: {e}")
    
    def format_key(self, key):
        """Format key for JSON serialization"""
        try:
            if hasattr(key, 'char') and key.char is not None:
                return key.char
            else:
                return str(key).replace('Key.', '')
        except:
            return str(key)
    
    def get_active_modifiers(self):
        """Get currently active modifier keys"""
        modifiers = []
        modifier_keys = {
            Key.ctrl_l: 'ctrl', Key.ctrl_r: 'ctrl', Key.ctrl: 'ctrl',
            Key.alt_l: 'alt', Key.alt_r: 'alt', Key.alt: 'alt',
            Key.shift: 'shift', Key.shift_l: 'shift', Key.shift_r: 'shift',
            Key.cmd: 'cmd', Key.cmd_l: 'cmd', Key.cmd_r: 'cmd'
        }
        
        for key, name in modifier_keys.items():
            if key in self.pressed_keys and name not in modifiers:
                modifiers.append(name)
        
        return modifiers
    
    def save_actions(self):
        """Save recorded actions to JSON file"""
        end_time = time.time()
        output_path = self.get_output_filepath()
        
        data = {
            "recording_info": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(end_time).isoformat(),
                "duration": round(end_time - self.start_time, 2),
                "total_actions": len(self.actions),
                "output_file": str(output_path)
            },
            "actions": self.actions
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"File saved to: {output_path}")
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def load_actions(self, file_path=None):
        """Load actions from JSON file"""
        if file_path is None:
            # If no specific file, try to find the most recent recording
            try:
                json_files = list(self.output_dir.glob("*.json"))
                if not json_files:
                    print(f"No recording files found in {self.output_dir}")
                    return None
                # Get most recent file
                file_path = max(json_files, key=os.path.getctime)
                print(f"Loading most recent recording: {file_path}")
            except Exception as e:
                print(f"Error finding recordings: {e}")
                return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            print(f"File {file_path} not found")
            return None
        except json.JSONDecodeError:
            print(f"Invalid JSON in {file_path}")
            return None
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    
    def list_recordings(self):
        """List all recordings in the output directory"""
        try:
            json_files = list(self.output_dir.glob("*.json"))
            if not json_files:
                print(f"No recordings found in {self.output_dir}")
                return []
            
            recordings = []
            for file_path in sorted(json_files, key=os.path.getctime, reverse=True):
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        info = data.get('recording_info', {})
                        recordings.append({
                            'file': file_path,
                            'start_time': info.get('start_time', 'Unknown'),
                            'duration': info.get('duration', 0),
                            'actions': info.get('total_actions', 0)
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            
            return recordings
        except Exception as e:
            print(f"Error listing recordings: {e}")
            return []

def check_permissions():
    """Check if the program has necessary permissions"""
    print("Checking permissions...")
    try:
        # Try to create a temporary listener to test permissions
        def dummy_handler(*args):
            pass
        
        test_listener = keyboard.Listener(on_press=dummy_handler, on_release=dummy_handler)
        test_listener.start()
        time.sleep(0.1)
        test_listener.stop()
        print("✓ Keyboard permissions OK")
        
        test_listener = mouse.Listener(on_click=dummy_handler, on_move=dummy_handler)
        test_listener.start()
        time.sleep(0.1)
        test_listener.stop()
        print("✓ Mouse permissions OK")
        
        return True
    except Exception as e:
        print(f"✗ Permission error: {e}")
        print("\nPermission issues detected!")
        print("On macOS: Go to System Preferences > Security & Privacy > Privacy > Accessibility")
        print("          and add your Terminal/IDE to the allowed applications")
        print("On Linux: You may need to run with sudo or add your user to the input group")
        print("On Windows: Run as administrator if needed")
        return False

def main():
    print("Keyboard and Mouse Action Recorder v2.0")
    print("=====================================")
    
    if not check_permissions():
        input("\nPress Enter after fixing permissions to continue...")
    
    # Ask user for output directory
    print(f"\nDefault recordings directory: ./recordings")
    custom_dir = input("Enter custom directory path (or press Enter for default): ").strip()
    
    if custom_dir:
        recorder = ActionRecorder(output_dir=custom_dir)
        print(f"Using directory: {custom_dir}")
    else:
        recorder = ActionRecorder()
        print(f"Using directory: ./recordings")
    
    while True:
        print("\n1. Start recording")
        print("2. View recent recording")
        print("3. List all recordings")
        print("4. View specific recording")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            # Ask for custom filename (optional)
            custom_name = input("Enter custom filename (or press Enter for auto-generated): ").strip()
            if custom_name and not custom_name.endswith('.json'):
                custom_name += '.json'
            
            if custom_name:
                recorder.output_file = custom_name
            else:
                recorder.output_file = None
                
            print("\n" + "="*50)
            recorder.start_recording()
            print("="*50)
            
        elif choice == '2':
            data = recorder.load_actions()
            if data:
                display_recording_info(data)
                
        elif choice == '3':
            recordings = recorder.list_recordings()
            if recordings:
                print(f"\n📁 Found {len(recordings)} recordings:")
                print("-" * 80)
                for i, rec in enumerate(recordings, 1):
                    filename = rec['file'].name
                    start_time = rec['start_time'][:19] if len(rec['start_time']) > 19 else rec['start_time']
                    print(f"{i:2d}. {filename:<30} | {start_time} | {rec['duration']:6.1f}s | {rec['actions']:4d} actions")
                    
        elif choice == '4':
            recordings = recorder.list_recordings()
            if recordings:
                print(f"\nSelect a recording (1-{len(recordings)}):")
                for i, rec in enumerate(recordings, 1):
                    filename = rec['file'].name
                    start_time = rec['start_time'][:19]
                    print(f"{i}. {filename} ({start_time})")
                
                try:
                    selection = int(input("Enter number: ")) - 1
                    if 0 <= selection < len(recordings):
                        selected_file = recordings[selection]['file']
                        data = recorder.load_actions(selected_file)
                        if data:
                            display_recording_info(data)
                    else:
                        print("Invalid selection")
                except ValueError:
                    print("Invalid input")
                    
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-5.")

def display_recording_info(data):
    """Display recording information in a formatted way"""
    info = data['recording_info']
    print(f"\n📊 Recording Info:")
    print(f"   File: {info.get('output_file', 'Unknown')}")
    print(f"   Start time: {info['start_time']}")
    print(f"   Duration: {info['duration']} seconds")
    print(f"   Total actions: {info['total_actions']}")
    
    if data['actions']:
        print(f"\n📝 First 10 actions:")
        for i, action in enumerate(data['actions'][:10]):
            ts = action['timestamp']
            action_type = action['type']
            if action_type == 'key_press' or action_type == 'key_release':
                detail = f"key='{action['key']}'"
            elif action_type == 'mouse_click':
                detail = f"button={action['button']}, pos=({action['x']},{action['y']}), pressed={action['pressed']}"
            elif action_type == 'mouse_move':
                detail = f"pos=({action['x']},{action['y']})"
            else:
                detail = str(action)
            print(f"   {i+1:2d}. [{ts:6.3f}s] {action_type:12s} | {detail}")
    else:
        print("   No actions found in recording")

if __name__ == "__main__":
    main()
