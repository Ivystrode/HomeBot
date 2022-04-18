# HomeBot

### Home Hub

The home_hub directory files run on the PINAS

***Need to make bot able to send command to main_hub (to start/stop wifi scans)***

### Remote Hub

The remote_hub files run on the remote machine (Linode instance)

### Home Unit

The home_unit directory files run on the camera units (and any other unit types I may add)

### Adding

1. Camera detects object (person)
2. Camera sends picture to PINAS
3. PINAS sends picture to remote hub
4. Remote hub runs face detection on picture and informs user if face is recognised and/or detected