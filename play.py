import json
import time
import threading
import argparse
from datetime import datetime
try:
    import pynput
    from pynput import mouse, keyboard
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
except ImportError:
    print("Please install pynput: pip install pynput")
    exit(1)

class ActionReplayer:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.is_replaying = False
        self.replay_thread = None
        self.start_time = None
        
    def load_recording(self, json_file_path):
        """Load the recording from JSON file"""
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    
    def map_key(self, key_name):
        """Map key names from recording to pynput keys"""
        key_mapping = {
            # Special keys
            'media_play_pause': Key.media_play_pause,
            'alt': Key.alt,
            'ctrl': Key.ctrl,
            'shift': Key.shift,
            'enter': Key.enter,
            'space': Key.space,
            'tab': Key.tab,
            'backspace': Key.backspace,
            'delete': Key.delete,
            'escape': Key.esc,
            'up': Key.up,
            'down': Key.down,
            'left': Key.left,
            'right': Key.right,
            'home': Key.home,
            'end': Key.end,
            'page_up': Key.page_up,
            'page_down': Key.page_down,
            'f1': Key.f1, 'f2': Key.f2, 'f3': Key.f3, 'f4': Key.f4,
            'f5': Key.f5, 'f6': Key.f6, 'f7': Key.f7, 'f8': Key.f8,
            'f9': Key.f9, 'f10': Key.f10, 'f11': Key.f11, 'f12': Key.f12,
        }
        
        # Return mapped key or the original key for regular characters
        return key_mapping.get(key_name, key_name)
    
    def map_mouse_button(self, button_name):
        """Map mouse button names to pynput buttons"""
        button_mapping = {
            'left': Button.left,
            'right': Button.right,
            'middle': Button.middle,
        }
        return button_mapping.get(button_name, Button.left)
    
    def replay_action(self, action):
        """Execute a single action"""
        action_type = action.get('type')
        
        try:
            if action_type == 'mouse_move':
                x, y = action['x'], action['y']
                self.mouse_controller.position = (x, y)
                
            elif action_type == 'mouse_click':
                x, y = action['x'], action['y']
                button = self.map_mouse_button(action['button'])
                pressed = action['pressed']
                
                self.mouse_controller.position = (x, y)
                if pressed:
                    self.mouse_controller.press(button)
                else:
                    self.mouse_controller.release(button)
                    
            elif action_type == 'key_press':
                key = self.map_key(action['key'])
                self.keyboard_controller.press(key)
                
            elif action_type == 'key_release':
                key = self.map_key(action['key'])
                self.keyboard_controller.release(key)
                
        except Exception as e:
            print(f"Error executing action {action_type}: {e}")
    
    def replay_recording(self, recording_data, speed_multiplier=1.0, repeat_times=1):
        """Replay the entire recording with specified speed and repetitions"""
        if not recording_data or 'actions' not in recording_data:
            print("Invalid recording data")
            return
            
        actions = recording_data['actions']
        if not actions:
            print("No actions to replay")
            return
        
        print(f"Starting replay of {len(actions)} actions...")
        print(f"Speed: {speed_multiplier}x, Repetitions: {repeat_times}")
        print("Press Ctrl+C to stop replay")
        
        self.is_replaying = True
        
        try:
            for repetition in range(repeat_times):
                if not self.is_replaying:
                    break
                
                if repeat_times > 1:
                    print(f"\n--- Repetition {repetition + 1}/{repeat_times} ---")
                
                self.start_time = time.time()
                first_timestamp = actions[0]['timestamp']
                
                for i, action in enumerate(actions):
                    if not self.is_replaying:
                        break
                        
                    # Calculate delay from previous action
                    current_timestamp = action['timestamp']
                    target_time = (current_timestamp - first_timestamp) / speed_multiplier
                    
                    # Wait until it's time for this action
                    elapsed_time = time.time() - self.start_time
                    sleep_time = target_time - elapsed_time
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    
                    # Execute the action
                    self.replay_action(action)
                    
                    # Print progress
                    if i % 50 == 0:  # Print every 50 actions
                        progress = (i / len(actions)) * 100
                        rep_info = f" (Rep {repetition + 1}/{repeat_times})" if repeat_times > 1 else ""
                        print(f"Progress: {progress:.1f}% ({i}/{len(actions)}){rep_info}")
                
                # Small pause between repetitions if there are multiple
                if repetition < repeat_times - 1 and self.is_replaying:
                    print("Pausing 1 second before next repetition...")
                    time.sleep(1.0)
                    
        except KeyboardInterrupt:
            print("\nReplay interrupted by user")
        except Exception as e:
            print(f"Error during replay: {e}")
        finally:
            self.is_replaying = False
            print("Replay finished")
    
    def start_replay_thread(self, recording_data, speed_multiplier=1.0, repeat_times=1):
        """Start replay in a separate thread"""
        if self.is_replaying:
            print("Replay already in progress")
            return
            
        self.replay_thread = threading.Thread(
            target=self.replay_recording, 
            args=(recording_data, speed_multiplier, repeat_times)
        )
        self.replay_thread.daemon = True
        self.replay_thread.start()
    
    def stop_replay(self):
        """Stop the current replay"""
        self.is_replaying = False
        if self.replay_thread:
            self.replay_thread.join(timeout=1.0)
    
    def analyze_recording(self, recording_data):
        """Analyze and print information about the recording"""
        if not recording_data:
            return
            
        info = recording_data.get('recording_info', {})
        actions = recording_data.get('actions', [])
        
        print("=== Recording Analysis ===")
        print(f"Start time: {info.get('start_time', 'Unknown')}")
        print(f"End time: {info.get('end_time', 'Unknown')}")
        print(f"Duration: {info.get('duration', 'Unknown')} seconds")
        print(f"Total actions: {len(actions)}")
        
        # Count action types
        action_counts = {}
        for action in actions:
            action_type = action.get('type')
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        print("\nAction breakdown:")
        for action_type, count in sorted(action_counts.items()):
            print(f"  {action_type}: {count}")
        
        print("=" * 30)

