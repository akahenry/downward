import os


def count_run_log_files(folder_path):
    count = 0

    # Walk through the directory and its subdirectories
    for _, _, files in os.walk(folder_path):
        for file in files:
            if file == "run.log":
                count += 1

    return count


if __name__ == "__main__":
    folder_path = "./experiments/lab/data/main"

    try:
        while True:
            run_log_count = count_run_log_files(folder_path)
            print(f"Number of run.log files: {run_log_count}", end="\r")
    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Exiting...")
