import protobuf.opq_pb2


def decode_trigger_message(encoded_trigger_message):
    """ Decodes and returns a serialized triggering message

    :param encoded_measurement: The protobuf encoded triggering message
    :return: The decoded TriggerMessage object
    """
    trigger_message = protobuf.opq_pb2.TriggerMessage()
    trigger_message.ParseFromString(encoded_trigger_message)
    return trigger_message

def encode_trigger_message(id,
                           time,
                           frequency,
                           rms):

    trigger_message = protobuf.opq_pb2.TriggerMessage()
    trigger_message.id = id
    trigger_message.time = time
    trigger_message.frequency = frequency
    trigger_message.rms = rms
    return trigger_message.SerializeToString()