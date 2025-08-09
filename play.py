import json
import time
import threading
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
    
    def replay_recording(self, recording_data, speed_multiplier=1.0):
        """Replay the entire recording"""
        if not recording_data or 'actions' not in recording_data:
            print("Invalid recording data")
            return
            
        actions = recording_data['actions']
        if not actions:
            print("No actions to replay")
            return
        
        print(f"Starting replay of {len(actions)} actions...")
        print("Press Ctrl+C to stop replay")
        
        self.is_replaying = True
        self.start_time = time.time()
        
        try:
            # Get the first timestamp as baseline
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
                    print(f"Progress: {progress:.1f}% ({i}/{len(actions)})")
                    
        except KeyboardInterrupt:
            print("\nReplay interrupted by user")
        except Exception as e:
            print(f"Error during replay: {e}")
        finally:
            self.is_replaying = False
            print("Replay finished")
    
    def start_replay_thread(self, recording_data, speed_multiplier=1.0):
        """Start replay in a separate thread"""
        if self.is_replaying:
            print("Replay already in progress")
            return
            
        self.replay_thread = threading.Thread(
            target=self.replay_recording, 
            args=(recording_data, speed_multiplier)
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

def main():
    replayer = ActionReplayer()
    
    # Load the recording
    print("Loading recording...")
    json_file = "recordings/recording_20250809_163052.json"  # Update this path as needed
    recording_data = replayer.load_recording(json_file)
    
    if not recording_data:
        print("Failed to load recording")
        return
    
    # Analyze the recording
    replayer.analyze_recording(recording_data)
    
    while True:
        print("\n=== Action Replayer ===")
        print("1. Replay at normal speed")
        print("2. Replay at 2x speed")
        print("3. Replay at 0.5x speed (slower)")
        print("4. Analyze recording")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            print("\nStarting replay in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            replayer.replay_recording(recording_data, 1.0)
            
        elif choice == '2':
            print("\nStarting 2x speed replay in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            replayer.replay_recording(recording_data, 2.0)
            
        elif choice == '3':
            print("\nStarting 0.5x speed replay in 3 seconds...")
            for i in range(3, 0, -1):
                print(f"{i}...")
                time.sleep(1)
            replayer.replay_recording(recording_data, 0.5)
            
        elif choice == '4':
            replayer.analyze_recording(recording_data)
            
        elif choice == '5':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
