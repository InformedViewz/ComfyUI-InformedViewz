"""Sixteen-way one-hot decoder for ComfyUI."""


class iv_onehot_class:
    """Set only the boolean output at index i to True (zero-based)."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "i": (
                    "INT",
                    {
                        "default": 0,
                        "forceInput": True,
                        "tooltip": "Zero-based output index (0-15). Values outside this range set all outputs to False.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("BOOLEAN",) * 16
    RETURN_NAMES = tuple(f"out_{index}" for index in range(16))
    FUNCTION = "one_hot"
    CATEGORY = "utils/selectors"
    DESCRIPTION = "Convert an integer index to 16 individual boolean outputs; only the selected output is True."

    def one_hot(self, i):
        return tuple(index == i for index in range(16))