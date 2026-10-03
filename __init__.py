from .iv_imagesizes import iv_imagesizes_class
from .iv_image_metadata_node_IVmod import iv_ImageMetadataSaver, iv_ImageMetadataLoader

NODE_CLASS_MAPPINGS = {
    "InformedViewz Image Sizes": iv_imagesizes_class,
    "InformedViewz Image Savers": iv_ImageMetadataSaver,
    "InformedViewz Image Loaders": iv_ImageMetadataLoader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InformedViewz Image Sizes": "Image Size Selector",
    "InformedViewz Image Savers": "WebP Image Saver with Metadata",
    "InformedViewz Image Loaders": "Image Loader with Metadata and Filename",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
