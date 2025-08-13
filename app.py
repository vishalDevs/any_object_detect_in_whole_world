from flask import Flask, render_template, Response , send_from_directory
import cv2

app = Flask(__name__)

# Load detection model
model = cv2.dnn_DetectionModel(
    r'F:\computer_vision\MY_project\models\frozen_inference_graph.pb',
    r'F:\computer_vision\MY_project\models\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
)
model.setInputSize(320, 320)
model.setInputScale(1.0 / 127.5)
model.setInputMean((127.5, 127.5, 127.5))
model.setInputSwapRB(True)

# Load labels
with open(r"F:\computer_vision\MY_project\dataset\lables.txt") as f:
    classLabels = f.read().strip().split("\n")

cap = cv2.VideoCapture(0)  # Webcam

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        ClassIndex, confidence, bbox = model.detect(frame, confThreshold=0.5)
        if len(ClassIndex) > 0:
            for classId, conf, box in zip(ClassIndex.flatten(), confidence.flatten(), bbox):
                if 0 < classId <= len(classLabels):
                    cv2.rectangle(frame, box, (0, 150, 0), 2)
                    cv2.putText(frame, f'{classLabels[classId-1]} {conf*100:.1f}%',
                                (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html') 

@app.route('/about')
def about():
    return render_template('about.html') 

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/index')
def home():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