def get_float_input(prompt, default=1.0, min_val=0.1, max_val=10.0):
    """Get float input with validation"""
    while True:
        try:
            value = input(f"{prompt} (default {default}): ").strip()
            if not value:
                return default
            
            float_val = float(value)
            if min_val <= float_val <= max_val:
                return float_val
            else:
                print(f"Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid number")

def get_int_input(prompt, default=1, min_val=1, max_val=100):
    """Get integer input with validation"""
    while True:
        try:
            value = input(f"{prompt} (default {default}): ").strip()
            if not value:
                return default
            
            int_val = int(value)
            if min_val <= int_val <= max_val:
                return int_val
            else:
                print(f"Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Please enter a valid integer")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", help="file path to the json file")
    args = parser.parse_args()

    replayer = ActionReplayer()
    
    # Load the recording
    print("Loading recording...")
    json_file = args.filepath
    recording_data = replayer.load_recording(json_file)
    
    if not recording_data:
        print("Failed to load recording")
        return
    
    # Analyze the recording
    replayer.analyze_recording(recording_data)
    
    while True:
        print("\n=== Action Replayer ===")
        print("1. Quick replay (normal speed, 1x)")
        print("2. Custom speed and repetition")
        print("3. Analyze recording")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\nStarting quick replay in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            replayer.replay_recording(recording_data, 1.0, 1)
            
        elif choice == '2':
            print("\n=== Custom Replay Settings ===")
            print("Speed examples: 0.5 (half speed), 1.0 (normal), 2.0 (double speed)")
            speed = get_float_input("Enter replay speed (0.1 - 10.0)")
            
            print("\nRepeat examples: 1 (once), 5 (five times), 10 (ten times)")
            repeat = get_int_input("Enter number of repetitions (1 - 100)")
            
            estimated_time = (recording_data.get('recording_info', {}).get('duration', 100) / speed) * repeat
            print(f"\nEstimated total time: {estimated_time:.1f} seconds")
            print(f"Settings: {speed}x speed, {repeat} repetition(s)")
            
            confirm = input("Proceed? (y/N): ").strip().lower()
            if confirm == 'y':
                print(f"\nStarting custom replay in 3 seconds...")
                for i in range(3, 0, -1):
                    print(f"{i}...")
                    time.sleep(1)
                replayer.replay_recording(recording_data, speed, repeat)
            else:
                print("Replay cancelled")
            
        elif choice == '3':
            replayer.analyze_recording(recording_data)
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
