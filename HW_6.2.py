# Global configuration
GLOBAL_CONFIG = {"feature_a": True, "max_retries": 3}


class Configuration:
    def __init__(self, updates, validator=None):
        self.updates = updates
        self.validator = validator
        self.original_config = None

    def __enter__(self):
        # Save original configuration
        self.original_config = GLOBAL_CONFIG.copy()

        # Apply updates
        GLOBAL_CONFIG.update(self.updates)

        # Validate if validator is provided
        if self.validator and not self.validator(GLOBAL_CONFIG):
            # Restore original before raising error
            GLOBAL_CONFIG.clear()
            GLOBAL_CONFIG.update(self.original_config)
            raise ValueError("Invalid configuration")

        return self  # <-- Return self instead of None

    def __exit__(self, exc_type, exc_value, traceback):
        # Restore original configuration
        GLOBAL_CONFIG.clear()
        GLOBAL_CONFIG.update(self.original_config)
        return False  # Propagate exceptions if any occurred


def validate_config(config):
    """Checks that max_retries >= 0 and feature_a is boolean"""
    return config.get("max_retries", 0) >= 0 and isinstance(config.get("feature_a"), bool)


# Tests
def run_tests():
    print("Initial configuration:", GLOBAL_CONFIG)

    # Test 1: Correct temporary change
    try:
        with Configuration({"max_retries": 5}):
            print("\nTest 1: Temporary change (max_retries=5)")
            print("Inside block:", GLOBAL_CONFIG)
    except Exception as e:
        print("Error:", e)
    print("After block:", GLOBAL_CONFIG)

    # Test 2: Change with validation error (should restore config)
    try:
        with Configuration({"max_retries": -1}, validator=validate_config):
            print("\nTest 2: Invalid change (max_retries=-1)")
            print("This text shouldn't appear")
    except ValueError as e:
        print("\nTest 2: Caught expected error:", e)
    print("After block:", GLOBAL_CONFIG)

    # Test 3: Error inside block (should restore config)
    try:
        with Configuration({"feature_a": False}):
            print("\nTest 3: Change (feature_a=False) with internal error")
            print("Inside block before error:", GLOBAL_CONFIG)
            raise RuntimeError("Artificial error")
    except RuntimeError as e:
        print("Caught error:", e)
    print("After block:", GLOBAL_CONFIG)

    # Test 4: Multiple parameter changes
    try:
        with Configuration({"feature_a": False, "max_retries": 10}, validator=validate_config):
            print("\nTest 4: Multiple changes")
            print("Inside block:", GLOBAL_CONFIG)
    except Exception as e:
        print("Error:", e)
    print("After block:", GLOBAL_CONFIG)

    # Test 5: Invalid data type
    try:
        with Configuration({"feature_a": "not a boolean"}, validator=validate_config):
            print("\nTest 5: Invalid data type")
            print("This text shouldn't appear")
    except ValueError as e:
        print("\nTest 5: Caught expected error:", e)
    print("After block:", GLOBAL_CONFIG)

    # Test 6: Using 'as' to access context manager
    try:
        with Configuration({"max_retries": 7}, validator=validate_config) as config:
            print("\nTest 6: Using 'as' to access context manager")
            print("Inside block:", GLOBAL_CONFIG)
            print("Context manager updates:", config.updates)
    except Exception as e:
        print("Error:", e)
    print("After block:", GLOBAL_CONFIG)


if __name__ == "__main__":
    run_tests()
