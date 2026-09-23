# Originally Developed by Light-x02
# https://github.com/Light-x02/ComfyUI-Lightx02-Node
# mod'ed by InformedViewz for ComfyUI-InformedViewz
import os
import json
import datetime
import struct
from PIL import Image, ImageOps, ImageSequence
import numpy as np
import torch
from comfy.comfy_types import ComfyNodeABC
import folder_paths

# Node to save WebP images with metadata
class iv_ImageMetadataSaver(ComfyNodeABC):
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
    CATEGORY = "InformedViewz"
    DESCRIPTION = "Saves WebP images at quality 93 with EXIF, ICC, XMP and JSON-compatible metadata. Unsupported metadata entries are discarded."

    @staticmethod
    def _webp_metadata(metadata):
        """Keep native WebP metadata and discard non-JSON custom entries."""
        save_options = {}
        exif = Image.Exif()
        raw_exif = metadata.get("exif")
        if isinstance(raw_exif, (bytes, bytearray)):
            try:
                exif.load(bytes(raw_exif))
                # Force parsing/serialization now to catch malformed EXIF.
                exif.tobytes()
            except (OSError, ValueError, TypeError, SyntaxError, KeyError, IndexError, struct.error):
                exif = Image.Exif()

        for key in ("icc_profile", "xmp"):
            value = metadata.get(key)
            if key == "xmp" and isinstance(value, str):
                value = value.encode("utf-8")
            if isinstance(value, (bytes, bytearray)):
                save_options[key] = bytes(value)

        compatible = {}
        for key, value in metadata.items():
            if not isinstance(key, str) or key in ("exif", "icc_profile", "xmp"):
                continue
            try:
                json.dumps(value, ensure_ascii=True, allow_nan=False)
            except (TypeError, ValueError, OverflowError, RecursionError):
                # Drop the whole entry if it contains unsupported nested values.
                continue
            compatible[key] = value

        exif[0x010E] = json.dumps(compatible, ensure_ascii=True, allow_nan=False)
        # ComfyUI uses Model/Make for prompt/workflow metadata in WebP.
        for key, tag in (("prompt", 0x0110), ("workflow", 0x010F)):
            if key in compatible:
                value = compatible[key]
                text = value if isinstance(value, str) else json.dumps(value, allow_nan=False)
                exif[tag] = f"{key}:{text}"
        save_options["exif"] = exif.tobytes()
        return save_options

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
        save_options = self._webp_metadata(metadata)
        results = []
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.webp"

            img.save(os.path.join(full_output_folder, file), format="WEBP", quality=self.quality, **save_options)
            results.append({
                "filename": file,
                "subfolder": os.path.join(subdirectory_name, subfolder) if subdirectory_name else subfolder,
                "type": self.type
            })
            counter += 1

        return {"ui": {"images": results}}


# Node to load image with metadata
class iv_ImageMetadataLoader(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {"required": {"image": (sorted(files), {"image_upload": True})}}

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True

    CATEGORY = "InformedViewz"
    RETURN_TYPES = ("IMAGE", "METADATA", "MASK", "STRING")
    RETURN_NAMES = ("image", "metadata", "mask", "filename")
    FUNCTION = "load_image_with_metadata"
    DESCRIPTION = "Loads images with original metadata and returns the filename with extension."

    def load_image_with_metadata(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)

        metadata = img.info.copy()
        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']

        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)
            if frame.mode == 'I':
                frame = frame.point(lambda x: x * (1 / 255))
            rgb_frame = frame.convert("RGB")

            if len(output_images) == 0:
                w, h = rgb_frame.size

            if rgb_frame.size != (w, h):
                continue

            image_tensor = np.array(rgb_frame).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_tensor)[None,]
            output_images.append(image_tensor)

            if 'A' in frame.getbands():
                mask = np.array(frame.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            elif frame.mode == 'P' and 'transparency' in frame.info:
                mask = np.array(frame.convert('RGBA').getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((h, w), dtype=torch.float32, device="cpu")
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, metadata, output_mask, os.path.basename(image_path))


# Register the saver and loader nodes
NODE_CLASS_MAPPINGS = {
    "InformedViewz Image Savers": iv_ImageMetadataSaver,
    "InformedViewz Image Loaders": iv_ImageMetadataLoader
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InformedViewz Image Savers": "WebP Image Saver with Metadata",
    "InformedViewz Image Loaders": "Image Loader with Metadata and Filename"
}




