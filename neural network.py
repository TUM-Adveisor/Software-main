import numpy as np
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Activation, Dropout, Flatten, Dense, GlobalAveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.optimizers import Adam
from keras.applications.inception_resnet_v2 import InceptionResNetV2
import glob

n_data = len(glob.glob("raw_data\*"))*64

n_epoch = 50
n_batch = 32

datagen = ImageDataGenerator(
    rotation_range=20,
    brightness_range=[0.8, 1.2],
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest',
    horizontal_flip=True,
    rescale=1. /255,
    data_format=None,
    validation_split=0.2
)
train_gen = datagen.flow_from_directory(
    './dataset',
    target_size = (400, 400),
    class_mode = 'categorical',
    color_mode = 'rgb',
    batch_size = n_batch,
    subset="training",
    shuffle=True
)
val_gen = datagen.flow_from_directory(
    './dataset',
    target_size = (400, 400),
    class_mode = 'categorical',
    color_mode = 'rgb',
    batch_size = n_batch,
    subset="validation",
    shuffle=True
)

model = Sequential()
base_model = InceptionResNetV2(weights='imagenet', include_top=False, input_shape=(400,400,3))
model.add(base_model)
model.add(GlobalAveragePooling2D())
model.add(Dense(units = 1024, activation="relu"))
#model.add(Dropout(0.2))
#model.add(Dense(units = 1024, activation="relu"))
model.add(Dense(units=13, activation="softmax"))

base_total = len(base_model.layers)
for layer in base_model.layers[:base_total]:
      layer.trainable=False
for layer in model.layers[base_total:]:
      layer.trainable=True
for layer in model.layers[1:]:
      layer.trainable = True

opt = Adam(learning_rate=0.0001)
model.compile(optimizer=opt, loss="categorical_crossentropy", metrics=['accuracy'])
model.summary()

checkpoint = ModelCheckpoint("chess_check.h5", monitor="val_acc", verbose=1, save_bes_only=True, save_weights_onlny=False, mode="auto", period=1)

early = EarlyStopping(monitor="val_acc", min_delta=0, patience=10, verbose=1, mode="auto", restore_best_weights=True)

hist = model.fit_generator(steps_per_epoch =  (0.8*n_data)//n_batch, generator = train_gen, validation_data = val_gen, validation_steps = (0.2*n_data)//n_batch, epochs=n_epoch, verbose=1, callbacks=[checkpoint, early])
model.save_weights('chess.h5')