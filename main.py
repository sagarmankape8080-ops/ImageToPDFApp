import os
from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from PIL import Image


class ImageToPDFApp(App):
    def build(self):
        self.selected_images = []
        self.request_android_permissions()

        self.layout = BoxLayout(orientation='vertical')

        self.filechooser = FileChooserIconView(
            filters=['*.png', '*.jpg', '*.jpeg'],
            multiselect=True
        )
        self.filechooser.path = self.get_start_path()
        self.filechooser.bind(selection=self.on_select)
        self.layout.add_widget(self.filechooser)

        quality_label = Label(text="Compression Quality (10 = chota size, 95 = best quality)",
                               size_hint_y=None, height=30)
        self.layout.add_widget(quality_label)

        self.quality_slider = Slider(min=10, max=95, value=70, size_hint_y=None, height=40)
        self.layout.add_widget(self.quality_slider)

        self.status_label = Label(text="Images select karo, phir Convert dabao",
                                   size_hint_y=None, height=60)
        self.layout.add_widget(self.status_label)

        convert_btn = Button(text="Convert to PDF (Compressed)", size_hint_y=None, height=60)
        convert_btn.bind(on_press=self.convert_to_pdf)
        self.layout.add_widget(convert_btn)

        return self.layout

    def request_android_permissions(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
        except Exception:
            pass  # Pydroid 3 / desktop testing mein yeh fail ho sakta hai, ignore karo

    def get_start_path(self):
        try:
            from android.storage import primary_external_storage_path
            return primary_external_storage_path()
        except Exception:
            return os.path.expanduser("~")

    def on_select(self, instance, value):
        self.selected_images = value

    def convert_to_pdf(self, instance):
        if not self.selected_images:
            self.status_label.text = "Pehle images select karo!"
            return

        try:
            quality = int(self.quality_slider.value)
            compressed_images = []
            temp_files = []

            for img_path in self.selected_images:
                img = Image.open(img_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                temp_path = img_path + "_temp_compressed.jpg"
                img.save(temp_path, "JPEG", quality=quality, optimize=True)
                temp_files.append(temp_path)
                compressed_images.append(Image.open(temp_path))

            output_dir = self.get_start_path()
            output_path = os.path.join(output_dir, "converted_output.pdf")

            first_image = compressed_images[0]
            rest_images = compressed_images[1:]
            first_image.save(output_path, save_all=True, append_images=rest_images)

            for f in temp_files:
                try:
                    os.remove(f)
                except Exception:
                    pass

            size_kb = round(os.path.getsize(output_path) / 1024, 1)
            self.status_label.text = f"PDF Saved ({size_kb} KB):\n{output_path}"

        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"


if __name__ == "__main__":
    ImageToPDFApp().run()
