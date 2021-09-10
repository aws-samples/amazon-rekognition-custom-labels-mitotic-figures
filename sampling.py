from functools import partial
import os
from typing import Any, Callable, Dict, List, Optional

import openslide
from pathlib import Path
from SlideRunner.dataAccess.annotations import *
from SlideRunner.dataAccess.database import Database
from tqdm.notebook import tqdm


class BoundingBox:
    
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self._left = left
        self._top = top
        self._right = right
        self._bottom = bottom
    
    @property
    def left(self) -> int:
        return self._left
    
    @property
    def top(self) -> int:
        return self._top

    @property
    def right(self) -> int:
        return self._right
    
    @property
    def bottom(self) -> int:
        return self._bottom
    
    def check_bbox(x_start: int, y_start: int, bbox, size: int = 512) -> bool:
        return (self._left > x_start and
                self._right < x_start + size and
                self._top > y_start and
                self._bottom < y_start + size)

    
class SlideContainer():

    def __init__(self,
                 file: Path,
                 annotations: Dict[str, Any],
                 y: Any,
                 level: int = 0,
                 width: int = 256,
                 height: int = 256,
                 sample_func: Optional[Callable] = None):
        
        self.file = file
        self.slide = openslide.open_slide(str(file))
        self.width = width
        self.height = height
        self.down_factor = self.slide.level_downsamples[level]
        self.y = y
        self.annotations = annotations
        self.sample_func = sample_func
        self.classes = list(set(self.y[1]))
        
        self.level = self.slide.level_count - 1 if level is None else level

    @property
    def shape(self):
        return (self.width, self.height)

    def get_patch(self,  x: int=0, y: int=0):
         return np.array(self.slide.read_region(location=(int(x * self.down_factor),int(y * self.down_factor)),
                                                level=self.level, size=(self.width, self.height)))[:, :, :3]


def sampling_func(y, **kwargs):

    h, w = kwargs['size']

    level_dimensions = kwargs['level_dimensions']
    level = kwargs['level']
    
    _random_offset_scale = 0.5
    xoffset = randint(-w, w) * _random_offset_scale
    yoffset = randint(-h, h) * _random_offset_scale

    slide_width, slide_height = level_dimensions[level]
        
    xmin, ymin = randint(int(w / 2 - xoffset), slide_width - w), randint(int(h / 2 - yoffset), slide_height - h)
    
    return int(xmin - w / 2 + xoffset), int(ymin - h / 2 + yoffset)
    

def get_slides(database: Database,
               test_slide_ids: List[int],
               base_path: str = 'WSI',
               size: int = 256,
               positive_class: int = 2,
               negative_class: int = 7):
    
    lbl_bbox = []
    training_slides = []
    test_slides = []
    files = []
    
    slides = tqdm(
        database.execute("SELECT uid, filename FROM Slides").fetchall(),
        desc='Loading slides...',
    )

    for idx, (cur_slide, filename) in enumerate(slides):

        database.loadIntoMemory(cur_slide)
        slide_path = os.path.join(base_path, filename)
        slide = openslide.open_slide(slide_path)

        level = 0
        level_dimension = slide.level_dimensions[level]
        down_factor = slide.level_downsamples[level]

        # Dictionary of classes found so far, initialized with the positive class, which
        # we are sure it exists.
        classes = {
            positive_class: 1
        }

        annotations = {}
        labels, bboxes = [], []
        for id, annotation in database.annotations.items():

            # Ignore deleted annotations, or any that are not of type SPOT.
            if annotation.deleted or annotation.annotationType != AnnotationType.SPOT:
                continue

            annotation.r = 25
            d = 2 * annotation.r / down_factor
            x_min = (annotation.x1 - annotation.r) / down_factor
            y_min = (annotation.y1 - annotation.r) / down_factor
            x_max = x_min + d
            y_max = y_min + d

            # If the annotation class is not yet in the classes dictionary, create
            # an entry and initialize the structures within.
            if annotation.agreedClass not in annotations:
                annotations[annotation.agreedClass] = {}
                annotations[annotation.agreedClass]['bboxes'] = []
                annotations[annotation.agreedClass]['label'] = []

            # Store bounding box and label into the annotation dictionary.
            annotations[annotation.agreedClass]['bboxes'].append([int(x_min), int(y_min), int(x_max), int(y_max)])
            annotations[annotation.agreedClass]['label'].append(annotation.agreedClass)

            # Store the bounding box and its label separately in the bboxes and labels
            # lists.
            if annotation.agreedClass in classes:
                label = classes[annotation.agreedClass]

                #                     bboxes.append([int(x_min), int(y_min), int(x_max), int(y_max)])
                bboxes.append(BoundingBox(int(x_min), int(y_min), int(x_max), int(y_max)))
                labels.append(label)

        if len(bboxes) > 0:
            lbl_bbox.append([bboxes, labels])
            
            is_test = str(cur_slide) in test_slide_ids
            if is_test:
                files.append(SlideContainer(
                    file=slide_path,
                    annotations=annotations,
                    level=level,
                    width=size,
                    height=size,
                    y=[bboxes, labels],
                    sample_func=partial(sampling_func, negative_class=negative_class)))
                test_slides.append(len(files) - 1)
            else:
                files.append(SlideContainer(
                    file=slide_path,
                    annotations=annotations,
                    level=level,
                    width=size,
                    height=size,
                    y=[bboxes, labels],
                    sample_func=partial(sampling_func, negative_class=negative_class)))
                training_slides.append(len(files) - 1)

    return lbl_bbox, training_slides, test_slides, files
