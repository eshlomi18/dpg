class DraggableWidget:
    def __init__(self, widget):
        self.widget_y = None
        self.widget_x = None
        self.start_y = None
        self.start_x = None
        self.widget = widget
        self.widget.bind("<Button-1>", self.on_button_press)
        self.widget.bind("<B1-Motion>", self.on_button_motion)
        self.widget.bind("<Double-Button-1>", self.on_double_click)
        self.dragging = False

    def on_button_press(self, event):
        if self.dragging:
            self.start_x = event.x_root
            self.start_y = event.y_root
            self.widget_x = self.widget.winfo_x()
            self.widget_y = self.widget.winfo_y()

    def on_button_motion(self, event):
        if self.dragging:
            x = event.x_root - self.start_x + self.widget_x
            y = event.y_root - self.start_y + self.widget_y
            self.widget.place(x=x, y=y)

    def on_double_click(self, event):
        # the x and y points of the clicked widget except from the "publish" button
        if self.widget.cget("text") != "publish":
            print(f"x={self.widget.winfo_x()}, y={self.widget.winfo_y()}")