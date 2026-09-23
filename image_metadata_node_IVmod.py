# Originally Developed by Light-x02
# https://github.com/Light-x02/ComfyUI-Lightx02-Node
# mod'ed by InformedViewz
import os
import json
import datetime
from PIL import Image
import numpy as np
from comfy.comfy_types import ComfyNodeABC
import folder_paths

# Node to save WebP images with metadata
class ImageMetadataSaver(ComfyNodeABC):
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.quality = 93

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. Supports: %date:yyyy-MM-dd%, %date:yyyy-MM%, %date:yyyy%, %date:MM%, %date:dd%, %time:HH-mm-ss%, %time:HH%, %time:mm%, %time:ss%, %datetime:full% (filename only)."}),
                "subdirectory_name": ("STRING", {"default": "", "tooltip": "Optional subdirectory. Avoid using %datetime:full% here to prevent excessive nesting."})
            },
            "optional": {
                "metadata": ("METADATA", {})
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "💡Lightx02/utilities"
    DESCRIPTION = "Saves WebP images at quality 93 with metadata stored in EXIF."

    def save_images(self, images, metadata=None, filename_prefix="ComfyUI", subdirectory_name=""):
        if metadata is None:
            metadata = {}

        if "%datetime:full%" in subdirectory_name:
            raise ValueError("The placeholder %datetime:full% is not allowed in subdirectory_name to avoid excessive folder nesting.")

        now = datetime.datetime.now()
        replacements = {
            "%date:yyyy-MM-dd%": now.strftime("%Y-%m-%d"),
            "%date:yyyy-MM%": now.strftime("%Y-%m"),
            "%date:yyyy%": now.strftime("%Y"),
            "%date:MM%": now.strftime("%m"),
            "%date:dd%": now.strftime("%d"),
            "%time:HH-mm-ss%": now.strftime("%H-%M-%S"),
            "%time:HH%": now.strftime("%H"),
            "%time:mm%": now.strftime("%M"),
            "%time:ss%": now.strftime("%S"),
            "%datetime:full%": now.strftime("%Y-%m-%d_%H-%M-%S")
        }

        for key, value in replacements.items():
            filename_prefix = filename_prefix.replace(key, value)
            if key != "%datetime:full%":
                subdirectory_name = subdirectory_name.replace(key, value)

        filename_prefix += self.prefix_append
        if subdirectory_name:
            full_output_folder = os.path.join(self.output_dir, subdirectory_name)
        else:
            full_output_folder = self.output_dir

        os.makedirs(full_output_folder, exist_ok=True)

        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, full_output_folder, images[0].shape[1], images[0].shape[0]
        )
        results = []
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            exif = Image.Exif()
            # WebP has no PNG text chunks; preserve all metadata as JSON.
            exif[0x010E] = json.dumps(metadata, ensure_ascii=True)  # ImageDescription
            # ComfyUI uses Make/Model for prompt/workflow metadata in WebP.
            for key, tag in (("prompt", 0x0110), ("workflow", 0x010F)):
                if key in metadata:
                    value = metadata[key]
                    text = value if isinstance(value, str) else json.dumps(value)
                    exif[tag] = f"{key}:{text}"

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.webp"

            img.save(os.path.join(full_output_folder, file), format="WEBP", quality=self.quality, exif=exif.tobytes())
            results.append({
                "filename": file,
                "subfolder": os.path.join(subfolder, subdirectory_name) if subdirectory_name else subfolder,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}}


# Register the saver node
NODE_CLASS_MAPPINGS = {
    "ImageMetadataSaver": ImageMetadataSaver
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageMetadataSaver": "📝✅ Image Metadata Saver"

}




