import RPi.GPIO as GPIO
import alsaseq #ALSA Sequencer Lib

#### GPIO INFO ####

MELODY_PINS = [3, 5, 7, 11, 13]

PERCUSSION_PIN = 5
BASS_PIN = 6
SYNTH_PIN = 6

#### ALSA INFO ####

THROUGHPORT_ID = 14
THROUGHPORT_PORT = 0

def setup_pins():
	# Use header pin number convention, as opposed to BCM convention
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(PERCUSSION_PIN, GPIO.OUT)
	GPIO.setup(BASS_PIN, GPIO.OUT)
	GPIO.setup(SYNTH_PIN, GPIO.OUT)

	for pin in MELODY_PINS:
		GPIO.setup(pin, GPIO.OUT)

def digitalWrite(pin, on):
	if on:
		GPIO.output(pin, GPIO.HIGH)
	else:
		GPIO.output(pin, GPIO.LOW)

def midi_open():
	handler = alsaseq.Sequencer('default', 'lightorganpy', alsaseq.SEQ_OPEN_INPUT, alsaseq.SEQ_NONBLOCK, 1)
	my_port = handler.create_simple_port('listen:in', alsaseq.SEQ_PORT_TYPE_APPLICATION, alsaseq.SEQ_PORT_CAP_WRITE|alsaseq.SEQ_PORT_CAP_SUBS_WRITE)

	client_info = handler.get_client_info()

	#connect the throughport to this app's port
	handler.connect_ports((THROUGHPORT_ID, THROUGHPORT_PORT), (client_info['id'], my_port))

	return handler

def midi_process(event):
