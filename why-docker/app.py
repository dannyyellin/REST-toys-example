
with open("/etc/os-release") as f:
    print("Operating system information:")
    print(f.read())