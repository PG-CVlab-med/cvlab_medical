from cvlab.view.image_preview import WindowManager
from cvlab_medical.med_visualisation_utils.med_visualisation_classes import PreviewWindowVtk


def extend_windows_manager():
    def window_vtk(self, winname, **kwargs):
        winname = str(winname)
        with self.lock:
            if winname not in self.windows:
                position = kwargs.pop('position', 'auto')
                if position == 'auto':
                    position = self.positions.get(winname, self.find_best_place())
                window = self.windows[winname] = PreviewWindowVtk(self, winname, position=position, **kwargs)
                window.key_signal.connect(self.key_slot)
                window.move_signal.connect(self.save_positions)
            return self.windows[winname]

    setattr(WindowManager, "window_vtk", window_vtk)

    print("Windows manager was extended")
