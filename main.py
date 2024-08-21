import threading
import time
import pygame

class SoundPlayer:
    def __init__(self, file_path):
        # Initialize the mixer module in pygame
        pygame.mixer.init()
        self.file_path = file_path
        self.stop_event = threading.Event()
        self.sound_thread = None

    def start(self):
        """Start playing the sound in a separate thread."""
        if self.sound_thread is not None and self.sound_thread.is_alive():
            print("Sound is already playing.")
            return

        # Create and start a new thread to play the sound
        self.stop_event.clear()
        self.sound_thread = threading.Thread(target=self._play_sound)
        self.sound_thread.start()

    def stop(self):
        """Stop playing the sound."""
        if self.sound_thread is None:
            print("Sound is not playing.")
            return

        # Signal the thread to stop
        self.stop_event.set()
        # Wait for the sound thread to finish
        self.sound_thread.join()
        print("Music stopped.")

    def _play_sound(self):
        """Play the sound file."""
        # Load the sound file
        pygame.mixer.music.load(self.file_path)
        # Play the sound
        pygame.mixer.music.play()

        # Keep checking if the stop event is set or if the music has finished
        while not self.stop_event.is_set() and pygame.mixer.music.get_busy():
            time.sleep(1)

        # Stop the music if the stop event is set
        if self.stop_event.is_set():
            pygame.mixer.music.stop()

    def is_playing(self):
        """Check if the sound is currently playing."""
        return self.sound_thread is not None and self.sound_thread.is_alive()

# Example usage
if __name__ == "__main__":
    # Path to your sound file
    sound_file = "static/alarm/alarm_sound.wav"

    # Create an instance of SoundPlayer
    player = SoundPlayer(sound_file)

    # Start playing the sound
    player.start()

    # Continue with other tasks
    for i in range(3):
        print(player.is_playing())
        time.sleep(1)

    # Stop the music after some time
    print("Stopping the music...")
    player.stop()
    for i in range(5):
        print(f"Task {i+1} is running...")
        time.sleep(2)

    player.start()

    for i in range(5):
        print(f"Task {i+1} is running...")
        time.sleep(0.3)

    print("Stopping the music...")
    player.stop()



# wave_obj = simpleaudio.WaveObject.from_wave_file("static/alarm/alarm_sound.wav")
# play_obj = wave_obj.play()
# play_obj.wait_done()
# for i in range(100):
#     print(i)
