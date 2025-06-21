#!/usr/bin/env python3
"""Script to detect display scaling factor."""

import subprocess
import re

def detect_scaling():
    """Detect the actual display scaling factor."""
    try:
        # Get xrandr output
        output = subprocess.check_output(['xrandr', '--query'], text=True)
        lines = output.split('\n')
        
        # Find primary display
        for line in lines:
            if 'connected' in line and 'primary' in line:
                print(f"Found primary display: {line}")
                
                # Extract physical resolution (e.g., 4096x2304)
                match = re.search(r'(\d+)x(\d+)', line)
                if match:
                    physical_width = int(match.group(1))
                    physical_height = int(match.group(2))
                    print(f"Physical resolution: {physical_width}x{physical_height}")
                    
                    # Find current logical resolution (marked with *)
                    for next_line in lines:
                        if '*' in next_line:
                            print(f"Current resolution line: {next_line}")
                            # Current resolution
                            res_match = re.search(r'(\d+)x(\d+)', next_line)
                            if res_match:
                                logical_width = int(res_match.group(1))
                                logical_height = int(res_match.group(2))
                                print(f"Logical resolution: {logical_width}x{logical_height}")
                                
                                # Calculate scaling factor
                                scale_x = physical_width / logical_width
                                scale_y = physical_height / logical_height
                                
                                print(f"Calculated scaling: {scale_x:.2f}x{scale_y:.2f}")
                                
                                # Return the average scaling factor
                                avg_scale = (scale_x + scale_y) / 2
                                print(f"Average scaling: {avg_scale:.2f}")
                                return avg_scale
                break
    except Exception as e:
        print(f"Error detecting scaling: {e}")
    
    return 1.0

if __name__ == "__main__":
    scaling = detect_scaling()
    print(f"Recommended scaling factor: {scaling:.2f}") 