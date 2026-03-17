from acv3 import ACV3

def main():
    print("Initializing ACV3 (Mitsubishi Heavy 88-bit ZJS)...")
    ac = ACV3()
    
    print("Sending AC command...")
    # Default settings: temp=26, off=False, swing=True, fan=True
    success = ac.set_cmd(temp=26, off=False, swing=True, fan=True)
    
    if success:
        print("Command sent successfully!")
    else:
        print("Failed to send command.")

if __name__ == '__main__':
    main()
