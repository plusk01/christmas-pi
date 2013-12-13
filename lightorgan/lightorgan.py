import RPi.GPIO as GPIO
from pyalsa import alsaseq #ALSA Sequencer Lib

from subprocess import Popen

#### GPIO INFO ####

# To turn off a percussion, bass, or synth pin, set to None

MELODY_PINS = [3, 5, 7, 11, 13]

PERCUSSION_PIN = 15
BASS_PIN = 19
SYNTH_PIN = 19

TOTAL_PINS = len(MELODY_PINS) + 3

#### ALSA INFO ####

THROUGHPORT_ID = 14
THROUGHPORT_PORT = 0

#### MIDI PROCESSING INFO ####

# currently playing note, by pin
pinNotes = {}

# currently playing channel, by pin
pinChannels = {}

# enabled MIDI channels
playChannels = {}

# max number of MIDI channels
CHANNEL_COUNT = 16

# static percussion bool; keep track globally if it's on/off
percussionOn = False


def setup_pins():
	Popen(['gpio reset'])

	# Use header pin number convention, as opposed to BCM convention
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(PERCUSSION_PIN, GPIO.OUT)
	GPIO.setup(BASS_PIN, GPIO.OUT)
	GPIO.setup(SYNTH_PIN, GPIO.OUT)

	for pin in MELODY_PINS:
		GPIO.setup(pin, GPIO.OUT)

def digital_write(pin, on):
	if on:
		print "PIN " + str(pin) + " HIGH"
		try:
			GPIO.output(pin, GPIO.HIGH)
		except:
			pass
	else:
		print "PIN " + str(pin) + " LOW"
		try:
			GPIO.output(pin, GPIO.LOW)
		except:
			pass

def choose_pin(note, channel):
	instrument = playChannels[channel]

	if is_percussion(instrument):
		return PERCUSSION_PIN

	elif is_bass(instrument):
		return BASS_PIN

	elif is_synth(instrument):
		return SYNTH_PIN

	else:
		# it's a melody type instrument
		# there are 12 notes in an octave, so to find the pitch use the modulus
		pitch = note % 12

		# the pin to use is determined by:
		# 	(pitch / (# of notes / # of melody pins))
		pin_index = pitch / (12.0 / len(MELODY_PINS))

		return MELODY_PINS[int(pin_index)]

def clear_pin_states():
	pinNotes = {}
	pinChannels = {}

def set_channel_instrument(channel, instrument):
	# keep track which instrument is on what channel
	playChannels[channel] = instrument

def is_percussion_channel(channel):
	instrument = playChannels[channel]
	return is_percussion(instrument)

def is_percussion(instrument):
	return instrument >= 8 and instrument <= 15

def is_synth(instrument):
	return instrument >= 88 and instrument <= 103

def is_bass(instrument):
	instrument >= 32 and instrument <= 39

def midi_open():
	handler = alsaseq.Sequencer('default', 'lightorganpy')
	my_port = handler.create_simple_port('listen:in', alsaseq.SEQ_PORT_TYPE_APPLICATION, alsaseq.SEQ_PORT_CAP_WRITE|alsaseq.SEQ_PORT_CAP_SUBS_WRITE)

	client_info = handler.get_client_info()

	#connect the throughport to this app's port
	handler.connect_ports((THROUGHPORT_ID, THROUGHPORT_PORT), (client_info['id'], my_port))

	return handler

def midi_process(event):
	data = event.get_data()

	# If the event is a PMGCHANGE, it's a request to setup a specific insrument on a channel [0-15]
	# also, it's probably the beginning of a new song
	if event.type == alsaseq.SEQ_EVENT_PGMCHANGE:
		print "PGMCHANGE: channel " + str(data['control.channel']) + "; instrument " + str(data['control.value'])

		# clear all the pin states (the current note, the current channel)
		clear_pin_states()

		set_channel_instrument(data['control.channel'], data['control.value']);

	# Note on or off event
	elif event.type == alsaseq.SEQ_EVENT_NOTEON or event.type == alsaseq.SEQ_EVENT_NOTEOFF:

		pin = choose_pin(data['note.note'], data['note.channel'])

		if not is_percussion_channel(data['note.channel']):

			# NOTE: velocity == 0 is the same as a NOTEOFF event
			turn_pin_on = not (data['note.velocity'] == 0 or event.type == alsaseq.SEQ_EVENT_NOTEOFF)

			if turn_pin_on:
				# if pin is currently available to play a note,
				# or it currently playing channel can be overriden due to a
				# higher priority channel (0 being most important), ...
				if not pin in pinNotes or (not pin in pinChannels or pinChannels[pin] > data['note.channel']):

					# turn pin on, and save the note to pinNotes, and channel to pinChannels
					digital_write(pin, True)
					pinNotes[pin] = data['note.note']
					pinChannels[pin] = data['note.channel']
					# for debugging:
					print_pin_info(pin, data, True)

			# else, turn pin off
			else:
				# if this is the note/channel that turned the pin on ...
				if pin in pinNotes and pinNotes[pin] == data['note.note'] and pin in pinChannels and pinChannels[pin] == data['note.channel']:
					# turn pin off, indicate that this pin is now available
					digital_write(pin, False)
					del pinNotes[pin]
					del pinChannels[pin]
					# for debugging:
					print_pin_info(pin, data, False)

		# else, this is a percussion channel
		else:
			# if percussion pin enabled
			if PERCUSSION_PIN:
				# flip the value
				global percussionOn
				digital_write(pin, not percussionOn)
				percussionOn = not percussionOn

###### DEBUG METHODS #######

def print_pin_info(pin, data, on=True):
	print "Pin " + str(pin) + " " + 'on' if on else 'off' + ". [Note=" + str(data['note.note']) + "] [Channel=" + str(data['note.channel']) + "]"

### MAIN CODE ###

setup_pins()

seq = midi_open()

while True:
	events = seq.receive_events()
	for event in events:
		try:
			midi_process(event)
		except:
			pass
