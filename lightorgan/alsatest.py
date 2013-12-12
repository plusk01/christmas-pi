from pyalsa import alsaseq

handler = alsaseq.Sequencer('default', 'lightorganpytest', alsaseq.SEQ_OPEN_INPUT, alsaseq.SEQ_NONBLOCK, 1)
my_port = handler.create_simple_port('listen:in', alsaseq.SEQ_PORT_TYPE_APPLICATION, alsaseq.SEQ_PORT_CAP_WRITE|alsaseq.SEQ_PORT_CAP_SUBS_WRITE)

client_info = handler.get_client_info()

#connect the throughport to this app's port
handler.connect_ports((THROUGHPORT_ID, THROUGHPORT_PORT), (client_info['id'], my_port))