import json

import numpy as np
import numpy
import os.path as op
import sys
from numpy import log, exp
from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    
    Courtesy of:
    
    http://stackoverflow.com/a/4913653/899470
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6371 km is the radius of the Earth
    km = 6371 * c

    return km 

def get_connection_coordinates_and_times(connections_filename):
    distances = dict()

    with open(connections_filename, 'r') as f:
        connection_times = json.load(f)

        xs = []
        ys = []
        zs = []

        for connection in connection_times:
            #if connection['to']['coordinate']['x'] < 50:
            x = connection['to']['coordinate']['y']
            y = connection['to']['coordinate']['x']

            from_x = connection['from']['coordinate']['x']
            from_y = connection['from']['coordinate']['y']

            distances[(from_x, from_y)] = 0

            z = [connection['duration']]

            if y > 90:
                print >>sys.stderr, "continuing:", connection
                continue

            if (x,y) in distances:
                if z[0] < distances[(x,y)]:
                    #print >>sys.stderr, "found faster:", connection
                    distances[(x,y)] = z[0]
                continue
                
            xs += [x]
            ys += [y]
            zs += [z]

            distances[(x,y)] = z[0]

    #scatter(xs,ys,c=log(zs), alpha=0.5)
    max_z = log(max(zs))
    
    return (distances, xs,ys,zs, from_x, from_y)
    
def create_grid(distances, xs, ys, zs, res):
    min_x, max_x = min(xs)-3, max(xs)
    min_y, max_y = min(ys)-3, max(ys)
    max_z = log(max(zs))

    grid_x, grid_y = np.mgrid[min_x:max_x:res, min_y:max_y:res]
    
    grid_z = [max_z[0]] * len(grid_x.ravel())
    ravelled_x = grid_x.ravel()
    ravelled_y = grid_y.ravel()

    for i,_ in enumerate(ravelled_x):
        sys.stderr.write("{} ".format(i))
        sys.stderr.flush()
        target_x = ravelled_x[i]
        target_y = ravelled_y[i]

        for (source_x, source_y) in distances.keys():
            station_to_target = haversine(target_x, target_y,
                                                   source_x, source_y)

            mult = 50
            if log(mult * station_to_target + distances[(source_x, source_y)]) < grid_z[i]:
                grid_z[i] =  log(mult * station_to_target + distances[(source_x, source_y)])

    grid_z = np.array(grid_z).reshape(grid_x.shape)
    return (grid_x, grid_y, grid_z)

def expand_grid(grid, curr_index, direction, function):
    # apply a function to this cell in the grid
    # and then recurse into its neighbors
    #print "curr_pos:", curr_index, "direction:", direction
    if curr_index[0] < 0 or curr_index[0] >= grid.shape[0]:
        return
    if curr_index[1] < 0 or curr_index[1] >= grid.shape[1]:
        return

    if direction == (0,0):
        return

    direction = np.array(direction)
    curr_index = np.array(map(int, curr_index))

    if not function(grid, curr_index):
        return

    if tuple(direction) == (1,1):
        expand_grid(grid, curr_index + np.array([1,1]), (1,1), function)
        expand_grid(grid, curr_index + np.array([1,0]), (1,0), function)
        expand_grid(grid, curr_index + np.array([0,1]), (0,1), function)
    elif tuple(direction) == (-1,1):
        expand_grid(grid, curr_index + np.array([-1,1]), (-1,1), function)
        expand_grid(grid, curr_index + np.array([-1,0]), (-1,0), function)
        expand_grid(grid, curr_index + np.array([0,1]), (0,1), function)
    elif tuple(direction) == (1,-1):
        expand_grid(grid, curr_index + np.array([1,-1]), (1,-1), function)
        expand_grid(grid, curr_index + np.array([1,0]), (1,0), function)
        expand_grid(grid, curr_index + np.array([0,-1]), (0,-1), function)
    elif tuple(direction) == (-1,-1):
        expand_grid(grid, curr_index + np.array([-1,-1]), (-1,-1), function)
        expand_grid(grid, curr_index + np.array([-1,0]), (-1,0), function)
        expand_grid(grid, curr_index + np.array([0,-1]), (0,-1), function)
    else:
        expand_grid(grid, curr_index + direction, tuple(direction), function)

