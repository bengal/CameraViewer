import config
import gi
gi.require_version('Gdk', '3.0')
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0') # Needed for xvimagesink.set_window_handle()
from gi.repository import Gst, GObject, Gdk, Gtk, GstVideo

class Viewer:
    def __init__(self, config):

        Gst.init(None)
        Gst.init_check(None)
        
        self.config = config
        self.window = Gtk.Window()
        self.window.connect('destroy', self.stop)
        self.window.set_default_size(640, 480)

        self.grid = Gtk.Grid()

        self.area = []
        for camera in config.cameras:
            self.area.append(GstWidget(camera))

        count = 0
        for a in self.area:
            a.set_hexpand(True);
            a.set_vexpand(True);
            print("attaching at {}, {}", count % self.config.columns, int(count / self.config.columns))
            self.grid.attach(a, count % self.config.columns, count / self.config.columns, 1, 1)
            count += 1
            
        self.window.add(self.grid)
        self.window.show_all()

        for a in self.area:
            a.start()
            a.connect("selected", self.area_selected)

        Gtk.main()

    def stop(self, foo):
        for a in self.area:
            a.stop()
        Gtk.main_quit()

    def area_selected(self, area):
        print("Viewer: {} area selected".format(area.get_index()))
        for a in self.area:
            a.stop()

        self.window.remove(self.grid)
        print(self.config.cameras)
        widget = GstWidget(self.config.cameras[area.get_index() - 1])
        self.window.add(widget)
        self.window.show_all()
        widget.start(full=True, audio=True)
        widget.connect("selected", self.full_selected)

    def full_selected(self, area):
        area.stop()
        self.window.remove(area)
        self.window.add(self.grid)
        for a in self.area:
            a.start()            

    
class GstWidget(Gtk.DrawingArea):
    def __init__(self, camera):
        super().__init__()
        # Only setup the widget after the window is shown
        self.connect('realize', self._on_realize)
        self.uri = camera.preview_url
        self.full_uri = camera.url
        self.name = camera.description
        self.index = camera.index
        self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.clicked)

    def get_index(self):
        return self.index

    def init_pipeline(self, full, audio):
        uri = self.full_uri if full else self.uri
        if audio:
            self.pipeline = Gst.parse_launch (f'rtspsrc location={uri}  name=d d. ! queue ! capsfilter caps="application/x-rtp,media=video" ! rtph264depay ! decodebin ! autovideosink d. ! queue ! capsfilter caps="application/x-rtp,media=audio" ! decodebin ! audioconvert ! autoaudiosink')
        else:
            self.pipeline = Gst.parse_launch (f'rtspsrc location={uri} ! rtph264depay ! decodebin ! autovideosink')
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

    def _on_realize(self, widget):
        Gtk.DrawingArea.__init__(self)
          
        self.set_size_request(640, 480);
        self.xid = self.get_property('window').get_xid()
        self.running = False

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)
            self.pipeline.set_state(Gst.State.NULL)

    def on_sync_message(self, bus, msg):
        if msg.get_structure().get_name() == 'prepare-window-handle':
            msg.src.set_property('force-aspect-ratio', True)
            msg.src.set_window_handle(self.xid)

    def start(self, full=False, audio=False):
        if self.running:
            return
        self.init_pipeline(full, audio)
        self.pipeline.set_state(Gst.State.PLAYING)
        self.running = True

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.running = False

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def clicked(self, widget, event):
        print("{} was clicked".format(self.name))
        self.emit("selected")

    @GObject.Signal
    def selected(self):
        print("{} selected".format(self.name))
