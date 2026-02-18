import cv2
import easyocr
import numpy as np
import re
from db import DatabaseManager  # Importing your database logic

class VehicleInspector:
    def __init__(self):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.db = DatabaseManager() # Initialize Database
        
        # Temporary storage for the current inspection
        self.current_data = {"mileage": "N/A", "engine": "N/A"}
        print("System Initialized: Ready for Inspection.")

    def preprocess_image(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)
        thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        return thresh

    def extract_data(self, frame, label_type="mileage"):
        processed = self.preprocess_image(frame)
        results = self.reader.readtext(processed)
        
        extracted_text = ""
        for (bbox, text, prob) in results:
            if prob > 0.4:
                extracted_text += f" {text.upper()}"

        if label_type == "mileage":
            numbers = re.findall(r'\d+', extracted_text)
            return "".join(numbers) if numbers else "Not Detected"
        
        return extracted_text.strip()

    def live_inspection(self):
        cap = cv2.VideoCapture(0)
        
        print("\n--- CONTROLS ---")
        print("M: Capture Mileage | E: Capture Engine No | S: Save to DB | Q: Quit")
        
        while True:
            ret, frame = cap.read()
            if not ret: break

            h, w, _ = frame.shape
            # Draw UI Overlay
            cv2.rectangle(frame, (w//4, h//3), (3*w//4, 2*h//3), (0, 255, 0), 2)
            cv2.putText(frame, f"MIL: {self.current_data['mileage']}", (10, 30), 1, 1.5, (255, 255, 255), 2)
            cv2.putText(frame, f"ENG: {self.current_data['engine']}", (10, 60), 1, 1.5, (255, 255, 255), 2)

            cv2.imshow("Vehicle Scanner", frame)
            key = cv2.waitKey(1) & 0xFF
            
            # --- ACTION LOGIC ---
            if key == ord('m'):
                roi = frame[h//3:2*h//3, w//4:3*w//4]
                self.current_data['mileage'] = self.extract_data(roi, "mileage")
                print(f"Captured Mileage: {self.current_data['mileage']}")
                
            elif key == ord('e'):
                roi = frame[h//3:2*h//3, w//4:3*w//4]
                self.current_data['engine'] = self.extract_data(roi, "engine")
                print(f"Captured Engine No: {self.current_data['engine']}")

            elif key == ord('s'):
                # Ask for Plate Number in console before saving
                plate = input("Enter Vehicle Plate Number: ").upper()
                self.db.save_entry(plate, self.current_data['mileage'], self.current_data['engine'])
                print("Inspection Logged! Resetting for next vehicle...")
                self.current_data = {"mileage": "N/A", "engine": "N/A"}
                
            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    inspector = VehicleInspector()
    inspector.live_inspection()