def create_grid2(distances, xs, ys, zs, res, min_x, max_x, min_y, max_y, walking_speed=5):
    if min_x is None:
        min_x = min(xs) - 3
    if max_x is None:
        max_x = max(xs)
    if min_y is None:
        min_y = min(ys)
    if max_y is None:
        max_y = max(ys)

    from mpl_toolkits.basemap import Basemap

    print >>sys.stderr, "resolution:", res
    my_map = Basemap(llcrnrlon=min_x,llcrnrlat=min_y,
                  urcrnrlon=max_x,urcrnrlat=max_y,\
                rsphere=(6378137.00,6356752.3142),\
                resolution='l',area_thresh=1000.,projection='merc',\
                lat_1=50.,lon_0=-107.)# draw coastlines, country boundaries, fill continents.

    is_land = dict()

    '''
    min_x, max_x = min(xs)-3, max(xs)
    min_y, max_y = min(ys)-3, max(ys)
    '''
    max_z = log(max(zs))
    max_value = 10800

    grid_x, grid_y = np.mgrid[min_x:max_x:res, min_y:max_y:res]
    grid_z = np.zeros(grid_x.shape)
    grid_z.fill(max_value)
    
    '''
    grid_z = [max_z[0]] * len(grid_x.ravel())
    ravelled_x = grid_x.ravel()
    ravelled_y = grid_y.ravel()
    '''

    grid_indeces = dict()

    for i,(dx, dy) in enumerate(distances.keys()):
        ix = (dx - min_x) / ((max_x - min_x) / float(res.imag - 1))
        iy = (dy - min_y) / ((max_y - min_y) / float(res.imag - 1))

        if distances[(dx, dy)] == 88:
            print >>sys.stderr, "dx:", dx, "dy:", dy
            print >>sys.stderr, "ix, iy", ix, iy
        # the position is outside of the bounding box
        if ix < 0:
            continue
        if ix >= len(grid_x):
            continue

        if iy < 0:
            continue
        if iy >= len(grid_x):
            continue

        #source_x = grid_x[ix][iy]
        #source_y = grid_y[ix][iy]

        source_x = dx
        source_y = dy

        curr_distance = distances[(dx,dy)]
        swimming_speed = 100

        #print >>sys.stderr, "curr_distance:", curr_distance, dx, dy

        def calc_distance(grid, curr_pos):
            target_x = grid_x[curr_pos[0]][curr_pos[1]]
            target_y = grid_y[curr_pos[0]][curr_pos[1]]

            mx, my = my_map(target_x, target_y)
            speed = walking_speed

            if (mx,my) not in is_land:
                is_land[(mx, my)] = my_map.is_land(mx, my)

            if not is_land[(mx,my)]:
                speed = swimming_speed

            station_to_target = haversine(target_x, target_y, source_x, source_y)
                
            #time_needed = 5 * station_to_target + curr_distance
            #print >>sys.stderr, "position:", target_x, target_y, "curr_distance:", curr_distance, "grid:", time_needed, log(time_needed), "station_to_target:", station_to_target, "speed:", speed, mx, my

            if (speed * station_to_target + curr_distance) < grid[curr_pos[0]][curr_pos[1]]:
                grid[curr_pos[0]][curr_pos[1]] =  (speed * station_to_target + curr_distance)
                return True
            else:
                return False

        calc_distance(grid_z, (ix, iy))
            
        expand_grid(grid_z, (ix+1, iy+1), (1,1), calc_distance)
        expand_grid(grid_z, (ix+1, iy-1), (1,-1), calc_distance)
        expand_grid(grid_z, (ix-1, iy+1), (-1,1), calc_distance)
        expand_grid(grid_z, (ix-1, iy-1), (-1,-1), calc_distance)

        expand_grid(grid_z, (ix+1, iy), (1,0), calc_distance)
        expand_grid(grid_z, (ix-1, iy), (-1,0), calc_distance)
        expand_grid(grid_z, (ix, iy+1), (0,1), calc_distance)
        expand_grid(grid_z, (ix, iy-1), (0,-1), calc_distance)

        grid_indeces[(dx,dy)]  = (ix, iy)

        '''
        print '-------------'
        print ix, iy
        print dx, dy
        print grid_x[ix][iy]
        print grid_y[ix][iy]

        print (dx - grid_x[ix][iy]) ** 2 + (dy - grid_y[ix][iy]) ** 2
        '''

    return (grid_x, grid_y, grid_z, min_x, max_x, min_y, max_y)

