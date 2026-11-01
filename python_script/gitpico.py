import os
import time
import re
import serial
import serial.tools.list_ports
import pygetwindow as gw
from git import Repo
from git.exc import InvalidGitRepositoryError

BAUD_RATE = 115200
INTERVAL = 2          

def find_microcontroller_port():
    """Scans system ports for the Pico"""
    ports = list(serial.tools.list_ports.comports())
    targets = ["arduino", "usb", "serial", "ch340", "cp210", "ftdi", "pico", "mbed"]
    for port in ports:
        port_info = (f"{port.device} {port.description} {port.hwid}").lower()
        if any(target in port_info for target in targets):
            return port.device
    if ports:
        return ports.device
    return None

def get_path_from_clion_header():
    """
    Parses the absolute system file path directly out of the title of the window.
    """
    try:
        active_window = gw.getActiveWindow()
        if not active_window or not active_window.title:
            return None
            
        title = active_window.title
        
        # Split on the en-dash or standard hyphens
        parts = [p.strip() for p in re.split(r'[-—–]', title)]
        
        for part in parts:
            if os.path.exists(part):
                return part
                
            match = re.search(r'([A-Za-z]:\\[^\[\]]+)', part)
            if match:
                extracted_path = match.group(1).strip()
                if os.path.exists(extracted_path):
                    return extracted_path
                    
    except Exception:
        pass
    return None



def get_git_status(path):
    if not path:
        return "ERR: No Focus"
        
    try:
        repo = Repo(path, search_parent_directories=True)
        if repo.bare:
            return "ERR: Bare Repo"
        
        branch = repo.active_branch.name
        if len(branch) > 14:  
            branch = branch[:11] + "..."
            
        staged = len(repo.index.diff("HEAD"))
        unstaged = len(repo.index.diff(None))
        untracked = len(repo.untracked_files)
        
        return f"{branch},{staged},{unstaged},{untracked}"
        
    except InvalidGitRepositoryError:
        return "ERR: Not Git Repo"
    except Exception as e:
        return f"ERR: {str(e)[:15]}"

def main():
    print("Scanning for connected screen modules...")
    detected_port = find_microcontroller_port()
    
    if not detected_port:
        print("ERROR: No board detected. Re-verify your USB interface.")
        return
        
    print(f"Opening port channel: {detected_port}")
    try:
        ser = serial.Serial(detected_port, BAUD_RATE, timeout=0.5)
        time.sleep(2)
        print("Success. Extracting path metrics from custom title headings...")
    except Exception as e:
        print(f"Connection dropped: {e}")
        return

    last_status = ""
    try:
        while True:
            if not ser.is_open:
                print("Lost port pipe. Recovering link...")
                time.sleep(4)
                main()
                return

            repo_path = get_path_from_clion_header()
            current_status = get_git_status(repo_path)
            
            if current_status != last_status:
                try:
                    ser.write(f"{current_status}\n".encode('utf-8'))
                    last_status = current_status
                    print(f"Header Path: {repo_path} -> Data: {current_status}")
                except (serial.SerialException, OSError):
                    ser.close()
                    time.sleep(2)
                    main()
                    return
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nTerminating process logs.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
