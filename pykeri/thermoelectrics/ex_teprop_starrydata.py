from TEProp_starrydata import TEProp

json_filename = "20200608_AllStarrydata.json"

sampleid_array = TEProp(json_filename)

tep_list = []
for sampleid in sampleid_array[:10]:
    try:
        tep_list.append(TEProp(json_filename, sampleid))
        print("sampleid={} appended.".format(sampleid))
    except ValueError:
        print("sampleid={} skipped".format(sampleid))