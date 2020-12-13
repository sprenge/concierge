# Services overview

Concierge is composed of the following micro services :

## Motion

Triggers the shape/deep analysis of motion assets (still images and recording video clips).

Service REST API interface

| REST API path                    | Port | Description                                                  |
| -------------------------------- | ---- | ------------------------------------------------------------ |
| /motion/api/v1.0/motion_detected | 5104 | To be called when motion is triggered on one of the managed cameras.  It is possible that an (initial) still image is passed. |
| /motion/api/v1.0/recording_ready | 5104 | To be called when a camera has a recording ready and the recording is available on the concierge storage (under ROOT_DIR) |

The motion service will not block the REST API caller and off load the analytics task to dedicated threads.  It can also decide to reduce processing time (skipping more and more video frames) when the analytics queue grows to a higher number (within the boundaries of the analytics profile)

## Gui

Graphical interface and REST API interface (http://<CONCIERGE_IP_ADDRESS>/rest) for the concierge application.  Maintains the configuration into persistent storage.  The database tables can be visualized using the django admin interface (http://<CONCIERGE_IP_ADDRESS>/admin).

### Database model

#### Camera tables (brand/type/camera)

Stores the configuration for each managed camera and trigger configuration client (REST API callbacks).

#### Camera listeners table

Storage of REST API callbacks, organised per type (configuration, recording, ftp, ...)

#### Analytics profile table

An analytics profile needs to be attached to each camera in case concierge need to perform analytics services on recording assets.  It will define which shape discovery must be done and which deep analytics needs to be performed (e.g face detected, object comparison).  Please be aware that shape detection drives the deep analysis (e.g. person shape detection must be enabled if face recognition is activated).

## Camera specific services

Camera specific code (per camera brand) is isolated from the rest of the code.  Each camera brand registers REST API callbacks for configuring camera's and actions with respect to recording and other services.

Each camera brand gets assigned a specific port for the REST API callbacks :

| Brand   | Port |
| ------- | ---- |
| Reolink | 5102 |



## ftp server

Some of the camera brands offer the possibility to configure a ftp client that transfers snapshots and recording video clips to a ftp server (e.g. Reolink brand).  The triggers of these transfer can be used to trigger other services (e.g. motion detection, analytics).  The ftp server is configured in passive mode.

## Detect shape

Two container containers are launched to handle shape detect, one for finding shape into a still image and another one to find shape into recording clips.  All discovered shapes are returned to the REST API caller.

Service REST API interface

| REST API path                      | Port | Description                                                  |
| ---------------------------------- | ---- | ------------------------------------------------------------ |
| /shape/api/v1.0/find_shape         | 5103 | Find and return shapes into still images.                    |
| /shape/api/v1.0/get_video_metadata | 5105 | Return frame rate and number of frames for a given video clip |
| /shape/api/v1.0/find_shape         | 5105 | Find and return shapes into recording video clips.  In order to reduce processing time the caller of this service can decide only analyse every X frames (X is configurable) |

## Influx DB

The influx docker container stores video analytics data for visualisation and further processing (e.g. shape information is used as input for detailed analytics like face recognition and object comparison).  The influx database service is served via port 8086.

## Scheduler

The scheduler is responsible for trigger periodic tasks such as

- Clean up recordings when the concierge disk (ROOT_DIR) is filled more than a predefined level. (run every hour)