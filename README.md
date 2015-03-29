`ch_stations_all.csv` contains a list of (id, station_name, lat, lon)

7872705 Brodski Stupnik 45.160682       17.795189
7872706 Oriovac 45.15918        17.756221
7872707 Luzani-Malino   45.170408       17.716785

This file contains 71882 entries. We need to get the connections from Vienna
to each of these cities. Vienna's id is 8101003.

*************

Get the connections for each city in ch_stations_shuffled.tsv

    mkdir all_times_vienna
    cat ch_stations_shuffled.tsv | awk '{print 8101003,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_vienna 2> times_err.csv

    mkdir all_times_paris
    cat ch_stations_shuffled.tsv | awk '{print 8711300,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_paris 2> times_err.csv

    mkdir all_times_london
    cat ch_stations_shuffled.tsv | awk '{print 7015400,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_london 2> times_err.csv

    mkdir all_times_jena
    cat ch_stations_shuffled.tsv | awk '{print 8016418,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_jena 2> times_err.csv

    mkdir all_times_berlin
    cat ch_stations_shuffled.tsv | awk '{print 8031922,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_berlin 2> times_err_berlin.csv

    city=madrid; id=007117000; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 007117000,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=rome; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 008308409,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=geneva; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 008501008,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=brussels; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 008814001,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=amsterdam; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 008400058,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=copenhagen; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 008600626,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=oslo; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 007600100,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=stockholm; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 007403751,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv

    city=helsinki; mkdir all_times_${city}
    cat ch_stations_shuffled.tsv | awk '{print 001000001,$1;}' |  xargs -n 2 python scripts/get_times.py -c -o all_times_${city} 2> times_err_${city}.csv


    city=london; find all_times_${city}/ -type f  > file_list_${city}.txt; python scripts/parse_connections.py -l file_list_${city}.txt > all_connections_${city}.json
    for city in vienna jena london berlin paris; do /usr/bin/time python scripts/create_grid.py all_connections_${city}.json -r 10 --min-x -12.4 --max-x 36.3 --min-y 33.1 --max-y 64.5 > grid_${city}.json; done;

where the r parameter indicates the resolution of the grid
