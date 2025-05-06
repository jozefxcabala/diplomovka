import tkinter as tk
from tkinter import filedialog
import os
import cv2
from PIL import Image, ImageTk

ACTIONS = [
    "person is running",
    "person is walking",
    "person fell to the ground",
    "person is lying in the ground",
    "person is fighting",
    "person have something in hand",
    "person is dancing",
    "person is standing in place",
    "person is sitting",
    "person is jumping",
    "person is coughing",
    "person is limping",
    "person is clapping",
    "a person wearing a helmet and an orange vest is walking",
    "a person wearing a helmet and an orange vest is dancing",
    "a person wearing a helmet and an orange vest is standing in place",
    "a person wearing a helmet and an orange vest is jumping",
    "a person wearing a helmet and an orange vest is running",
    "a person wearing a helmet and an orange vest is fighting",
    "a person wearing a helmet and an orange vest have something in hand",
    "a person wearing a helmet and an orange vest is lying in the ground",
    "a person wearing a helmet and an orange vest is limping",
    "a person wearing a helmet and an orange vest fell to the ground",
    "person wearing a helmet and an orange vest is sitting",
    "a person wearing a helmet and an orange vest is riding motocycle",
    "person is lying in the ground and shaking"
]

class VideoAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Annotator")
        self.video_list = []
        self.current_video_path = None
        self.cap = None
        self.frame = None
        self.status_label = None

        self.setup_ui()

    def setup_ui(self):
        folder_btn = tk.Button(self.root, text="Select Folder", command=self.load_folder)
        folder_btn.pack()

        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.video_listbox = tk.Listbox(main_frame, width=40)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.video_listbox.bind("<<ListboxSelect>>", self.load_video)

        self.canvas = tk.Canvas(main_frame, width=640, height=480)
        self.canvas.pack(side=tk.LEFT)

        self.right_frame = tk.Frame(main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.check_vars = []
        for action in ACTIONS:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.right_frame, text=action, variable=var)
            chk.pack(anchor=tk.W)
            self.check_vars.append((action, var))

        save_btn = tk.Button(self.right_frame, text="Save Annotation", command=self.save_annotation)
        save_btn.pack(pady=10)

        self.status_label = tk.Label(self.right_frame, text="", fg="green")
        self.status_label.pack()

        # Annotations preview label
        self.preview_label = tk.Label(self.right_frame, text="Annotations Preview:", fg="white")
        self.preview_label.pack(pady=(20, 0))

        self.preview_text = tk.Text(self.right_frame, height=10, width=60, state=tk.DISABLED, bg="#2e2e2e", fg="white")
        self.preview_text.pack()

    def extract_info_from_filename(self, filename):
        base = filename.replace('.mp4', '').replace('.avi', '')
        parts = base.split('_')
        mode = 'a' if parts[0] == 'abnormal' else 'n'
        scene = next((int(p) for i, p in enumerate(parts) if parts[i-1] == 'scene'), 0)
        scenario = next((int(p) for i, p in enumerate(parts) if parts[i-1] == 'scenario'), 0)
        known_objects = ['fog', 'fire', 'smoke']
        object_type = parts[-1] if parts[-1] in known_objects else '-'
        return scene, scenario, object_type, mode

    def extract_sort_key(self, filename):
        _, scenario, _, mode = self.extract_info_from_filename(filename)
        is_normal = 1 if mode == 'n' else 0
        return (is_normal, scenario)

    def load_folder(self):
        base = os.path.join(os.getcwd(), "ubnormal")
        folder = filedialog.askdirectory(initialdir=base)
        if not folder:
            return
        self.folder_path = folder
        self.video_list = [f for f in os.listdir(folder) if f.endswith(('.mp4', '.avi'))]
        self.video_list.sort(key=self.extract_sort_key)

        self.video_listbox.delete(0, tk.END)
        for video in self.video_list:
            self.video_listbox.insert(tk.END, video)

    def load_video(self, event):
        selection = self.video_listbox.curselection()
        if not selection:
            return
        filename = self.video_list[selection[0]]
        self.current_video_path = os.path.join(self.folder_path, filename)

        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.current_video_path)
        self.update_frame()

        for _, var in self.check_vars:
            var.set(False)
        self.status_label.config(text="")

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (640, 480))
                self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(self.frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.imgtk = imgtk
                self.root.after(30, self.update_frame)

    def save_annotation(self):
        if not self.current_video_path:
            self.status_label.config(text="Please select a video first!", fg="red")
            return

        filename = os.path.basename(self.current_video_path)
        scene, scenario, object_type, mode = self.extract_info_from_filename(filename)

        lines = []
        for action, var in self.check_vars:
            if var.get():
                line = f"{scene},{scenario},{object_type},{mode},-,-,{action}"
                lines.append(line)

        if lines:
            output_path = os.path.join(self.folder_path, "annotations.txt")
            with open(output_path, 'a') as f:
                for line in lines:
                    f.write(line + '\n')
            self.status_label.config(text="Annotation saved.", fg="green")
        else:
            self.status_label.config(text="No action selected!", fg="orange")

        self.update_preview()

    def update_preview(self):
        output_path = os.path.join(self.folder_path, "annotations.txt")
        if not os.path.exists(output_path):
            return
        try:
            with open(output_path, 'r') as f:
                content = f.read()
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, content)
            self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, f"Error reading file:\n{str(e)}")
            self.preview_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoAnnotator(root)
    root.mainloop()