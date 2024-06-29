import logging
import time


def is_this_a_log_file(output_list):
    # Key to check
    key_to_check_for = 'A_platformId_A_sourceID'
    first_dict = output_list[0]
    # Access the inner dictionary
    inner_dict = first_dict.get('data')
    if key_to_check_for in inner_dict:
        return True
    return False


def time_of_data_generation():
    right_indent = 1e9
    current_time = time.time()
    seconds = int(current_time)
    fractional_seconds = current_time - seconds
    nanoseconds = int(fractional_seconds * right_indent)
    return seconds, nanoseconds


# make the entry to be red for 1 second
def blink_entry_red(entry_widget):
    original_bg = entry_widget.cget("background")
    entry_widget.config(background="red")
    entry_widget.after(1000, lambda: entry_widget.config(background=original_bg))


# check if there is an empty entry
def validate_entry(entry, condition, error_message):
    if condition:
        if entry.get() == '':
            logging.error(error_message)
            blink_entry_red(entry)
            return False
    return True
