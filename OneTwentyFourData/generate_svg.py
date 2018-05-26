import fiona
import shapely.affinity
import shapely.geometry
import shapely.ops
import shapely.geometry.polygon
import svgwrite

with fiona.open('data/2018/districts/districts.shp') as ridings_2018:
    geos = list()
    for riding in ridings_2018:
        transformed = shapely.geometry.shape(riding['geometry'])
        #scale down
        transformed = shapely.affinity.scale(transformed, 0.001, -0.001, origin=(0, 0, 0))
        geos.append(transformed)
    union = shapely.ops.cascaded_union(geos)
    dwg = svgwrite.Drawing('ridings_map.svg', style='fill: blue; stroke: black; stroke-width: 0.5px')
    for riding, geo in zip(ridings_2018, geos):
        geo = shapely.affinity.translate(geo, -union.bounds[0], -union.bounds[1])
        poly = dwg.polygon(geo.exterior.coords, id='riding_' + str(riding['properties']['ED_ID']))
        dwg.add(poly)
    dwg.save()

