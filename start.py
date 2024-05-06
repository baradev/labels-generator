import boto3
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
from io import BytesIO

def detect_labels(photo, bucket):
    # Create a Rekognition client
    client = boto3.client('rekognition')

    # Detect labels in the photo
    response = client.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        MaxLabels=15)

    # Detect faces in the photo and get emotion information
    face_response = client.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
        Attributes=['ALL'])

    # Load the image from S3
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, photo)
    img_data = obj.get()['Body'].read()
    img = Image.open(BytesIO(img_data))

    # Display the image with bounding boxes for labels
    plt.imshow(img)
    ax = plt.gca()

    # Track detected emotions for each face
    face_emotions = {}

    # Process faces and emotions
    for face in face_response['FaceDetails']:
        emotions = face['Emotions']
        dominant_emotion = max(emotions, key=lambda x: x['Confidence'])
        # Convert bounding box dictionary to a tuple
        bbox_tuple = (face['BoundingBox']['Left'], face['BoundingBox']['Top'], 
                      face['BoundingBox']['Width'], face['BoundingBox']['Height'])
        face_emotions[bbox_tuple] = dominant_emotion

    # Draw bounding boxes and labels for faces
    for face_bbox, emotion in face_emotions.items():
        left = face_bbox[0] * img.width
        top = face_bbox[1] * img.height
        width = face_bbox[2] * img.width
        height = face_bbox[3] * img.height
        rect = patches.Rectangle((left, top), width, height, linewidth=1, edgecolor='g', facecolor='none')
        ax.add_patch(rect)
        emotion_text = emotion['Type'] + ' (' + str(round(emotion['Confidence'], 2)) + '%)'
        plt.text(left, top - 2, emotion_text, color='g', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

    # Draw bounding boxes and labels for other detected labels
    for label in response['Labels']:
        for instance in label.get('Instances', []):
            bbox = instance['BoundingBox']
            left = bbox['Left'] * img.width
            top = bbox['Top'] * img.height
            width = bbox['Width'] * img.width
            height = bbox['Height'] * img.height
            rect = patches.Rectangle((left, top), width, height, linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            label_text = label['Name'] + ' (' + str(round(label['Confidence'], 2)) + '%)'
            plt.text(left, top - 2, label_text, color='r', fontsize=8, bbox=dict(facecolor='white', alpha=0.7))

    plt.show()

    return len(response['Labels'])

def main():
    photo = ''
    bucket = 'my-rekognition-label-maker'
    label_count = detect_labels(photo, bucket)
    print("Labels detected:", label_count)

if __name__ == "__main__":
    main()
