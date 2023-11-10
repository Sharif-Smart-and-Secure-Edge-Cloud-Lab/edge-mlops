#!/bin/python

import subprocess
from picamera import PiCamera

def read_proc_stdout(proc):
    return proc.stdout.readline().rstrip()

def write_proc_stdin(proc, data):
    proc.stdin.write(f"{data.rstrip()}\n")
    proc.stdin.flush()

def main():
    camera = PiCamera()
    det_proc = subprocess.Popen(["./mnist-v1"],
                                text=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)

    camera.start_preview(fullscreen=False, window=(10, 10, 640, 640))
    while True:
        print(10*"-")
        print("Enter the working mode (run/quit):", end=" ")
        mode = input()
        if mode == "quit":
            break
        elif mode == "run":
            camera.capture('img.jpg', resize=(640, 640))
            write_proc_stdin(det_proc, mode)
            print("\tRunning the model...")
        else:
            det_proc.stdin.close()
            det_proc.kill()
            camera.stop_preview()
            raise ValueError("\tUnknown mode provided " + mode)

        det_label = read_proc_stdout(det_proc)
        print(f"\tDetected label: {det_label}")
        print(f"\tIs it correct?", end=" ")
        status = input()
        if status == "yes" or status == "1":
            is_correct = "1"
        elif status == "no" or status == "0": # For the sake of simplicity
            is_correct = "0"
        write_proc_stdin(det_proc, is_correct)
        if not int(is_correct):
            print("\tEnter true label:", end=" ")
            true_lable = input()
            write_proc_stdin(det_proc, true_lable)
            print("\tRetraining the model...")
            loss = read_proc_stdout(det_proc)
            print(f"\tTraining loss: {loss}")

    camera.stop_preview()
    det_proc.stdin.close()
    det_proc.kill()
    print("Farewell!")

if __name__ == '__main__':
    main()
