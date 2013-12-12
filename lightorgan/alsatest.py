from pyalsa import alsaseq

#### ALSA INFO ####

THROUGHPORT_ID = 14
THROUGHPORT_PORT = 0


def dump(event):
    print "event: %s" % event
    print "  ",
    for attr in alsaseq.SeqEvent.__dict__:
        if attr.startswith('is_'):
            t = event.__getattribute__(attr)
            if t:
                print "%s" % attr,
    print
    data = event.get_data()
    print "  data=%s" % data

handler = alsaseq.Sequencer('default', 'lightorganpytest')
my_port = handler.create_simple_port('listen:in', alsaseq.SEQ_PORT_TYPE_APPLICATION, alsaseq.SEQ_PORT_CAP_WRITE)

client_info = handler.get_client_info()

#connect the throughport to this app's port
src = (alsaseq.SEQ_CLIENT_SYSTEM,alsaseq.SEQ_PORT_SYSTEM_ANNOUNCE)
handler.connect_ports((THROUGHPORT_ID, THROUGHPORT_PORT), (client_info['id'], my_port))



while True:
	events = handler.receive_events(5000)
	for event in events:
		dump(event)