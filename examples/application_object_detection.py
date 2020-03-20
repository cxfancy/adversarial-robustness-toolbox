import cv2
import numpy as np
import matplotlib.pyplot as plt

from art.estimators.object_detection.PyTorchFasterRCNN import PyTorchFasterRCNN
from art.attacks.evasion import FastGradientMethod

COCO_INSTANCE_CATEGORY_NAMES = [
    "__background__", "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "N/A", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse",
    "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "N/A", "backpack", "umbrella", "N/A", "N/A", "handbag",
    "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "N/A", "wine glass", "cup", "fork", "knife", "spoon",
    "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
    "chair", "couch", "potted plant", "bed", "N/A", "dining table", "N/A", "N/A", "toilet", "N/A", "tv", "laptop",
    "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "N/A",
    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush", ]


def extract_predictions(predictions_):
    # for key, item in predictions[0].items():
    #     print(key, item)

    # Get the predicted class
    predictions_class = [COCO_INSTANCE_CATEGORY_NAMES[i] for i in list(predictions_["labels"].numpy())]
    print('predicted classes:', predictions_class)

    # Get the predicted bounding boxes
    predictions_boxes = [[(i[0], i[1]), (i[2], i[3])] for i in list(predictions_["boxes"].detach().numpy())]

    # Get the predicted prediction score
    predictions_score = list(predictions_["scores"].detach().numpy())
    print('predicted score:', predictions_score)

    # Get a list of index with score greater than threshold
    threshold = 0.5
    predictions_t = [predictions_score.index(x) for x in predictions_score if x > threshold][-1]

    predictions_boxes = predictions_boxes[: predictions_t + 1]
    predictions_class = predictions_class[: predictions_t + 1]

    return predictions_class, predictions_boxes, predictions_class


def plot_image_with_boxes(img, boxes, pred_cls):
    text_size = 5
    text_th = 5
    rect_th = 6

    for i in range(len(boxes)):
        cv2.rectangle(
            img, boxes[i][0], boxes[i][1], color=(0, 255, 0), thickness=rect_th
        )  # Draw Rectangle with the coordinates
        cv2.putText(
            img, pred_cls[i], boxes[i][0], cv2.FONT_HERSHEY_SIMPLEX, text_size, (0, 255, 0), thickness=text_th
        )  # Write the prediction class

    plt.axis("off")
    plt.imshow(img.astype(np.uint8), interpolation="nearest")
    plt.show()


def main():
    # Create object detector
    frcnn = PyTorchFasterRCNN(clip_values=(0, 255))

    # Load image 1
    image_1 = cv2.imread("./10best-cars-group-cropped-1542126037.jpg")
    image_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2RGB)  # Convert to RGB
    print('image_1.shape:', image_1.shape)

    # Load image 2
    # image_2 = cv2.imread("./banner-diverse-group-of-people-2.jpg")
    # image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2RGB)  # Convert to RGB
    # print('image_2.shape:', image_2.shape)

    # Stack images
    image = np.stack([image_1], axis=0)
    print('image.shape:', image.shape)

    for i in range(image.shape[0]):
        plt.axis("off")
        plt.title('image {}'.format(i))
        plt.imshow(image[i], interpolation="nearest")
        plt.show()

    # Make prediction on benign samples
    predictions = frcnn.predict(x=image)

    # Process predictions
    predictions_class, predictions_boxes, predictions_class = extract_predictions(predictions[0])

    # Plot predictions
    plot_image_with_boxes(img=image[0].copy(), boxes=predictions_boxes, pred_cls=predictions_class)

    # # Calculate loss gradients
    # gradients = frcnn.loss_gradient(x=image, y=None)
    #
    # # Create adversarial image
    # image_adv = image + np.sign(gradients) * 8 * 1
    # image_adv = np.clip(image_adv, a_min=0, a_max=255).astype(np.uint8)

    attack = FastGradientMethod(classifier=frcnn, eps=8)
    image_adv = attack.generate(x=image, y=None)

    print('np.amax(np.abs(image - image_adv))')
    print(np.amax(np.abs(image - image_adv)))

    for i in range(image_adv.shape[0]):
        plt.axis("off")
        plt.title('image_adv {}'.format(i))
        plt.imshow(image_adv[i].astype(np.uint8), interpolation="nearest")
        plt.show()

    predictions_adv = frcnn.predict(x=image_adv)

    predictions_adv_class, predictions_adv_boxes, predictions_adv_class = extract_predictions(predictions_adv[0])

    plot_image_with_boxes(img=image_adv[0].copy(), boxes=predictions_adv_boxes, pred_cls=predictions_adv_class)


if __name__ == "__main__":
    main()