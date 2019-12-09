import sys, subprocess, shlex, time
import queue

input_command = shlex.split('sudo tcpdump -AUtttvvvXXnns1024 -i lo port 9001 -l')
regex = shlex.split('egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr [0-9]+|length [0-9][0-9]|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"')
thread_queue = queue.Queue()
#regex_obj = re.compile(regex)
#input_command = shlex.split('sudo tcpdump -l -AUtttvvvXXnns1024 -i lo0 port 9001 | egrep -o \"00:00:00.[0-9]+|val [0-9]+|ecr ['
                #'\'0-9]+|length [0-9][0-9|3[0-9]30 3\w\w\w \w\w\w\w \w+|\w+.\w+.\w+.\w+.\w+ > \w+.\w+.\w+.\w+.\w+\"')


def parse_packet(packet_list, change_codes):
    delta_time = ''
    val_timestamp = ''
    ecr_timestamp = ''
    src_port = ''
    dest_port = ''
    length = ''
    payload = '0'
    attack_bit = '0'
    for entry in packet_list:
        p = subprocess.Popen(regex, stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        out = p.communicate(input=entry)[0]
        if out is not None:
            out = out.split('\n')
            # This block always starts with 127.0.0... ip and is always followed by val and ecr timestamps in order
            if out[0].startswith('127.') or out[0].startswith('10.') or out[0].startswith('192.'):
                ip = out[0].split(' > ')
                src = ip[0].split('.')
                src_port = src[4]

                dest = ip[1].split('.')
                dest_port = dest[4]

                val = out[1].split(' ')
                val_timestamp = val[1]

                ecr = out[2].split(' ')
                ecr_timestamp = ecr[1]

            # This block always starts with a delta time (00:00:00...) and followed by length
            elif out[0].startswith('0'):
                temp_timestamp = out[0].split(':')
                temp_timestamp = temp_timestamp[2].split('.')
                delta_time = temp_timestamp[1]

                temp_length = out[1].split(' ')
                length = temp_length[1]

            # This block should contain only the payload, all payloads start with '3'
            elif out[0].startswith('3'):
                hex_payload = out[0].replace(' ', '')
                if change_codes == 1:
                    if hex_payload.startswith('5', 5):
                        hex_payload = hex_payload[0:5] + '0' + hex_payload[6:len(hex_payload)]
                        attack_bit = '1'
                payload = str(int(hex_payload, 16))

        # If no payload block was found, make it 0. Payload block is always the last line
        else:
            payload = '0'

    # If some parts of package are missing, throw it away
    if length == '' or delta_time == '' or src_port == '' or dest_port == '' or val_timestamp == '' or ecr_timestamp == '':
        return None

    if change_codes == 0:
        parsed_packet = [length, delta_time, src_port, dest_port, payload, val_timestamp, ecr_timestamp]
    else:
        parsed_packet = [attack_bit, length, delta_time, src_port, dest_port, payload, val_timestamp, ecr_timestamp]

#    for i in parsed_packet:
#        print(i)
#    print("________________")
    return parsed_packet


def listen_on_network():
    # Main execution
    if sys.argv[1] == '0':
        change_codes = 0
    elif sys.argv[1] == '1':
        change_codes = 1
    else:
        print("Please specify a mode: 0 -> no change; 1 -> change the codes...\n")
        sys.exit()

    packet = []
    line_count = 0

    # Execute the tcpdump command, where it listens live on port 9001 and gives out captured packets in real time
    p = subprocess.Popen(input_command, stdout=subprocess.PIPE, universal_newlines=False)
    time.sleep(5) # Give some time to initialize
    for row in iter(p.stdout.readline, b''):
        new_row = row.rstrip().decode('utf-8')
        packet.append(new_row)
        line_count += 1
        if line_count == 6:
            processed_packet = parse_packet(packet, change_codes)
            if processed_packet is not None:


                # CALL EXTERNAL FUNCTION TO PASS PROCESSED PACKET HERE #    #    #    #
                thread_queue.put(processed_packet)


            # Reset the line count and packet list, ready for the next packet processing
            line_count = 0
            packet.clear()


# Run the script
#listen_on_network()
