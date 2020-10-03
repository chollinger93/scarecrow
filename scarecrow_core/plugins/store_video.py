from PIL import Image
import cv2
import numpy as np
from scarecrow_core.plugin_base.base import *
import datetime

from scarecrow_core.utilities.utils import get_logger
logger = get_logger()

class StoreVideoPlugin(ImageDetectorBasePlugin):
    name = 'store_video'
    mode = 'server'

    def __init__(self, configuration):
        self.buffer = []
        self.fps = float(configuration['Video']['FPS'])
        self.video_path = configuration['Video']['Path']
        self.codec = configuration['Video']['Codec']
        self.name = configuration['Video']['OutName']
        try:
            self.buffer_size = int(configuration['Video']['BufferSize'])
        except Exception:
            target_len = int(configuration['Video']['TargetLengthSeconds'])
            self.buffer_size = target_len*self.fps
            logger.warning('Using TargetLengthSeconds, setting to {}'.format(self.buffer_size))
        ImageDetectorBasePlugin.__init__(self, configuration, mode=self.mode)

    def run_after(self, res, ix, confidence, np_det_img):
        # TODO: SIGTERM handler
        # TODO: detection labels as *args
        logger.debug('StoreVideoPlugin run_after ix {} / buf {}'.format(ix, len(self.buffer)))
        if np_det_img is not None:
            img = np_det_img.astype(np.uint8)
            self.buffer.append(img)
        else:
            logger.warning('Store video frame is null?')

        if len(self.buffer) > self.buffer_size:
            dt = datetime.datetime.now().isoformat()
            vid_path = '{}/{}_{}'.format(self.video_path, dt, self.name)
            logger.info('Flushing video to {}'.format(vid_path))
            fourcc = cv2.VideoWriter_fourcc(*self.codec) #mp4v
            video = cv2.VideoWriter(
                vid_path, 
                fourcc, 
                self.fps, 
                (self.buffer[0].shape[1], self.buffer[0].shape[0]),
                True)
            for frame in self.buffer:
                video.write(frame)
            video.release()
            cv2.destroyAllWindows()
            # Clear buffer
            self.buffer = []
            # Save a separate key frame 
            img = Image.fromarray(np_det_img, 'RGB')
            thumb_path = '{}/{}_{}_thumb.jpg'.format(self.video_path, dt, ix)
            logger.info('Flushing thumbnail to {}'.format(thumb_path))
            img.save(thumb_path)
