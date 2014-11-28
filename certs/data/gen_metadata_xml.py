import sys

with open('sp_metadata_tp.xml', 'r') as sp_metadata_tp:
    sp_metadata_xml_tp = sp_metadata_tp.read()

start = False
end = False
certdata = ''

sp_cert_data = file('cacert.pem', 'r')

for line in sp_cert_data:
    if line.startswith('-----BEGIN CERT'):
        start = True
        continue

    elif line.startswith('-----END CERT'):
        end = True

    if start and not end:
        certdata += line.strip('\n ')

sp_cert_data.close()

sp_metadata_xml = sp_metadata_xml_tp % {
    'cert': certdata,
    'host': sys.argv[1],
}

with open('../out/sp_meta.xml', 'w') as sp_meta_out:
    sp_meta_out.write(sp_metadata_xml)
