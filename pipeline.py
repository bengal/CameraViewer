import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

class Pipeline:
    def __init__(self, uri, preview, proto):
        if proto == "rtsp" or proto == None:
            if preview:
                self.pipeline = Gst.parse_launch (f"rtspsrc location={uri} "
                                                  "! rtph264depay "
                                                  "! decodebin "
                                                  "! videoconvert "
                                                  "! autovideosink")
            else:
                self.pipeline = Gst.parse_launch (f"rtspsrc location={uri}  name=d d. "
                                                  "! queue "
                                                  "! capsfilter caps=\"application/x-rtp,media=video\" "
                                                  "! rtph264depay "
                                                  "! decodebin "
                                                  "! videoconvert "
                                                  "! autovideosink d. "
                                                  "! queue "
                                                  "! capsfilter caps=\"application/x-rtp,media=audio\" "
                                                  "! decodebin "
                                                  "! audioconvert "
                                                  "! autoaudiosink")
        elif proto == "mjpeg":
            self.pipeline = Gst.parse_launch (f"souphttpsrc location={uri} do-timestamp=true is_live=true "
                                              "! multipartdemux "
                                              "! jpegdec "
                                              "! autovideosink")
        else:
            raise Exception(f"invalid proto {proto}")

    def get_gst_pipeline(self):
        return self.pipeline