def calc_speed_grid(grid_x, grid_y, grid_z, from_x, from_y):
    '''
    Calculate the speed from the start point (from_x, from_y)
    to every point on the grid.

    @param grid_x: The x grid of latitudes and longitudes
    @param grid_y: The y grid of latitutdes and longitudes
    @param grid_z: The z grid (travel points) of latitudes and longitudes
    @param from_x: The latitude of the start point
    @param from_y: The longitude of the start point
    '''
    rav_x, rav_y, rav_z = grid_x.ravel(), grid_y.ravel(), grid_z.ravel()

    def calc_speed((x,y,z)):
        new_tt = np.exp(z)
        dist = haversine(from_y, from_x, x, y)
        print >>sys.stderr, "x,y,z", x,y,z, dist, new_tt, (dist / new_tt)

        return new_tt / dist

    grid_s = map(calc_speed,
                 zip(rav_x, rav_y, rav_z))

    grid_s = np.array(grid_s).reshape(grid_z.shape)
    #print >>sys.stderr, zip(rav_x, rav_y, rav_z)
    #print >>sys.stderr, "grid_z", grid_z
    #print >>sys.stderr, "grid_s:", grid_s

    return  grid_s

def plot_plain_grid(grid_x,grid_y,grid_z,xs,ys,zs):
    min_x, max_x = min(xs)-3, max(xs)
    min_y, max_y = min(ys)-3, max(ys)
    
    fig = plt.figure(figsize=(80,80))
    from matplotlib.cm import get_cmap

    plt.imshow(-grid_z.T, extent= (min_x, max_x, min_y, max_y), 
               origin='lower', cmap=get_cmap('Blues'))

    fig, ax = plt.subplots(figsize = (40,40))

