class iv_imagesizes_class:
    """
    Dropdown selector that maps custom text labels to two integer outputs.
    """

    # The keys are the text shown in the dropdown.
    # The values are the two INT outputs.
    CHOICE_TO_PAIR = {
        "~1MP Square 1:1 (1024, 1024) for Flux.2 Gen": (1024, 1024),
        "~1MP Portrait 1:1.5 (832, 1248) for Flux.2 Gen": (832, 1248),
        "~1MP Portrait 1:1.75 ~9:16 (768, 1344) for Flux.2 Gen": (768, 1344),
        "~1MP Portrait 1:2 (720, 1440) for Flux.2 Gen": (720, 1440),
        "~1MP Landscape 1.5:1 (1248, 832) for Flux.2 Gen": (1248, 832),
        "~1MP Landscape 1.75:1 ~16:9 (1344, 768) for Flux.2 Gen": (1344, 768),
        "~1MP Landscape 2:1 (1440, 720) for Flux.2 Gen": (1440, 720),
        "1.5MP+ Square 1:1 (1328, 1328) for Qwen Gen": (1328, 1328),
        "1.5MP+ Portrait 1:1.5 (1056, 1584) for Qwen Gen": (1056, 1584),
        "1.5MP+ Portrait ~1:1.8 ~9:16 (928, 1664) for Qwen Gen": (928, 1664),
        "1.5MP+ Portrait 1:2 (928, 1856) for Qwen Gen": (928, 1856),
        "1.5MP+ Landscape 1.5:1 (1584, 1056) for Qwen Gen": (1584, 1056),
        "1.5MP+ Landscape ~1.8:1 ~16:9 (1664, 928) for Qwen Gen": (1664, 928),
        "1.5MP+ Landscape 2:1 (1856, 928) for Qwen Gen": (1856, 928),
        "4MP+ Square 1:1 (2048, 2048) for Output": (2048, 2048),
        "4MP+ Portrait 1:1.5 (2048, 3072) for Output": (2048, 3072),
        "4MP+ Portrait ~1:1.8 ~9:16 (2160, 3840) for Output": (2160, 3840),
        "4MP+ Portrait 1:2 (2048, 4096) for Output": (2048, 4096),
        "4MP+ Landscape 1.5:1 (3072, 2048) for Output": (3072, 2048),
        "4MP+ Landscape ~1.8:1 ~16:9 (3840, 2160) for Output": (3840, 2160),
        "4MP+ Landscape 2:1 (4096, 2048) for Output": (4096, 2048),
    }

    @classmethod
    def INPUT_TYPES(cls):
        choices = list(cls.CHOICE_TO_PAIR.keys())

        return {
            "required": {
                "selection": (
                    choices,
                    {
                        "default": choices[0],
                        "tooltip": "Select a preset. Each label maps to two integer outputs.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("INT", "INT")
    RETURN_NAMES = ("width", "height")

    FUNCTION = "get_pair"
    CATEGORY = "utils/selectors"

    def get_pair(self, selection):
        int_a, int_b = self.CHOICE_TO_PAIR[selection]
        return (int_a, int_b)
