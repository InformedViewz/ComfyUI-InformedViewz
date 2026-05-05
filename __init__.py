from .iv_imagesizes import iv_imagesizes_class

NODE_CLASS_MAPPINGS = {
    "InformedViewz Image Sizes": iv_imagesizes_class,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InformedViewz Image Sizes": "Image Size Selector",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
