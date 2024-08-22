from datetime import datetime
from ultralytics import YOLO
import cv2
import math
import threading
import time
import pygame
from triggerEmail import sendEmail
import pandas as pd
import os
import random

classNames = ['Excavator', 'Gloves', 'Hardhat', 'Ladder', 'Mask', 'NO-hardhat',
              'NO-Mask', 'NO-Safety Vest', 'Person', 'SUV', 'Safety Cone', 'Safety Vest',
              'bus', 'dump truck', 'fire hydrant', 'machinery', 'mini-van', 'sedan', 'semi',
              'trailer', 'truck and trailer', 'truck', 'van', 'vehicle', 'wheel loader']

collected_data = []
data_dict = {}


# Function to append data to an existing CSV file or create a new one with headers
def append_data_to_csv(file_path, data: dict):
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    # Check if the file exists
    if os.path.exists(file_path):
        # Append data to the existing CSV file without headers
        df.to_csv(file_path, mode='a', index=False, header=False)
    else:
        # If the file doesn't exist, create a new CSV file and write data with headers
        df.to_csv(file_path, mode='w', index=False, header=True)


def trigger_email():
    print("Email Triggered")
    sendEmail(data_dict['Start_Date_Time'], data_dict['Zone_Triggered'], data_dict['Violations'])


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
        print("Alarm started.")

    def stop(self):
        """Stop playing the sound."""
        if self.sound_thread is None:
            print("Sound is not playing.")
            return

        # Signal the thread to stop
        self.stop_event.set()
        # Wait for the sound thread to finish
        self.sound_thread.join()
        print("Alarm stopped.")

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


def handle_alarm_and_email(violation: bool, player: SoundPlayer, missing_classes):
    global data_dict

    if violation and not player.is_playing():
        # Start the siren
        player.start()

        # Collect the data

        data_dict = {
            'Start_Date_Time': datetime.now(),
            'Zone_Triggered': random.choice([1, 2, 3, 4]),
            'Violations': missing_classes
        }

        # Trigger the email
        trigger_email()

    if not violation and player.is_playing():
        data_dict.update({'End_Date_Time': datetime.now()})
        print("Zone cleared")
        player.stop()
        append_data_to_csv('./data_insights.csv', data_dict)


def video_detection(path_x):
    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO("YOLO-Weights/bestest.pt")

    # Path to your sound file
    sound_file = "static/alarm/alarm_sound.wav"
    # Create an instance of SoundPlayer
    player = SoundPlayer(sound_file)

    # Initialize variables
    start_time = datetime.now()
    detection_results = []

    while True:
        success, img = cap.read()
        results = model(img, stream=True)

        for r in results:
            print("New Iteration")
            boxes = r.boxes
            missing_classes = []
            is_person_present = False
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                if class_name in ['NO-Safety Vest', 'NO-hardhat']:
                    missing_classes.append(class_name)
                elif class_name == 'Person':
                    is_person_present = True

                label = f'{class_name}{conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                c2 = x1 + t_size[0], y1 - t_size[1] - 3

                if class_name == 'Hardhat':
                    color = (0, 204, 255)
                elif class_name == "Gloves":
                    color = (222, 82, 175)
                elif class_name == "NO-hardhat":
                    color = (0, 100, 150)
                elif class_name == "Mask":
                    color = (0, 180, 255)
                elif class_name == "NO-Safety Vest":
                    color = (0, 230, 200)
                elif class_name == "Safety Vest":
                    color = (0, 266, 280)
                else:
                    color = (85, 45, 255)

                if conf > 0.6:
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)
                    cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

                    # Check if the class is NO-Mask, NO-Safety Vest, or NO-hardhat and confidence is above threshold
                    if class_name in ['NO-Safety Vest', 'NO-hardhat']:
                        detection_results.append({
                            'class': class_name,
                            'confidence': conf,
                            'bounding_box': (x1, y1, x2, y2),
                            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })

            # Handling alarm and email in case of missing classes
            if is_person_present and len(missing_classes) != 0:
                print(missing_classes)
                handle_alarm_and_email(True, player, missing_classes)

            else:
                handle_alarm_and_email(False, player, missing_classes)

        yield img

        if (datetime.now() - start_time).seconds >= 30:
            # Open the text file for appending detections
            with open('detection_results.txt', 'a') as file:
                # Write the detection results
                for detection in detection_results:
                    file.write(
                        f"[ {detection['time']} ] {detection['class']} {detection['confidence']} {detection['bounding_box']} \n")
                file.write('\n')  # Add a newline to separate each 30-second interval

            # Reset the start time and clear the detection results list
            start_time = datetime.now()
            detection_results = []

        yield img
        # out.write(img)
        # cv2.imshow("image", img)
        # if cv2.waitKey(1) & 0xFF==ord('1'):
        # break
    # out.release()


cv2.destroyAllWindows()
