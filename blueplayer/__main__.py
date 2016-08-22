import sys
import serial
from blueplayer import blueplayer


def main(args):
    # first argument should be a serial terminal to open
    if not len(args):
        port = "/dev/ttyAMA0"
    else:
        port = args[0]

    player = None

    with serial.Serial(port) as serial_port:
        try:
            player = blueplayer.BluePlayer(serial_port)
            player.start()
        except KeyboardInterrupt as ex:
            print("\nBluePlayer cancelled by user")
        except Exception as ex:
            print("How embarrassing. The following error occurred {}".format(ex))
        finally:
            if player:
                player.end()
                player.stop()

if __name__ == "__main__":
    main(sys.argv[1:])
