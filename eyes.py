import cv2
import numpy as np

class Eyes:
    def __init__(self,cap_dev=0):
        self.cap = cv2.VideoCapture(cap_dev)  # input device id: 0-3
        self.img = []
        self.img_result = []
        self.points = []
        self.img_thresh = []
        self.img_warp = []
        self.img_warp_inv = []

        # Saved variable paths
        self.warp_fn = 'vars/warp_points.txt'
        self.thresh_fn = 'vars/thresh_points.txt'

        if self.cap.isOpened():
            self.get_points()

    def destroy(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def get_points(self):  #is get_points disposable?
        with open(self.warp_fn, 'r') as file:
            warp_points = np.loadtxt(file)
        with open(self.thresh_fn, 'r') as file:
            thresh_points = np.loadtxt(file, dtype=int)

        self.points = np.array([{'warp_points': warp_points,
                                 'thresh_points': thresh_points}])

    def cap_img(self, display=False, size=[480, 240]):
        ret, self.img = self.cap.read()
        self.img = cv2.resize(self.img, (size[0], size[1]))

        if not ret:
            self.error = 1
        else:
            # Undistort image
            dist_vars = np.load('vars/cam_dist_matrix.npz')
            self.img = cv2.undistort(self.img, dist_vars['mtx'], dist_vars['dist'], None, dist_vars['newcameramtx'])

        if display:
            print('Press \'q\' to quit.')
            while True:
                self.cap_img()
                cv2.imshow('IMG', self.img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    def get_img(self):
        self.cap_img()
        return self.img

    def thresholding(self):
        thresh_pts = self.points[0]['thresh_points']
        img_copy = self.img.copy()
        img_hsv = cv2.cvtColor(img_copy, cv2.COLOR_BGR2HSV)
        lower_thresh = np.array(thresh_pts[0])   # [81, 54, 140]
        upper_thresh = np.array(thresh_pts[1])    # [128, 255, 255]
        mask = cv2.inRange(img_hsv, lower_thresh, upper_thresh)
        self.img_thresh = mask

    def get_thresh_img(self):
        self.cap_img()
        self.thresholding()
        return self.img_thresh

    def warp_image(self, img_in=None, inv=False):
        pts1 = np.float32(self.points[0]['warp_points'])
        pts2 = np.float32([[0, 0], [self.w_t, 0], [0, self.h_t], [self.w_t, self.h_t]])

        if img_in is None:
            img_in = self.img_thresh

        if inv:
            # Warp original image with inverse perspective for self.draw_lanes()
            matrix = cv2.getPerspectiveTransform(pts2, pts1)
            self.img_warp_inv = cv2.warpPerspective(img_in, matrix, (self.w_t, self.h_t))
        else:
            # Warp image after threshold filter with standard perspective for lane processing
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            self.img_warp = cv2.warpPerspective(img_in, matrix, (self.w_t, self.h_t))

    def show_img(self, img, string="Thresh Img"):
        img = cv2.resize(img, (480, 240))
        cv2.imshow(string, img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.destroy()

def load_img(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (480, 240))
    return img

if __name__ == '__main__':
    eye = Eyes()
    while True:
        eye.show_img(eye.get_img(), 'regular')
