import tello
import time


def init_drone():
    d = tello.TelloControl()
    if d.initialize() is False:
        exit()
    d.status()
    return d


def main():
    drone = init_drone()

    drone.takeoff()
    drone.land()
    drone.status()

    drone.terminate()


if __name__ == "__main__":
    main()
