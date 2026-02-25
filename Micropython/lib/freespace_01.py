
def print_free_filespace():
    import os

    # Get filesystem statistics
    statvfs = os.statvfs('/')

    # Calculate free space in bytes
    free_bytes = statvfs[0] * statvfs[3]  # statvfs[0]: block size, statvfs[3]: free blocks

    # Calculate total space in bytes
    total_bytes = statvfs[0] * statvfs[2]  # statvfs[2]: total blocks

    # Convert to kilobytes for readability
    free_kb = free_bytes / 1024
    total_kb = total_bytes / 1024

    print(f"Free space: {free_kb:.2f} KB")
    print(f"Total space: {total_kb:.2f} KB")
    
    return free_bytes, total_bytes


if __name__ == "__main__":
    print_free_filespace()
    