def plot_map_grid(grid_z,min_x,max_x,min_y,max_y, filename=None, showgrid=True, contour=False, cmap_name="Blues"):
    from mpl_toolkits.basemap import Basemap
    import matplotlib.pyplot as plt
    import numpy as np
    
    #fig, ax = plt.subplots(figsize=(20,6))
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_axes([0.0,0.0,1.0,1.0])

    # set up orthographic map projection with
    # perspective of satellite looking down at 50N, 100W.
    # use low resolution coastlines.
    my_map = Basemap(llcrnrlon=min_x,llcrnrlat=min_y,
                  urcrnrlon=max_x,urcrnrlat=max_y,\
                rsphere=(6378137.00,6356752.3142),\
                resolution='l',area_thresh=1000.,projection='merc',\
                lat_1=50.,lon_0=-107.,ax=ax)# draw coastlines, country boundaries, fill continents.
    my_map.drawcoastlines(linewidth=0.25)
    my_map.drawcountries(linewidth=0.25)
    #my_map.fillcontinents(color='white',lake_color='aqua')
    # draw the edge of the map projection region (the projection limb)
    my_map.drawmapboundary(fill_color='aqua')

    res = len(grid_z)
    x_vals = np.linspace(min_x, max_x, res)
    y_vals = np.linspace(min_y, max_y, res)

    grid_x, grid_y = np.mgrid[min_x:max_x:complex(0, res), min_y:max_y:complex(0, res)]
    
    #print "grid_x:", grid_x
    topodat = my_map.transform_scalar(-grid_z.T,x_vals,y_vals,
                                      res, res)

    max_z = max([max(x) for x in topodat])
    min_z = min([min(x) for x in topodat])
    print >>sys.stderr, "min_z:", min_z, "max_z:", max_z

    from matplotlib.cm import get_cmap
    from numpy import exp

    '''
    im = my_map.imshow(topodat, extent= (min_x, max_x, min_y, max_y), 
               origin='lower', cmap=get_cmap(cmap_name))
    import matplotlib
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    '''
    levels = [-(i * 60) for i in range(2, 33, 2)]
    print >>sys.stderr, "levels:", levels

    if contour:
        import matplotlib.ticker as ticker
        def tick_formatter(x, pos):
            return "{:.1f}".format(exp(-x) / 60)
        cont = my_map.contourf(grid_x, grid_y, -grid_z, levels, cmap=get_cmap(cmap_name), latlon=True)
        plt.clabel(cont, fmt=ticker.FuncFormatter(tick_formatter))

    my_map.drawlsmask(land_color=(0,0,0,0), ocean_color='w')

    """
    cb = my_map.colorbar(im,location='bottom',pad="2%", size="5%", format=ticker.FuncFormatter(tick_formatter))

    cb.update_ticks()
    cb.ax.set_position((0, 0.90, 0.5, 0.05))
    """

    #plt.title('Travel time from Vienna')
    ax.axis('off')
    if filename is not None:
        plt.savefig(filename, dpi=900, bbox_inches='tight', pad_inches=0)

    if showgrid:
        plt.show()

    #return cont

def plot_distances(connections_filename, res=4j):
    import os.path as op
    import os
    
    output_dir = op.splitext(op.basename(connections_filename))[0]
    print output_dir
    if not op.exists(output_dir):
        os.makedirs(output_dir)
    
    print "getting coordinates and times..."
    (distances, xs,ys,zs) = get_connection_coordinates_and_times(connections_filename)
    print "creating the grid..."
    (grid_x, grid_y, grid_z) = create_grid(distances, xs, ys, zs, res)
    print "plotting plain..."
    #plot_plain_grid(grid_x, grid_y, grid_z, xs, ys, zs)
    print "plotting map..."
    
    min_x, max_x = min(xs)-3, max(xs)
    min_y, max_y = min(ys)-3, max(ys)
    plot_map_grid(grid_z, min_x, max_x, min_y, max_y,
                  filename = op.join(output_dir, 'map.png'))
    
    with open(op.join(output_dir, 'grid_data.json'), 'w') as f:
        json.dump({'grid_z':[list(g) for g in grid_z], 'min_x':min(xs), 
                   'max_x':max(xs), 'min_y': min(ys), 'max_y':max(ys)}, f)
    
def fix_grid(grid):
    sorted_vals = sorted(np.array(grid).ravel())
    max_val = min(sorted_vals[len(sorted_vals)/20:])
    new_grid = [[max_val if x < max_val else x for x in g] for g in grid]
    return new_grid
        
#!/usr/bin/python

import sys
from optparse import OptionParser

def main():
    usage = """
    python plot_travel_times.py grid_filename.json

    Plot the travel times grid.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    output_filename = op.splitext(args[0])[0] + ".png"
    print >>sys.stderr, "output_filename:", output_filename

    import json
    import numpy as np
    with open(args[0], 'r') as f:
        print >>sys.stderr, "loading grid"
        grid = json.load(f)
        print >>sys.stderr, "loaded grid"
        
        plot_map_grid(np.array(fix_grid(grid['grid_z'])),
                                   grid['min_x'], grid['max_x'], grid['min_y'], grid['max_y'],
                                   filename=output_filename, showgrid=False)
        print >>sys.stderr, "plotted grid"

if __name__ == '__main__':
    main()

