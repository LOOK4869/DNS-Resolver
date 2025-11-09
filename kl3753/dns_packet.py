import struct
import socket
import random

class DNSPacket:
    @staticmethod
    def build_query(domain, qtype=1, qclass=1):
        id = random.randint(0, 65535)
        flags = 0x0000 
        qdcount = 1
        ancount = 0
        nscount = 0
        arcount = 0
        
        header = struct.pack('!HHHHHH', id, flags, qdcount, ancount, nscount, arcount)
        
        qname = DNSPacket.build_domain_name(domain)
        question = qname + struct.pack('!HH', qtype, qclass)
        
        return header + question

    @staticmethod
    def build_domain_name(domain):
        labels = domain.split('.')
        result = b''
        for label in labels:
            if label:  
                result += struct.pack('B', len(label))
                result += label.encode('utf-8')
        result += b'\x00'
        return result

    @staticmethod
    def build_response(query_data, answers):
        try:
            query_id = struct.unpack('!H', query_data[0:2])[0]
            
            flags = 0x8180  # QR=1, RA=1, RCODE=0
            qdcount = 1
            ancount = len(answers)
            nscount = 0
            arcount = 0
            
            header = struct.pack('!HHHHHH', query_id, flags, qdcount, ancount, nscount, arcount)
            
            offset = 12
            while offset < len(query_data) and query_data[offset] != 0:
                offset += query_data[offset] + 1
            if offset < len(query_data):
                offset += 5  # 跳过null字节和QTYPE、QCLASS
            
            question_section = query_data[12:offset]
            
            answer_section = b''
            for answer in answers:
                name = b'\xc0\x0c'  
                rdata = socket.inet_aton(answer['ip'])
                rdlength = len(rdata)
                ttl = answer.get('ttl', 300)
                
                answer_record = name + struct.pack('!HHIH', 
                                                 answer['type'], answer['class'],
                                                 ttl, rdlength)
                answer_record += rdata
                answer_section += answer_record
            
            return header + question_section + answer_section
            
        except Exception as e:
            print(f"Error building response: {e}")
            return None

    @staticmethod
    def parse_query(data):
        try:
            id = struct.unpack('!H', data[0:2])[0]
            flags = struct.unpack('!H', data[2:4])[0]
            qdcount = struct.unpack('!H', data[4:6])[0]
            
            offset = 12
            questions = []
            for _ in range(qdcount):
                qname, offset = DNSPacket.parse_domain_name(data, offset)
                qtype = struct.unpack('!H', data[offset:offset+2])[0]
                qclass = struct.unpack('!H', data[offset+2:offset+4])[0]
                offset += 4
                questions.append({
                    'qname': qname,
                    'qtype': qtype,
                    'qclass': qclass
                })
            
            return {
                'id': id,
                'flags': flags,
                'questions': questions
            }
        except Exception as e:
            print(f"Error parsing query: {e}")
            return None

    @staticmethod
    def parse_domain_name(data, offset):
        labels = []
        original_offset = offset
        
        while True:
            if offset >= len(data):
                break
                
            length = data[offset]
            if length == 0:
                offset += 1
                break

            if length & 0xC0 == 0xC0:
                pointer = struct.unpack('!H', data[offset:offset+2])[0] & 0x3FFF
                label, _ = DNSPacket.parse_domain_name(data, pointer)
                labels.append(label)
                offset += 2
                break
            else:
                offset += 1
                label = data[offset:offset+length].decode('utf-8', errors='ignore')
                labels.append(label)
                offset += length
        
        return '.'.join(labels), offset