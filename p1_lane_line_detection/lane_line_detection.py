import cv2
import numpy as np


def find_lane_lines(img):
    """
    Detecting road markings
    This function will take a color image, in BGR color system,
    Returns a filtered image of road markings
    """

    # Convert to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply a Gaussian filter to remove noise
    # You can experiment with other filters here.
    img_gauss = cv2.GaussianBlur(gray, (11, 11), 0)

    # Apply Canny edge detection
    thresh_low = 100
    thresh_high = 150
    img_canny = cv2.Canny(img_gauss, thresh_low, thresh_high)

    # Return image
    return img_canny


def birdview_transform(img):
    """Apply bird-view transform to the image
    """
    IMAGE_H = 480
    IMAGE_W = 640
    src = np.float32([[0, IMAGE_H], [IMAGE_W, IMAGE_H], [0, IMAGE_H // 3], [IMAGE_W, IMAGE_H // 3]])
    dst = np.float32([[120, IMAGE_H], [IMAGE_W - 120, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    M = cv2.getPerspectiveTransform(src, dst) # The transformation matrix
    warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H)) # Image warping
    return warped_img


def find_left_right_points(image, draw=None, secondary_line_y=0.4):
    """Find left and right points of lane
    """

    im_height, im_width = image.shape[:2]

    # Primary line at 99.9% from the top of the image
    interested_line_y = int(im_height * 0.85)
    if draw is not None:
        cv2.line(draw, (0, interested_line_y),
                 (im_width, interested_line_y), (0, 0, 255), 2)

    # Secondary line at a given percentage from the top of the image
    secondary_line_y = int(im_height * secondary_line_y)
    if draw is not None:
        cv2.line(draw, (0, secondary_line_y),
                 (im_width, secondary_line_y), (0, 255, 255), 2)

    # Detect left/right points for primary line
    primary_line = image[interested_line_y, :]
    secondary_line = image[secondary_line_y, :]

    left_point_primary, right_point_primary = detect_points(primary_line, im_width // 2)
    left_point_secondary, right_point_secondary = detect_points(secondary_line, im_width // 2)

    # Draw points on the image
    if draw is not None:
        if left_point_primary != -1:
            draw = cv2.circle(draw, (left_point_primary, interested_line_y), 7, (255, 255, 0), -1)
        if right_point_primary != -1:
            draw = cv2.circle(draw, (right_point_primary, interested_line_y), 7, (0, 255, 0), -1)
        if left_point_secondary != -1:
            draw = cv2.circle(draw, (left_point_secondary, secondary_line_y), 7, (255, 0, 255), -1)
        if right_point_secondary != -1:
            draw = cv2.circle(draw, (right_point_secondary, secondary_line_y), 7, (0, 255, 255), -1)

    return (left_point_primary, right_point_primary), (left_point_secondary, right_point_secondary)


def detect_points(line, center):
    """Detect left and right points in a given line of the image"""
    left_point = -1
    right_point = -1
    lane_width = 2000

    for x in range(center, 0, -1):
        if line[x] > 0:
            left_point = x
            break
    for x in range(center + 1, len(line)):
        if line[x] > 0:
            right_point = x
            break

    if left_point != -1 and right_point == -1:
        right_point = left_point + lane_width

    if right_point != -1 and left_point == -1:
        left_point = right_point - lane_width

    return left_point, right_point


def calculate_control_signal(img, draw=None):
    """Calculate speed and steering angle"""

    # Find left/right points
    img_lines = find_lane_lines(img)
    img_birdview = birdview_transform(img_lines)
    draw[:, :] = birdview_transform(draw)
    (left_point_primary, right_point_primary), (left_point_secondary, right_point_secondary) = find_left_right_points(
        img_birdview, draw=draw)

    # Calculate speed and steering angle
    throttle = 0.7
    steering_angle = 0
    im_center = img.shape[1] // 2

    if left_point_primary != -1 and right_point_primary != -1:
        center_point = (right_point_primary + left_point_primary) // 2
        center_diff = im_center - center_point
        steering_angle = - float(center_diff * 0.15)
        abs_steering_angle = abs(steering_angle)

        # Check if there's a turn based on secondary line
        if left_point_secondary == -1 or right_point_secondary == -1:
            throttle = 0.3
        elif abs_steering_angle > 0.15:
            throttle = 0.3

    return throttle, steering_angle
