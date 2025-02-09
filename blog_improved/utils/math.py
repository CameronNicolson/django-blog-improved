class RangeClamper:
    def __init__(self, max_offset_percent=20):
        """
        WidthNegotiator performs a clamping-like function, but with a
        negotiable range rather than a strict clamp.

        Initialise the negotiator with an allowed offset percentage.

        :param max_offset_percent: The maximum allowable offset 
        as a percentage.
        """
        if not isinstance(max_offset_percent, int):
            raise ValueError("max_offset_percent must be an integer type")
        self.max_offset_percent = max_offset_percent

    def negotiate(self, value, min_value, max_value):
        """
        Negotiate a value against the maximum allowed value.

        :param value: The input value to evaluate.
        :param max_value: The maximum allowable value.
        :return: Adjusted value if within the offset range, otherwise None.
        """
        min_limit = min_value - (max_value * self.max_offset_percent / 100) 
        max_limit = max_value + (max_value * self.max_offset_percent / 100)
        if value <= min_value and value >= min_limit:
            return min_value
        elif value > min_value and value <= max_limit:
            return min(value, max_value)
        return None

