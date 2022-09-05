import cv2
import time
import datetime
import smtplib

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")
my_email = "youremail@gmail.com"
password = "password"

detection = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5
frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

while True:
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.05, 4)
    bodies = face_cascade.detectMultiScale(gray, 1.05, 4)

    if len(faces) + len(bodies) > 0:
        if detection:
            timer_started = False
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%m-%y-%H-%M-%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20, frame_size)
            print("started recording")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
                connection.ehlo()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=my_email,
                                    msg=f"Subject: Movement tracker\n\n"
                                        f"your movement tracker started at: {current_time}")
    elif detection:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_started = False
                out.release()
                print("Stop recording!")
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
                    connection.ehlo()
                    connection.login(user=my_email, password=password)
                    connection.sendmail(from_addr=my_email, to_addrs=my_email,
                                        msg=f"Subject: Movement tracker\n\n"
                                            f"your movement tracker stopped at: {current_time}")
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection:
        out.write(frame)
    # for (x, y, width, height) in faces:
    #     cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)
    cv2.imshow("camera", frame)
    if cv2.waitKey(1) == ord("q"):
        break
out.release()
cap.release()
cv2.destroyAllWindows()
